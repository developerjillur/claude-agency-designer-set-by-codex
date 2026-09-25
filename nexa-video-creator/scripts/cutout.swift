// Cut a subject out of a photo and style it for a Vox-style collage (Apple frameworks only, nothing downloaded).
//
//     cutout IN OUT [--style auto|color|bw|halftone] [--stroke auto|HEX|none] [--stroke-width PX] [--offset DX,DY]
//            [--shadow soft|none] [--dot PX] [--contrast X] [--max PX] [--no-lift]
//
// The subject is lifted with Vision's foreground-instance mask (macOS 14 or newer) and cropped to it; a picture that
// already has transparency is used as it is (--no-lift forces that). Styles: colour kept (buildings, objects), black
// and white, or black and white with a halftone dot texture (people, like newsprint). "auto" looks for people with
// Vision's human detector: a person becomes halftone with the marker stroke, anything else stays in colour. The
// marker stroke is the subject's silhouette grown and moved up and to the left, in a flat colour behind it; its width
// and offset scale with the subject (1.4 % and 2 % of its longer side) unless given in pixels. A soft shadow is baked
// in under everything, so the renderer draws a plain picture (a CSS shadow on every frame is slow). The PNG keeps its
// transparency and is padded so nothing is clipped. One JSON line goes to stdout.
import AppKit
import CoreImage
import CoreImage.CIFilterBuiltins
import Foundation
import Vision

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(2)
}

var args = Array(CommandLine.arguments.dropFirst())
guard args.count >= 2 else {
    fail("usage: cutout IN OUT [--style auto|color|bw|halftone] [--stroke auto|HEX|none] [--stroke-width PX] "
        + "[--offset DX,DY] [--shadow soft|none] [--dot PX] [--contrast X] [--max PX] [--no-lift]")
}
let inPath = args.removeFirst()
let outPath = args.removeFirst()
var style = "auto"
var strokeHex = "auto"
var strokeWidthArg: Double? = nil
var offsetArg: CGPoint? = nil       // screen x, y (y down), in px
var shadow = "soft"
var dot: Double = 0                 // 0: from the subject's size
var contrast: Double = 1.2
var maxSide: Double = 2000
var lift = true
var i = 0
while i < args.count {
    let a = args[i]
    func value() -> String {
        guard i + 1 < args.count else { fail("\(a) needs a value") }
        i += 1
        return args[i]
    }
    switch a {
    case "--style": style = value()
    case "--stroke": strokeHex = value()
    case "--stroke-width": strokeWidthArg = Double(value())
    case "--offset":
        let p = value().split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
        if p.count == 2 { offsetArg = CGPoint(x: p[0], y: p[1]) }
    case "--shadow": shadow = value()
    case "--dot": dot = Double(value()) ?? dot
    case "--contrast": contrast = Double(value()) ?? contrast
    case "--max": maxSide = Double(value()) ?? maxSide
    case "--no-lift": lift = false
    default: fail("unknown option \(a)")
    }
    i += 1
}
guard ["auto", "color", "bw", "halftone"].contains(style) else { fail("--style is auto, color, bw or halftone") }
guard ["soft", "none"].contains(shadow) else { fail("--shadow is soft or none") }

guard let source = CIImage(contentsOf: URL(fileURLWithPath: inPath), options: [.applyOrientationProperty: true]) else {
    fail("cannot read \(inPath)")
}
let context = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.sRGB)!])

// Does the picture already have transparent pixels? Then it is a cutout already.
func hasTransparency(_ image: CIImage) -> Bool {
    let small = image.transformed(by: CGAffineTransform(scaleX: min(1, 256 / max(1, image.extent.width)),
                                                        y: min(1, 256 / max(1, image.extent.height))))
    let minAlpha = CIFilter.areaMinimum()
    minAlpha.inputImage = small
    minAlpha.extent = small.extent
    guard let out = minAlpha.outputImage else { return false }
    var px = [UInt8](repeating: 255, count: 4)
    context.render(out, toBitmap: &px, rowBytes: 4, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBA8,
                   colorSpace: nil)
    return px[3] < 250
}

// People in the picture (bodies, not identities): Vision's human rectangles.
func peopleIn(_ image: CIImage) -> Int {
    let request = VNDetectHumanRectanglesRequest()
    let handler = VNImageRequestHandler(ciImage: image, options: [:])
    guard (try? handler.perform([request])) != nil else { return 0 }
    return (request.results ?? []).filter { $0.confidence > 0.5 }.count
}

