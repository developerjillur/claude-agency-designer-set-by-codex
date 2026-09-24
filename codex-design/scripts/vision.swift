// codex-design vision helper (macOS, Apple Vision; compiled once by design.py into the cache).
//   cd-vision analyze <image>          -> JSON: size, faces, attention and objectness saliency boxes (top-left px)
//   cd-vision cutout <image> <out.png> -> the foreground subject(s) on transparency (macOS 14+)
//   cd-vision ocr <image> [--langs en-US,fr-FR] [--correct] -> JSON: text lines and words with boxes (top-left px)
//   cd-vision ocr-langs <any-image>    -> JSON: the recognition languages this macOS supports
import CoreImage
import Foundation
import ImageIO
import UniformTypeIdentifiers
import Vision

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

// The image as it is meant to be seen: EXIF orientation applied (phone photos are often stored sideways), so the
// boxes match what Pillow (exif_transpose) and Chrome (image-orientation: from-image) show.
func load(_ path: String) -> CGImage {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let src = CGImageSourceCreateWithURL(url, nil) else { fail("cannot read image: \(path)") }
    let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any] ?? [:]
    let side = max(props[kCGImagePropertyPixelWidth] as? Int ?? 0, props[kCGImagePropertyPixelHeight] as? Int ?? 0)
    let opts: [CFString: Any] = [kCGImageSourceCreateThumbnailFromImageAlways: true,
                                 kCGImageSourceCreateThumbnailWithTransform: true,
                                 kCGImageSourceShouldCacheImmediately: true,
                                 kCGImageSourceThumbnailMaxPixelSize: max(side, 1)]
    guard let img = CGImageSourceCreateThumbnailAtIndex(src, 0, opts as CFDictionary) ?? CGImageSourceCreateImageAtIndex(src, 0, nil)
    else { fail("cannot read image: \(path)") }
    return img
}

// Vision boxes are normalised with the origin at the bottom left; return top-left pixel boxes
func px(_ r: CGRect, _ w: Int, _ h: Int) -> [Double] {
    let W = Double(w), H = Double(h)
    return [Double(r.minX) * W, (1 - Double(r.maxY)) * H, Double(r.width) * W, Double(r.height) * H].map { ($0 * 10).rounded() / 10 }
}

func emit(_ obj: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: obj, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

let args = CommandLine.arguments
guard args.count >= 3 else { fail("usage: cd-vision analyze <image> | cutout <image> <out.png>") }
let cg = load(args[2])
let handler = VNImageRequestHandler(cgImage: cg, options: [:])

switch args[1] {
case "analyze":
    let faces = VNDetectFaceRectanglesRequest()
    let attention = VNGenerateAttentionBasedSaliencyImageRequest()
    let objectness = VNGenerateObjectnessBasedSaliencyImageRequest()
    do { try handler.perform([faces, attention, objectness]) } catch { fail("vision failed: \(error)") }
    let f = (faces.results ?? []).map { ["box": px($0.boundingBox, cg.width, cg.height), "confidence": Double($0.confidence)] as [String: Any] }
    let a = ((attention.results?.first)?.salientObjects ?? []).map { ["box": px($0.boundingBox, cg.width, cg.height), "confidence": Double($0.confidence)] as [String: Any] }
    let o = ((objectness.results?.first)?.salientObjects ?? []).map { ["box": px($0.boundingBox, cg.width, cg.height), "confidence": Double($0.confidence)] as [String: Any] }
    emit(["width": cg.width, "height": cg.height, "faces": f, "attention": a, "objects": o])
case "cutout":
    guard args.count >= 4 else { fail("usage: cd-vision cutout <image> <out.png>") }
    if #available(macOS 14.0, *) {
        let req = VNGenerateForegroundInstanceMaskRequest()
        do { try handler.perform([req]) } catch { fail("vision failed: \(error)") }
        guard let obs = req.results?.first else { fail("no foreground subject found") }
        do {
            let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: false)
            let ci = CIImage(cvPixelBuffer: buf)
            let ctx = CIContext()
            let out = URL(fileURLWithPath: args[3])
            try ctx.writePNGRepresentation(of: ci, to: out, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
            emit(["cutout": args[3], "instances": obs.allInstances.count, "width": cg.width, "height": cg.height])
        } catch { fail("mask failed: \(error)") }
    } else {
        fail("subject cutout needs macOS 14 or later")
    }
case "ocr":
    // raw recognition (no language correction by default): a misspelt word must stay misspelt so it can be caught
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = args.contains("--correct")
    req.minimumTextHeight = 0.006
    if let i = args.firstIndex(of: "--langs"), i + 1 < args.count {
        req.recognitionLanguages = args[i + 1].split(separator: ",").map(String.init)
    } else if #available(macOS 13.0, *) {
        req.automaticallyDetectsLanguage = true
    }
    // a second, language-corrected pass supplies alternative readings only ("alts"): when the raw reading is wrong
    // but a corrected one spells the approved word, the glyph was probably misread and a second reader decides
    let alt = VNRecognizeTextRequest()
    alt.recognitionLevel = .accurate
    alt.usesLanguageCorrection = true
    alt.minimumTextHeight = req.minimumTextHeight
    alt.recognitionLanguages = req.recognitionLanguages
    if #available(macOS 13.0, *) { alt.automaticallyDetectsLanguage = req.automaticallyDetectsLanguage }
    do { try handler.perform([req, alt]) } catch { fail("vision failed: \(error)") }
    func iou(_ a: CGRect, _ b: CGRect) -> CGFloat {
        let i = a.intersection(b)
        if i.isNull { return 0 }
        let u = a.width * a.height + b.width * b.height - i.width * i.height
        return u > 0 ? i.width * i.height / u : 0
    }
    let altObs = alt.results ?? []
    var lines: [[String: Any]] = []
    for obs in req.results ?? [] {
        let cands = obs.topCandidates(3)
        guard let cand = cands.first else { continue }
        var alts: [String] = []
        for s in cands.dropFirst().map({ $0.string }) where s != cand.string && !alts.contains(s) { alts.append(s) }
        if let twin = altObs.max(by: { iou($0.boundingBox, obs.boundingBox) < iou($1.boundingBox, obs.boundingBox) }),
           iou(twin.boundingBox, obs.boundingBox) > 0.5 {
            for s in twin.topCandidates(3).map({ $0.string }) where s != cand.string && !alts.contains(s) { alts.append(s) }
        }
        var words: [[String: Any]] = []
        let text = cand.string
        var start = text.startIndex
        while start < text.endIndex {
            while start < text.endIndex && text[start] == " " { start = text.index(after: start) }
            if start >= text.endIndex { break }
            var end = start
            while end < text.endIndex && text[end] != " " { end = text.index(after: end) }
            if let rect = try? cand.boundingBox(for: start..<end) {
                words.append(["text": String(text[start..<end]), "box": px(rect.boundingBox, cg.width, cg.height)])
            }
            start = end
        }
        lines.append(["text": text, "confidence": Double(cand.confidence), "box": px(obs.boundingBox, cg.width, cg.height),
                      "words": words, "alts": alts])
    }
    emit(["width": cg.width, "height": cg.height, "lines": lines, "language_correction": req.usesLanguageCorrection,
          "languages": req.recognitionLanguages])
case "ocr-langs":
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    emit(["languages": (try? req.supportedRecognitionLanguages()) ?? []])
default:
    fail("unknown command \(args[1])")
}
