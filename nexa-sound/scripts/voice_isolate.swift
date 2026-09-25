// voice-isolate: run Apple's voice isolation Audio Unit (AUSoundIsolation: type aufx, subtype vois, manufacturer
// appl, present since macOS 13) over a file, offline, through AVAudioEngine's manual rendering.
//
// usage: voice-isolate IN OUT.caf [mix 0-100] [--params]
//   IN      any file AVAudioFile reads (nexa-sound passes 48 kHz float WAV)
//   OUT     written in the input's processing format (float, same rate and channels); CAF is safest
//   mix     parameter address 0, "Wet/Dry Mix", 0 to 100 (default 100)
//   --params  print the unit's parameters and continue
//
// The unit is not documented by Apple for this use: treat it as optional and re-test it after macOS updates.
// It delays the audio by about 56.3 ms (measured on an M4 Max); nexa-sound pads the input and trims that delay.
// Build: swiftc -O voice_isolate.swift -o voice-isolate   (sound.py clean --isolate does this once by itself)
import AVFoundation
import AudioToolbox
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 3 else { fail("usage: voice-isolate IN OUT.caf [mix 0-100] [--params]") }
let mixArg = args.count > 3 && !args[3].hasPrefix("--") ? Float(args[3]) : nil
let mix = max(0, min(100, mixArg ?? 100))
let desc = AudioComponentDescription(componentType: kAudioUnitType_Effect,
                                     componentSubType: 0x766F6973,          // 'vois'
                                     componentManufacturer: kAudioUnitManufacturer_Apple,
                                     componentFlags: 0, componentFlagsMask: 0)
var lookup = desc
guard AudioComponentFindNext(nil, &lookup) != nil else {
    fail("this Mac has no voice isolation unit (aufx/vois/appl needs macOS 13 or newer)")
}

do {
    let input = try AVAudioFile(forReading: URL(fileURLWithPath: args[1]))
    let format = input.processingFormat
    let engine = AVAudioEngine()
    let player = AVAudioPlayerNode()
    let fx = AVAudioUnitEffect(audioComponentDescription: desc)
    engine.attach(player)
    engine.attach(fx)
    engine.connect(player, to: fx, format: format)
    engine.connect(fx, to: engine.mainMixerNode, format: format)
    if let tree = fx.auAudioUnit.parameterTree {
        for p in tree.allParameters {
            if args.contains("--params") {
                print("param", p.address, p.identifier, p.displayName, p.minValue, p.maxValue, p.value)
            }
            if p.address == 0 { p.value = mix }          // wet/dry mix, 0 to 100
        }
    }
    try engine.enableManualRenderingMode(.offline, format: format, maximumFrameCount: 4096)
    try engine.start()
    player.scheduleFile(input, at: nil)
    player.play()
    let out = try AVAudioFile(forWriting: URL(fileURLWithPath: args[2]), settings: format.settings)
    guard let buffer = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat,
                                        frameCapacity: engine.manualRenderingMaximumFrameCount) else {
        fail("could not make a render buffer")
    }
    let started = Date()
    var stalls = 0
    while engine.manualRenderingSampleTime < input.length {
        let left = AVAudioFrameCount(input.length - engine.manualRenderingSampleTime)
        let frames = min(buffer.frameCapacity, left)
        let status = try engine.renderOffline(frames, to: buffer)
        switch status {
        case .success:
            try out.write(from: buffer)
            stalls = 0
        case .error:
            fail("the render failed")
        default:
            stalls += 1
            if stalls > 100 { fail("the render stalled") }
        }
    }
    player.stop()
    engine.stop()
    print("rendered \(input.length) frames in \(String(format: "%.2f", Date().timeIntervalSince(started))) s")
} catch {
    fail("voice isolation failed: \(error)")
}