var subject = source
var lifted = false
if lift && !hasTransparency(source) {
    if #available(macOS 14.0, *) {
        let request = VNGenerateForegroundInstanceMaskRequest()
        let handler = VNImageRequestHandler(ciImage: source, options: [:])
        do {
            try handler.perform([request])
        } catch {
            fail("Vision could not look at the picture: \(error.localizedDescription)")
        }
        guard let result = request.results?.first, !result.allInstances.isEmpty else {
            fail("no subject found in the picture: use a photo with a clear subject, or pass a cutout with --no-lift")
        }
        do {
            let buffer = try result.generateMaskedImage(ofInstances: result.allInstances, from: handler,
                                                        croppedToInstancesExtent: true)
            subject = CIImage(cvPixelBuffer: buffer)
            lifted = true
        } catch {
            fail("Vision could not cut the subject out: \(error.localizedDescription)")
        }
    } else {
        fail("cutting out needs macOS 14 or newer; pass a picture with transparency and --no-lift")
    }
}
subject = subject.transformed(by: CGAffineTransform(translationX: -subject.extent.minX, y: -subject.extent.minY))
// big pictures slow every frame of the render: keep the longer side at most --max px
let longer = max(subject.extent.width, subject.extent.height)
if longer > maxSide {
    let k = maxSide / longer
    let scale = CIFilter.lanczosScaleTransform()
    scale.inputImage = subject
    scale.scale = Float(k)
    scale.aspectRatio = 1
    subject = scale.outputImage!
    subject = subject.transformed(by: CGAffineTransform(translationX: -subject.extent.minX, y: -subject.extent.minY))
}
let extent = CGRect(x: 0, y: 0, width: subject.extent.width.rounded(.down), height: subject.extent.height.rounded(.down))
subject = subject.cropped(to: extent)
let side = max(extent.width, extent.height)

let people = style == "auto" || strokeHex == "auto" ? peopleIn(source) : 0
if style == "auto" { style = people > 0 ? "halftone" : "color" }
if strokeHex == "auto" { strokeHex = style == "halftone" ? "#E04329" : "none" }
let strokeWidth = strokeWidthArg ?? max(4, (side * 0.014).rounded())
// Core Image's y points up: the offset is given (and defaults) as screen x, y with y down
let screenOffset = offsetArg ?? CGPoint(x: -(side * 0.020).rounded(), y: -(side * 0.015).rounded())
let offset = CGPoint(x: screenOffset.x, y: -screenOffset.y)
if dot <= 0 { dot = max(3, (side * 0.0045).rounded()) }

// The subject's alpha as a mask (white where the subject is).
let alphaMask: CIImage = {
    let m = CIFilter.colorMatrix()
    m.inputImage = subject
    m.rVector = CIVector(x: 0, y: 0, z: 0, w: 1)
    m.gVector = CIVector(x: 0, y: 0, z: 0, w: 1)
    m.bVector = CIVector(x: 0, y: 0, z: 0, w: 1)
    m.aVector = CIVector(x: 0, y: 0, z: 0, w: 1)
    return m.outputImage!.cropped(to: extent)
}()

func grey(_ image: CIImage) -> CIImage {
    let c = CIFilter.colorControls()
    c.inputImage = image
    c.saturation = 0
    c.contrast = Float(contrast)
    c.brightness = 0.02
    return c.outputImage!.cropped(to: extent)
}

var styled = subject
if style == "bw" {
    styled = grey(subject)
} else if style == "halftone" {
    // newsprint: the grey picture with a dot screen laid over it (the dots carry the texture, the grey keeps the face)
    let g = grey(subject)
    let dots = CIFilter.dotScreen()
    dots.inputImage = g
    dots.center = CGPoint(x: extent.midX, y: extent.midY)
    dots.angle = Float.pi / 4
    dots.width = Float(dot)
    dots.sharpness = 0.7
    let screen = dots.outputImage!.cropped(to: extent)
    let fade = CIFilter.colorMatrix()
    fade.inputImage = screen
    fade.aVector = CIVector(x: 0, y: 0, z: 0, w: 0.5)
    let over = CIFilter.multiplyBlendMode()
    over.inputImage = fade.outputImage!
    over.backgroundImage = g
    styled = over.outputImage!.cropped(to: extent)
}
if style != "color" {
    // back to the subject's own shape
    let keep = CIFilter.blendWithMask()
    keep.inputImage = styled
    keep.backgroundImage = CIImage(color: .clear).cropped(to: extent)
    keep.maskImage = alphaMask
    styled = keep.outputImage!.cropped(to: extent)
}

