#!/usr/local/lib/hermes-agent/venv/bin/python3
"""Prepare compact, source-traceable site images from selected public social frames."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "research" / "frame-samples"
POSTERS = ROOT / "public" / "assets" / "social"
OUT = ROOT / "public" / "assets" / "stories"
OUT.mkdir(parents=True, exist_ok=True)

SELECTIONS = [
    ("hero-community", FRAMES / "hike-6-53.0s.jpg", "7586238790667193607", "Community hike group", "trim-black"),
    ("hike-friends", FRAMES / "hike-3-25.9s.jpg", "7586238790667193607", "Women connecting during a SheBelieves hike", None),
    ("riding-adventure", FRAMES / "riding-5-18.5s.jpg", "7569658548527959304", "A participant at a SheBelieves riding and archery camp", None),
    ("golf-workshop", FRAMES / "golf-4-13.0s.jpg", "7581172949768506632", "A participant practicing at a SheBelieves golf workshop", None),
    ("vision-board-circle", FRAMES / "vision-board-5-9.1s.jpg", "7588913148514585874", "Participants making vision boards together outdoors", None),
    ("give-back-team", FRAMES / "give-back-6-13.1s.jpg", "7552585302041169159", "The SheBelieves flood-relief support team", "trim-black"),
    ("climbing-courage", FRAMES / "climbing-4-24.1s.jpg", "7576460143953448210", "A participant trying rock climbing at a SheBelieves camp", "remove-top-overlay"),
    ("qawali-night", POSTERS / "qawali-7583844829843557640.jpg", "7583844829843557640", "A live performance at a SheBelieves Qawali night", None),
]


def trim_black(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    mask = Image.new("RGB", rgb.size, (4, 4, 4))
    diff = ImageChops.difference(rgb, mask).convert("L").point(lambda value: 255 if value > 14 else 0)
    box = diff.getbbox()
    return rgb.crop(box) if box else rgb


manifest = []
for slug, source, post_id, alt, operation in SELECTIONS:
    image = Image.open(source).convert("RGB")
    if operation == "trim-black":
        image = trim_black(image)
    elif operation == "remove-top-overlay":
        image = image.crop((0, int(image.height * 0.13), image.width, image.height))
    if image.width > 1400:
        image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
    destination = OUT / f"{slug}.webp"
    image.save(destination, "WEBP", quality=84, method=6)
    manifest.append(
        {
            "slug": slug,
            "asset": f"/assets/stories/{destination.name}",
            "source_url": f"https://www.tiktok.com/@shebelieves.pk/video/{post_id}",
            "alt": alt,
            "public_source": "@shebelieves.pk on TikTok",
            "dimensions": list(image.size),
        }
    )

logo = Image.open(ROOT / "public" / "assets" / "shebelieves-logo-reference.jpg").convert("RGB")
white = Image.new("RGB", logo.size, "white")
box = ImageChops.difference(logo, white).convert("L").point(lambda value: 255 if value > 12 else 0).getbbox()
if box:
    logo = logo.crop(box)
logo = ImageOps.expand(logo, border=20, fill="white")
logo.save(ROOT / "public" / "assets" / "shebelieves-logo.webp", "WEBP", quality=94, method=6)

(ROOT / "public" / "assets" / "story-source-manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
)
print(json.dumps({"prepared": len(manifest), "manifest": manifest}, ensure_ascii=False))
