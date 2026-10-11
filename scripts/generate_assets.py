"""Render the banner and profile animation. Requires Pillow and macOS fonts.

Run from anywhere: python3 scripts/generate_assets.py
Each PNG is a reduced-motion fallback for its animated GIF.
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


def indexed_frame(image, palette):
    indexed = image.quantize(palette=palette, dither=Image.Dither.NONE)
    white_mask = image.convert("L").point(lambda value: 255 if value == 255 else 0)
    indexed.paste(223, mask=white_mask)
    return indexed


def profile_animation(palette):
    frames = []
    corners = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8)
             if sum(corners[a][axis] != corners[b][axis] for axis in range(3)) == 1]
    for frame in range(72):
        image = Image.new("RGB", (420, 420), PAPER)
        draw = ImageDraw.Draw(image)
        for x in range(66, 355, 24):
            for y in range(66, 355, 24):
                draw.ellipse((x, y, x + 1, y + 1), fill="#e2e5e9")
        theta = 2 * pi * frame / 72
        points = []
        for x, y, z in corners:
            rx, rz = x * cos(theta) + z * sin(theta), -x * sin(theta) + z * cos(theta)
            ry, depth = y * cos(0.45) - rz * sin(0.45), y * sin(0.45) + rz * cos(0.45)
            scale = 78 / (1 + depth * 0.12)
            points.append((210 + rx * scale, 193 + ry * scale, depth))
        for a, b in sorted(edges, key=lambda edge: points[edge[0]][2] + points[edge[1]][2], reverse=True):
            color = "#c3ccd9" if points[a][2] + points[b][2] > 0 else ACCENT
            draw.line(points[a][:2] + points[b][:2], fill=color, width=3)
        for x, y, depth in points:
            draw.ellipse((x - 4, y - 4, x + 4, y + 4),
                         fill=ACCENT if depth < 0 else "#b5bfce")
        text = "SYSTEMS IN MOTION"
        draw.text((210, 365), text, font=SMALL, fill=MUTED, anchor="mt")
        if frame == 0:
            image.save(ASSETS / "profile.png", optimize=True)
        frames.append(indexed_frame(image, palette))
    frames[0].save(ASSETS / "profile.gif", save_all=True,
                   append_images=frames[1:], duration=90, loop=0,
                   optimize=True, disposal=1)


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
        frames.append(indexed_frame(image, palette))
    frames[0].save(ASSETS / "header.gif", save_all=True,
                   append_images=frames[1:], duration=80, loop=0,
                   optimize=True, disposal=1)
    profile_animation(palette)
    print("Generated header and profile assets (PNG + GIF)")


if __name__ == "__main__":
    main()