func color(_ hex: String) -> CIColor? {
    var s = hex.trimmingCharacters(in: .whitespaces)
    if s.hasPrefix("#") { s.removeFirst() }
    guard s.count == 6, let v = UInt32(s, radix: 16) else { return nil }
    return CIColor(red: CGFloat((v >> 16) & 255) / 255, green: CGFloat((v >> 8) & 255) / 255, blue: CGFloat(v & 255) / 255)
}

// Room for the stroke and the shadow on every side.
let shadowBlur = (shadow == "soft") ? max(3, (side * 0.012).rounded()) : 0
let shadowOffset = CGPoint(x: (side * 0.006).rounded(), y: -(side * 0.009).rounded())
var pad = 2.0
if strokeHex != "none" { pad = max(pad, strokeWidth + max(abs(offset.x), abs(offset.y)) + 4) }
if shadow == "soft" { pad = max(pad, shadowBlur * 3 + max(abs(shadowOffset.x), abs(shadowOffset.y)) + 4) }
pad = pad.rounded(.up)
let canvas = CGRect(x: 0, y: 0, width: extent.width + 2 * pad, height: extent.height + 2 * pad)
let place = CGAffineTransform(translationX: pad, y: pad)
let paddedMask = alphaMask.transformed(by: place).composited(over: CIImage(color: .black).cropped(to: canvas))
var composed = styled.transformed(by: place)

// the silhouette (as a mask) of what is drawn so far: the subject, and the stroke once there is one
var silhouette = paddedMask
if strokeHex != "none" {
    guard let c = color(strokeHex) else { fail("--stroke is a colour like #E04329, auto or none") }
    let grown = CIFilter.morphologyMaximum()
    grown.inputImage = paddedMask
    grown.radius = Float(strokeWidth)
    let shifted = grown.outputImage!.transformed(by: CGAffineTransform(translationX: offset.x, y: offset.y))
        .composited(over: CIImage(color: .black).cropped(to: canvas)).cropped(to: canvas)
    let fill = CIFilter.blendWithMask()
    fill.inputImage = CIImage(color: c).cropped(to: canvas)
    fill.backgroundImage = CIImage(color: .clear).cropped(to: canvas)
    fill.maskImage = shifted
    composed = composed.composited(over: fill.outputImage!.cropped(to: canvas)).cropped(to: canvas)
    let both = CIFilter.maximumCompositing()
    both.inputImage = shifted
    both.backgroundImage = paddedMask
    silhouette = both.outputImage!.cropped(to: canvas)
}
if shadow == "soft" {
    // a soft shadow down and to the right, so the cut-out sits a little above the paper
    let blur = CIFilter.gaussianBlur()
    blur.inputImage = silhouette.clampedToExtent()
    blur.radius = Float(shadowBlur)
    let soft = blur.outputImage!.cropped(to: canvas)
        .transformed(by: CGAffineTransform(translationX: shadowOffset.x, y: shadowOffset.y)).cropped(to: canvas)
    let tint = CIFilter.blendWithMask()
    tint.inputImage = CIImage(color: CIColor(red: 0.16, green: 0.11, blue: 0.07, alpha: 0.30)).cropped(to: canvas)
    tint.backgroundImage = CIImage(color: .clear).cropped(to: canvas)
    tint.maskImage = soft
    composed = composed.composited(over: tint.outputImage!.cropped(to: canvas)).cropped(to: canvas)
}

let url = URL(fileURLWithPath: outPath)
do {
    try context.writePNGRepresentation(of: composed, to: url, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
} catch {
    fail("cannot write \(outPath): \(error.localizedDescription)")
}
let json: [String: Any] = ["ok": true, "file": outPath, "width": Int(canvas.width), "height": Int(canvas.height),
                           "lifted": lifted, "style": style, "stroke": strokeHex, "people": people,
                           "shadow": shadow, "pad": Int(pad)]
let data = try! JSONSerialization.data(withJSONObject: json, options: [.sortedKeys])
print(String(data: data, encoding: .utf8)!)
