// facetrack: sample a video at N fps and print face boxes as JSON (Apple Vision, runs on the Neural Engine/GPU).
// Build: swiftc -O facetrack.swift -o facetrack    Run: ./facetrack input.mp4 5 > faces.json
// Output boxes are normalized to the displayed (rotation-applied) frame, origin top-left.
import AVFoundation
import Foundation
import Vision

let args = CommandLine.arguments
guard args.count >= 2 else {
    FileHandle.standardError.write("usage: facetrack VIDEO [samplesPerSecond]\n".data(using: .utf8)!)
    exit(2)
}
let url = URL(fileURLWithPath: args[1])
let sps = args.count >= 3 ? (Double(args[2]) ?? 5) : 5
let asset = AVURLAsset(url: url)
let duration = CMTimeGetSeconds(asset.duration)
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true // honour rotation metadata
gen.requestedTimeToleranceBefore = .zero
gen.requestedTimeToleranceAfter = .zero
gen.maximumSize = CGSize(width: 960, height: 960) // detection does not need full resolution

var samples: [[String: Any]] = []
var t = 0.0
while t < duration {
    let time = CMTime(seconds: t, preferredTimescale: 600)
    if let cg = try? gen.copyCGImage(at: time, actualTime: nil) {
        let request = VNDetectFaceRectanglesRequest()
        let handler = VNImageRequestHandler(cgImage: cg, options: [:])
        try? handler.perform([request])
        let faces = (request.results ?? []).map { f -> [String: Double] in
            let b = f.boundingBox // normalized, origin bottom-left
            return ["x": b.minX, "y": 1 - b.maxY, "w": b.width, "h": b.height, "confidence": Double(f.confidence)]
        }
        samples.append(["t": (t * 1000).rounded() / 1000, "faces": faces])
    }
    t += 1.0 / sps
}
let out: [String: Any] = ["source": args[1], "samplesPerSecond": sps, "durationSec": duration, "samples": samples]
let data = try JSONSerialization.data(withJSONObject: out, options: [.prettyPrinted])
FileHandle.standardOutput.write(data)
