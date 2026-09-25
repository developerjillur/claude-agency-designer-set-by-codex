// A contact sheet with numbered, captioned cells, for picking stock media by eye (Apple frameworks only).
//
//     sheet SPEC.json
//
// SPEC: {"out": "sheet.png", "cols": 4, "cell_w": 480, "cell_h": 270,
//        "items": [{"file": "thumb.jpg", "label": "3", "caption": "video 1920x1080 12.4 s"}]}
//
// Each picture is fitted into its cell without cropping (a dark band shows what it does not fill), the label sits in
// a badge at the top left, and the caption runs under the cell. A picture that cannot be read leaves a marked cell.
import AppKit
import Foundation

struct Item: Decodable {
    let file: String
    let label: String
    let caption: String?
}

struct Spec: Decodable {
    let out: String
    let cols: Int
    let cell_w: Int
    let cell_h: Int
    let items: [Item]
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(2)
}

let args = CommandLine.arguments
guard args.count >= 2, let raw = FileManager.default.contents(atPath: args[1]) else {
    fail("usage: sheet SPEC.json")
}
guard let spec = try? JSONDecoder().decode(Spec.self, from: raw), !spec.items.isEmpty else {
    fail("the spec is not valid JSON with at least one item")
}

let pad = 10
let captionH = 34
let cols = max(1, min(spec.cols, spec.items.count))
let rows = (spec.items.count + cols - 1) / cols
let cw = max(64, spec.cell_w)
let ch = max(36, spec.cell_h)
let width = cols * cw + (cols + 1) * pad
let height = rows * (ch + captionH) + (rows + 1) * pad

guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height, bitsPerSample: 8,
                                 samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                                 bytesPerRow: 0, bitsPerPixel: 0),
      let context = NSGraphicsContext(bitmapImageRep: rep) else {
    fail("could not make the canvas")
}
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = context

// AppKit draws from the bottom left; every box below is given from the top left and flipped here
func box(_ x: Int, _ yTop: Int, _ w: Int, _ h: Int) -> NSRect {
    return NSRect(x: x, y: height - yTop - h, width: w, height: h)
}

NSColor(calibratedWhite: 0.96, alpha: 1).setFill()
NSRect(x: 0, y: 0, width: width, height: height).fill()

let labelFont = NSFont.boldSystemFont(ofSize: max(18, CGFloat(ch) / 9))
let captionFont = NSFont.systemFont(ofSize: 15)

for (i, item) in spec.items.enumerated() {
    let col = i % cols
    let row = i / cols
    let x = pad + col * (cw + pad)
    let y = pad + row * (ch + captionH + pad)
    let cell = box(x, y, cw, ch)
    NSColor(calibratedWhite: 0.13, alpha: 1).setFill()
    cell.fill()
    if let image = NSImage(contentsOfFile: item.file), image.size.width > 0, image.size.height > 0 {
        let scale = min(CGFloat(cw) / image.size.width, CGFloat(ch) / image.size.height)
        let w = image.size.width * scale
        let h = image.size.height * scale
        let fit = NSRect(x: cell.minX + (CGFloat(cw) - w) / 2, y: cell.minY + (CGFloat(ch) - h) / 2, width: w, height: h)
        image.draw(in: fit, from: .zero, operation: .sourceOver, fraction: 1.0)
    } else {
        let missing = NSAttributedString(string: "could not read the picture",
                                         attributes: [.font: captionFont, .foregroundColor: NSColor.white])
        missing.draw(at: NSPoint(x: cell.minX + 12, y: cell.midY))
    }
    // the label badge
    let label = NSAttributedString(string: item.label, attributes: [.font: labelFont, .foregroundColor: NSColor.white])
    let size = label.size()
    let badge = NSRect(x: cell.minX + 8, y: cell.maxY - 8 - size.height - 8, width: size.width + 20, height: size.height + 8)
    NSColor(calibratedRed: 0.85, green: 0.1, blue: 0.2, alpha: 0.92).setFill()
    NSBezierPath(roundedRect: badge, xRadius: 6, yRadius: 6).fill()
    label.draw(at: NSPoint(x: badge.minX + 10, y: badge.minY + 4))
    // the caption under the cell
    if let text = item.caption, !text.isEmpty {
        let style = NSMutableParagraphStyle()
        style.lineBreakMode = .byTruncatingTail
        let caption = NSAttributedString(string: text, attributes: [.font: captionFont,
                                                                    .foregroundColor: NSColor(calibratedWhite: 0.12, alpha: 1),
                                                                    .paragraphStyle: style])
        caption.draw(in: box(x + 2, y + ch + 6, cw - 4, captionH - 6))
    }
}

NSGraphicsContext.restoreGraphicsState()
guard let png = rep.representation(using: .png, properties: [:]) else {
    fail("could not encode the PNG")
}
do {
    try png.write(to: URL(fileURLWithPath: spec.out))
} catch {
    fail("could not write \(spec.out): \(error)")
}
print(spec.out)
