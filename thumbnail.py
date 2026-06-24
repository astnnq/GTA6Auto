# -*- coding: utf-8 -*-
"""Simple thumbnail generator using Pillow."""

import os
import re
import textwrap
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from config import THUMBNAILS_DIR, ensure_directories


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:70] or "thumbnail"


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def generate_thumbnail(topic):
    ensure_directories()
    title = topic.get("title", "GTA 6 Update") if isinstance(topic, dict) else str(topic)
    slug = _slug(title)
    output_path = os.path.join(THUMBNAILS_DIR, f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slug}.jpg")

    img = Image.new("RGB", (1280, 720), "#101014")
    draw = ImageDraw.Draw(img)

    # Bold blocks give readable thumbnails without needing copyrighted imagery.
    draw.rectangle((0, 0, 1280, 120), fill="#e31b23")
    draw.rectangle((0, 610, 1280, 720), fill="#f4c542")
    draw.rectangle((48, 160, 1232, 560), outline="#ffffff", width=6)

    draw.text((54, 30), "GTA 6", font=_font(68, bold=True), fill="#ffffff")
    draw.text((54, 632), "NEWS  |  GUIDES  |  BREAKDOWNS", font=_font(42, bold=True), fill="#101014")

    wrapped = textwrap.wrap(title.upper(), width=24)[:3]
    y = 205
    for line in wrapped:
        draw.text((82, y), line, font=_font(62, bold=True), fill="#ffffff")
        y += 78

    img.save(output_path, "JPEG", quality=92)
    print(f"[Thumbnail] Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_thumbnail("Everything officially known about the GTA 6 map so far")
