#!/root/.agent-reach/venv/bin/python
"""Collect public SheBelieves TikTok poster images for a non-commercial concept preview."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import yt_dlp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "assets" / "social"
OUT.mkdir(parents=True, exist_ok=True)

POSTS = {
    "hike": "7586238790667193607",
    "riding": "7569658548527959304",
    "golf": "7581172949768506632",
    "vision-board": "7588913148514585874",
    "give-back": "7552585302041169159",
    "qawali": "7583844829843557640",
    "climbing": "7576460143953448210",
    "riding-community": "7550024852212600071",
    "paint": "7539758114279607559",
    "field-day": "7525060536006888722",
}

manifest = []
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
}
opts = {
    "quiet": True,
    "skip_download": True,
    "noplaylist": True,
}
with yt_dlp.YoutubeDL(opts) as ydl:
    for slug, post_id in POSTS.items():
        page_url = f"https://www.tiktok.com/@shebelieves.pk/video/{post_id}"
        info = ydl.extract_info(page_url, download=False)
        candidates = [x for x in info.get("thumbnails", []) if x.get("url")]
        if not candidates:
            raise RuntimeError(f"No thumbnail for {post_id}")
        thumb = max(candidates, key=lambda x: (x.get("width") or 0) * (x.get("height") or 0))
        destination = OUT / f"{slug}-{post_id}.jpg"
        request = urllib.request.Request(thumb["url"], headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
        manifest.append(
            {
                "slug": slug,
                "post_id": post_id,
                "source_url": page_url,
                "description": info.get("description") or info.get("title") or "",
                "published_timestamp": info.get("timestamp"),
                "asset": f"/assets/social/{destination.name}",
                "asset_origin": "Public TikTok poster image",
            }
        )
        print(f"saved {destination.name}")

(ROOT / "public" / "assets" / "social-source-manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
)
print(f"wrote {len(manifest)} assets")
