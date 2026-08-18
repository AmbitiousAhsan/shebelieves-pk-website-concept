#!/usr/local/lib/hermes-agent/venv/bin/python3
"""Download selected public posts and generate frame contact sheets for visual selection."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / "research" / "videos"
FRAMES = ROOT / "research" / "frame-samples"
VIDEOS.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

POSTS = {
    "hike": "7586238790667193607",
    "riding": "7569658548527959304",
    "golf": "7581172949768506632",
    "vision-board": "7588913148514585874",
    "give-back": "7552585302041169159",
    "qawali": "7583844829843557640",
    "climbing": "7576460143953448210",
}


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def has_video(path: Path) -> bool:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return "video" in result.stdout


def frame(path: Path, at: float, out: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{at:.2f}", "-i", str(path), "-frames:v", "1", "-q:v", "2", "-y", str(out)],
        check=True,
    )


all_tiles = []
for slug, post_id in POSTS.items():
    url = f"https://www.tiktok.com/@shebelieves.pk/video/{post_id}"
    result = subprocess.run(
        [
            "/root/.agent-reach/venv/bin/yt-dlp",
            "--quiet",
            "--no-playlist",
            "--format",
            "bestvideo[height<=720]/bestvideo/best[height<=720]/best",
            "--print",
            "after_move:filepath",
            "--output",
            str(VIDEOS / "%(id)s.%(ext)s"),
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    video = next((path for path in reversed(paths) if path.exists()), None)
    if video is None:
        raise RuntimeError(f"Downloader returned no video path for {post_id}: {result.stdout}")
    if not has_video(video):
        print(f"skipped {slug}: no video stream in {video.name}")
        continue
    total = duration(video)
    for index, fraction in enumerate((0.12, 0.28, 0.44, 0.60, 0.76, 0.90), 1):
        at = max(0.1, total * fraction)
        output = FRAMES / f"{slug}-{index}-{at:.1f}s.jpg"
        frame(video, at, output)
        image = Image.open(output).convert("RGB")
        tile = ImageOps.fit(image, (250, 360), method=Image.Resampling.LANCZOS)
        card = Image.new("RGB", (266, 400), "white")
        card.paste(tile, (8, 8))
        ImageDraw.Draw(card).text((10, 375), f"{slug} · {at:.1f}s", fill="#06184a")
        all_tiles.append(card)
    print(f"sampled {slug}: {total:.1f}s")

cols = 6
rows = (len(all_tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 266, rows * 400), "#f5f0ec")
for index, tile in enumerate(all_tiles):
    sheet.paste(tile, ((index % cols) * 266, (index // cols) * 400))
sheet.save(ROOT / "research" / "video-frame-contact-sheet.jpg", quality=90, optimize=True)
print(f"wrote {len(all_tiles)} frame samples")
