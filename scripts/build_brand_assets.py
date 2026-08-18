#!/usr/local/lib/hermes-agent/venv/bin/python3
"""Derive site brand assets from the supplied SheBelieves logo and public story frames.

Nothing here redraws or restyles the official logo: the transparent lockup and the
favicon wing are pixel crops of `public/assets/shebelieves-logo.webp` with the flat
white studio background converted to alpha.

Run: scripts/build_brand_assets.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public" / "assets"
BRAND = ASSETS / "brand"
STORIES = ASSETS / "stories"
FONT_CACHE = Path(__file__).resolve().parent / ".fontcache"

INK = (1, 18, 70)
MAGENTA = (193, 20, 88)
PAPER = (251, 246, 239)

FONT_SOURCES = {
    "fraunces.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf",
    "manrope.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf",
}
FONT_FALLBACKS = {
    "fraunces.ttf": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "manrope.ttf": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
}


def load_font(name: str, size: int, weight: float | None = None) -> ImageFont.FreeTypeFont:
    FONT_CACHE.mkdir(exist_ok=True)
    path = FONT_CACHE / name
    if not path.exists():
        try:
            urllib.request.urlopen(FONT_SOURCES[name], timeout=30)  # noqa: S310 - pinned Google Fonts source
            urllib.request.urlretrieve(FONT_SOURCES[name], path)  # noqa: S310
        except Exception:  # offline build machines fall back to a system serif/sans
            path = Path(FONT_FALLBACKS[name])
    font = ImageFont.truetype(str(path), size)
    if weight is not None:
        try:
            axes = [axis[2] for axis in font.get_variation_axes()]
            names = [axis[3] if len(axis) > 3 else b"" for axis in font.get_variation_axes()]
            values = []
            for default, axis_name in zip(axes, names):
                label = axis_name.decode() if isinstance(axis_name, bytes) else str(axis_name)
                values.append(weight if label.lower() in {"weight", "wght"} else default)
            font.set_variation_by_axes(values)
        except Exception:
            pass
    return font


def white_to_alpha(image: Image.Image) -> Image.Image:
    """Convert a flat-white background to transparency while keeping antialiased edges."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    out = Image.new("RGBA", (width, height))
    source = rgb.load()
    target = out.load()
    for y in range(height):
        for x in range(width):
            r, g, b = source[x, y]
            whiteness = min(r, g, b)
            alpha = 255 - whiteness
            if alpha <= 4:
                target[x, y] = (0, 0, 0, 0)
                continue
            scale = 255 / alpha
            target[x, y] = (
                max(0, min(255, int((r - whiteness) * scale))),
                max(0, min(255, int((g - whiteness) * scale))),
                max(0, min(255, int((b - whiteness) * scale))),
                alpha,
            )
    return out


