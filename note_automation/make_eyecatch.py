"""Generate a note.com eyecatch image (1280x670) from an article's title.

Renders the article title on a gradient background with Pillow. Runs fully
offline -- no image API needed, so Codex/local can generate every eyecatch
for free. For richer AI-generated illustrations, swap this out for an image
API call and keep the same CLI.

Usage:
    python make_eyecatch.py article.md [--out eyecatch.png]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 670
TOP_COLOR = (24, 34, 64)
BOTTOM_COLOR = (76, 58, 128)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (255, 196, 66)
MARGIN = 110

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/ヒラギノ角ゴ ProN W6.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise RuntimeError("No Japanese-capable font found; add your font path to FONT_CANDIDATES")


def extract_title(md_path: Path) -> str:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    # Japanese has no spaces, so wrap greedily by measured character width.
    lines, current = [], ""
    for ch in text:
        if draw.textlength(current + ch, font=font) <= max_width:
            current += ch
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def draw_gradient(image: Image.Image):
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(round(top + (bottom - top) * t) for top, bottom in zip(TOP_COLOR, BOTTOM_COLOR))
        draw.line([(0, y), (WIDTH, y)], fill=color)


def make_eyecatch(md_path, out_path) -> Path:
    md_path, out_path = Path(md_path), Path(out_path)
    title = extract_title(md_path)

    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw_gradient(image)
    draw = ImageDraw.Draw(image)

    max_text_width = WIDTH - MARGIN * 2
    font = None
    lines = []
    for size in (80, 72, 64, 56, 48):
        font = load_font(size)
        lines = wrap_text(title, font, max_text_width, draw)
        if len(lines) <= 4:
            break

    line_height = round(font.size * 1.45)
    block_height = line_height * len(lines)
    y = (HEIGHT - block_height) // 2

    draw.rectangle([MARGIN - 34, y + 6, MARGIN - 22, y + block_height - 14], fill=ACCENT_COLOR)
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=TEXT_COLOR)
        y += line_height

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("article", help="Path to article markdown (title taken from the '# ' heading)")
    parser.add_argument("--out", default="eyecatch.png")
    args = parser.parse_args()

    out_path = make_eyecatch(args.article, args.out)
    print(f"Eyecatch written to {out_path}")


if __name__ == "__main__":
    main()
