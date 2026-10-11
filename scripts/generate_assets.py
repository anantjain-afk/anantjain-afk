"""Render the profile banner. Requires Pillow and macOS's Didot/Menlo fonts.

Run from anywhere: python3 scripts/generate_assets.py
The PNG is also the reduced-motion fallback for the animated GIF.
"""

from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1600, 480
INK = "#22252a"
MUTED = "#646b75"
ACCENT = "#486caa"
PAPER = "#ffffff"


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


SERIF = font("/System/Library/Fonts/Supplemental/Didot.ttc", 188)
MONO = font("/System/Library/Fonts/Menlo.ttc", 18)
SMALL = font("/System/Library/Fonts/Menlo.ttc", 16)


def tracked(draw, text, xy, fill=MUTED, spacing=3, face=MONO):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=face, fill=fill, anchor="lt")
        x += draw.textlength(char, font=face) + spacing


def orbit(theta):
    tilt = -pi / 5
    x, y = 122 * cos(theta), 55 * sin(theta)
    return (
        1320 + x * cos(tilt) - y * sin(tilt),
        231 + x * sin(tilt) + y * cos(tilt),
    )


def base_image():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    tracked(draw, "ANANTJAIN-AFK / ENGINEERING", (92, 45))
    tracked(draw, "SELECTED WORK", (1270, 46), spacing=2, face=SMALL)
    draw.line((92, 83, 1508, 83), fill="#e2e5e9", width=2)
    draw.text((87, 142), "Anant Jain.", font=SERIF, fill=INK, anchor="lt")
    tracked(draw, "BACKEND / AI / FULL STACK", (96, 337), spacing=4)
    draw.line((92, 408, 1508, 408), fill="#e2e5e9", width=2)
    tracked(draw, "INTELLIGENT SYSTEMS. THOUGHTFUL EXPERIENCES.", (94, 438),
            spacing=1.6, face=SMALL)
    tracked(draw, "01 / PROFILE", (1310, 438), spacing=1.5, face=SMALL)

    cx, cy, radius = 1320, 231, 105
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                 outline="#d9dfe7", width=2)
    draw.line([orbit(i * 2 * pi / 240) for i in range(241)],
              fill="#c3ccd9", width=2)
    for i in range(8):
        angle = i * pi / 4
        draw.line((cx + 115 * cos(angle), cy + 115 * sin(angle),
                   cx + 121 * cos(angle), cy + 121 * sin(angle)),
                  fill="#c3ccd9", width=2)
    draw.line((cx - 12, cy, cx + 12, cy), fill="#b5bfce", width=2)
    draw.line((cx, cy - 12, cx, cy + 12), fill="#b5bfce", width=2)
    draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=ACCENT)
    return image


def main():
    ASSETS.mkdir(exist_ok=True)
    base = base_image()
    # A fixed palette keeps stationary typography consistent across frames.
    colors = [(round(i * 255 / 223),) * 3 for i in range(224)] + [
        (round(72 + (255 - 72) * i / 31),
         round(108 + (255 - 108) * i / 31),
         round(170 + (255 - 170) * i / 31)) for i in range(32)
    ]
    palette = Image.new("P", (1, 1))
    palette.putpalette([channel for color in colors for channel in color])
    frames = []
    for frame in range(64):
        image = base.copy()
        draw = ImageDraw.Draw(image)
        theta = frame * 2 * pi / 64 - pi / 2
        trail = [orbit(theta - 0.6 + i * 0.6 / 30) for i in range(31)]
        draw.line(trail, fill="#92a9cd", width=3)
        x, y = orbit(theta)
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=PAPER)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=ACCENT)
        if frame == 0:
            image.save(ASSETS / "header.png", optimize=True)
        indexed = image.quantize(palette=palette, dither=Image.Dither.NONE)
        white_mask = image.convert("L").point(lambda value: 255 if value == 255 else 0)
        indexed.paste(223, mask=white_mask)
        frames.append(indexed)
    frames[0].save(ASSETS / "header.gif", save_all=True,
                   append_images=frames[1:], duration=80, loop=0,
                   optimize=True, disposal=1)
    print("Generated assets/header.png and assets/header.gif")


if __name__ == "__main__":
    main()
