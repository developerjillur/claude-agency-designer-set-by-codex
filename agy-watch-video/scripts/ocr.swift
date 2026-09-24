// awv-ocr: Apple Vision text recognition for agy-watch-video.
// Usage: awv-ocr <image> [--langs en-US,fr-FR]
// Prints {"width", "height", "lines": [{"text", "confidence", "box": [x, y, w, h]}]} with pixel boxes, top-left origin.
// Vision reads Latin, Cyrillic, CJK, Arabic, Thai and more, but not Bengali: for Bengali the boxes still show where text is.
import AppKit
import Foundation
import Vision

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 2 else { fail("usage: awv-ocr <image> [--langs en-US,fr-FR]") }
guard let image = NSImage(contentsOfFile: args[1]),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fail("cannot read \(args[1])") }

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false  // keep real typos visible
request.minimumTextHeight = 0.008       // default 1/32 of the image misses small print
if let i = args.firstIndex(of: "--langs"), i + 1 < args.count {
    request.recognitionLanguages = args[i + 1].split(separator: ",").map(String.init)
} else if #available(macOS 13.0, *) {
    request.automaticallyDetectsLanguage = true
}

do {
    try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
} catch {
    fail("vision failed: \(error)")
}

let width = Double(cg.width), height = Double(cg.height)
var lines: [[String: Any]] = []
for observation in request.results ?? [] {
    guard let best = observation.topCandidates(1).first else { continue }
    let b = observation.boundingBox
    let x = Double(b.origin.x) * width
    let y = (1.0 - Double(b.origin.y) - Double(b.size.height)) * height
    lines.append([
        "text": best.string,
        "confidence": Double(best.confidence),
        "box": [x.rounded(), y.rounded(), (Double(b.size.width) * width).rounded(), (Double(b.size.height) * height).rounded()],
    ])
}
let out: [String: Any] = ["width": cg.width, "height": cg.height, "lines": lines]
FileHandle.standardOutput.write(try! JSONSerialization.data(withJSONObject: out, options: []))