def magenta_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    rgb = image.convert("RGB")
    mask = Image.new("L", rgb.size, 0)
    pixels = rgb.load()
    mask_pixels = mask.load()
    for y in range(rgb.height):
        for x in range(rgb.width // 3):  # the wing sits left of the wordmark
            r, g, b = pixels[x, y]
            if r > 110 and r - g > 45:
                mask_pixels[x, y] = 255
    box = mask.getbbox()
    if box is None:
        raise SystemExit("Could not locate the wing motif in the logo file.")
    return box


def rounded_square(size: int, radius_ratio: float, fill: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (0, 0, size * 4 - 1, size * 4 - 1),
        radius=int(size * 4 * radius_ratio),
        fill=fill + (255,),
    )
    return canvas.resize((size, size), Image.LANCZOS)


def isolate_wing(transparent: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """Keep only the magenta wing strokes so the wordmark's S never bleeds into the icon."""
    wing = transparent.crop(box)
    pixels = wing.load()
    for y in range(wing.height):
        for x in range(wing.width):
            r, g, b, a = pixels[x, y]
            if a and (r - g) < 40:
                pixels[x, y] = (0, 0, 0, 0)
    return wing.crop(wing.getbbox())


def fit(image: Image.Image, target: int) -> Image.Image:
    scale = target / max(image.width, image.height)
    return image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)


def build_logo_and_icons(logo: Image.Image) -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    transparent = white_to_alpha(logo)
    transparent.crop(transparent.getbbox()).save(BRAND / "shebelieves-logo.png")

    wing = isolate_wing(transparent, magenta_bbox(logo))
    wing.save(BRAND / "wing-mark.png")

    icons = ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"))
    for size, name in icons:
        icon = rounded_square(size, 0.22, PAPER)
        scaled = fit(wing, int(size * 0.72))
        icon.alpha_composite(scaled, ((size - scaled.width) // 2, (size - scaled.height) // 2))
        icon.convert("RGB").save(BRAND / name)

    ico = rounded_square(256, 0.22, PAPER)
    wing_small = fit(wing, 196)
    ico.alpha_composite(wing_small, ((256 - wing_small.width) // 2, (256 - wing_small.height) // 2))
    ico.save(ASSETS.parent / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_open_graph(logo: Image.Image) -> None:
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), PAPER)

    photo = Image.open(STORIES / "hero-community.webp").convert("RGB")
    panel_x = 690
    photo_width, photo_height = width - panel_x, height
    ratio = max(photo_width / photo.width, photo_height / photo.height)
    photo = photo.resize((int(photo.width * ratio), int(photo.height * ratio)), Image.LANCZOS)
    left = (photo.width - photo_width) // 2
    top = max(0, int(photo.height * 0.06))
    top = min(top, photo.height - photo_height)
    canvas.paste(photo.crop((left, top, left + photo_width, top + photo_height)), (panel_x, 0))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((panel_x - 6, 0, panel_x, height), fill=MAGENTA)

    lockup = white_to_alpha(logo)
    lockup = fit(lockup.crop(lockup.getbbox()), 230)
    canvas.paste(lockup, (72, 58), lockup)

    display = load_font("fraunces.ttf", 50, weight=680)
    body = load_font("manrope.ttf", 23, weight=500)
    label = load_font("manrope.ttf", 18, weight=600)

    margin, text_width = 72, panel_x - 144
    y = 218
    for line in wrap(draw, "Find your next brave thing — and your people.", display, text_width):
        draw.text((margin, y), line, font=display, fill=INK)
        y += 62

    y += 22
    for line in wrap(draw, "A women-only Twin Cities sisterhood for trying new things and finding your people.", body, text_width):
        draw.text((margin, y), line, font=body, fill=(46, 58, 92))
        y += 33

    draw.line((margin, height - 108, margin + 56, height - 108), fill=MAGENTA, width=4)
    draw.text((margin, height - 88), "Independent concept preview · Built from", font=label, fill=(84, 94, 124))
    draw.text((margin, height - 60), "public SheBelieves content", font=label, fill=(84, 94, 124))

    canvas.save(ASSETS / "og-cover.jpg", quality=88, optimize=True)


def reframe_climbing_story() -> None:
    """Re-crop the climbing frame so the TikTok reply overlay (a third-party username) is gone.

    Always derived from the original frame sample, so repeated runs are idempotent. Fresh
    clones do not ship `research/frame-samples/`, and there the committed crop is already final.
    """
    source = ROOT / "research" / "frame-samples" / "climbing-4-24.1s.jpg"
    if not source.exists():
        print(json.dumps({"skipped": "climbing-courage reframe", "reason": "frame sample not present"}))
        return
    frame = Image.open(source).convert("RGB")
    cropped = frame.crop((0, round(frame.height * 0.25), frame.width, frame.height))
    cropped.save(STORIES / "climbing-courage.webp", "WEBP", quality=86, method=6)

    manifest_path = ASSETS / "story-source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest:
        if entry["slug"] == "climbing-courage":
            entry["dimensions"] = list(cropped.size)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    logo = Image.open(ASSETS / "shebelieves-logo.webp")
    build_logo_and_icons(logo)
    build_open_graph(logo)
    reframe_climbing_story()
    print(json.dumps({"brand_assets": sorted(p.name for p in BRAND.iterdir())}))


if __name__ == "__main__":
    main()
