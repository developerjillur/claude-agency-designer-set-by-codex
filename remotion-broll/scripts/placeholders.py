"""python3 placeholders.py PUBLIC_DIR : the two stand-in pictures the scenes load (presenter-pip.png, creator-cutout.png).

Plain flat shapes, no person and no text, so the kit renders before a project has its own pictures. Replace them with
the presenter's real footage still or cutouts made from references/asset-briefs.json (codex-imagegen batch)."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

INK, SKIN, HAIR = (43, 29, 22, 255), (233, 180, 138, 255), (58, 40, 30, 255)
SIZE = 1254


def presenter(path: Path) -> None:
    im = Image.new("RGB", (SIZE, SIZE), (246, 222, 196))
    d = ImageDraw.Draw(im)
    for i in range(SIZE):  # a soft warm backdrop, lighter at the top
        c = int(246 - 22 * i / SIZE)
        d.line([(0, i), (SIZE, i)], fill=(c, int(222 - 26 * i / SIZE), int(196 - 30 * i / SIZE)))
    d.ellipse([227, 820, 1027, 1500], fill=(38, 64, 102))          # shoulders in a navy top
    d.rounded_rectangle([547, 690, 707, 880], 40, fill=SKIN)       # neck
    d.ellipse([417, 250, 837, 740], fill=SKIN)                      # head
    d.pieslice([397, 210, 857, 620], 180, 360, fill=HAIR)           # hair
    for x in (540, 714):                                            # eyes
        d.ellipse([x - 18, 470, x + 18, 506], fill=INK)
    d.arc([557, 540, 697, 640], 20, 160, fill=INK, width=10)        # a small smile
    im.save(path)


def creator(path: Path) -> None:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = 10
    d.rounded_rectangle([430, 760, 500, 1110], 30, fill=(31, 92, 99, 255), outline=INK, width=w)   # legs
    d.rounded_rectangle([530, 760, 600, 1110], 30, fill=(31, 92, 99, 255), outline=INK, width=w)
    d.rounded_rectangle([400, 1090, 520, 1140], 20, fill=(255, 255, 255, 255), outline=INK, width=w)
    d.rounded_rectangle([510, 1090, 630, 1140], 20, fill=(255, 255, 255, 255), outline=INK, width=w)
    d.rounded_rectangle([390, 470, 640, 800], 70, fill=(255, 196, 61, 255), outline=INK, width=w)  # t-shirt
    d.ellipse([405, 200, 625, 450], fill=SKIN, outline=INK, width=w)                               # head
    d.pieslice([395, 180, 635, 380], 180, 360, fill=HAIR, outline=INK, width=w)
    d.ellipse([560, 300, 584, 324], fill=INK)                                                      # eye, three-quarter
    d.line([(620, 560), (760, 600)], fill=INK, width=34)                                           # arm to the handle
    d.line([(620, 560), (760, 600)], fill=SKIN, width=20)
    d.line([(760, 640), (700, 1140)], fill=(120, 120, 120, 255), width=16)                         # tripod
    d.line([(800, 640), (800, 1140)], fill=(120, 120, 120, 255), width=16)
    d.line([(840, 640), (900, 1140)], fill=(120, 120, 120, 255), width=16)
    d.rounded_rectangle([730, 520, 900, 650], 22, fill=(30, 30, 34, 255), outline=INK, width=w)   # camera body
    d.ellipse([880, 540, 980, 630], fill=(55, 55, 60, 255), outline=INK, width=w)                 # lens, frame-right
    im.save(path)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
    out.mkdir(parents=True, exist_ok=True)
    presenter(out / "presenter-pip.png")
    creator(out / "creator-cutout.png")
    print(f"wrote {out / 'presenter-pip.png'} and {out / 'creator-cutout.png'}")
