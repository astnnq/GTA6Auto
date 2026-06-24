# -*- coding: utf-8 -*-
"""FFmpeg video assembly for long-form and short-form GTA 6 videos."""

import os
import re
import shutil
import subprocess
from datetime import datetime

from clips_manager import get_clips_by_tags, mark_clip_used
from config import OUTPUT_DIR, SHORT_MAX_SECONDS, ensure_directories


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:70] or "gta6-video"


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-500:])
        return False
    return True


def _duration(path, default=90):
    if not shutil.which("ffprobe"):
        return default
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return default
    try:
        return max(1, float(result.stdout.strip()))
    except ValueError:
        return default


def _build_from_clip(clip_path, audio_path, output_path, duration, vertical=False):
    scale_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        if vertical
        else "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    )
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", clip_path,
        "-i", audio_path,
        "-t", str(duration),
        "-vf", scale_filter,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]
    return _run(cmd)


def _build_color(audio_path, output_path, duration, vertical=False):
    size = "1080x1920" if vertical else "1920x1080"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x111111:s={size}:r=30",
        "-i", audio_path,
        "-t", str(duration),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]
    return _run(cmd)


def build_video(audio_path, topic):
    """Build long 16:9 and short 9:16 videos from one voiceover."""
    ensure_directories()
    if not shutil.which("ffmpeg"):
        print("[Assembler] ffmpeg is not installed or not on PATH.")
        return None
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    title = topic.get("title", "GTA 6 Update") if isinstance(topic, dict) else str(topic)
    slug = _slug(title)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    long_path = os.path.join(OUTPUT_DIR, f"{stamp}-{slug}-long.mp4")
    short_path = os.path.join(OUTPUT_DIR, f"{stamp}-{slug}-short.mp4")

    audio_duration = _duration(audio_path)
    short_duration = min(audio_duration, SHORT_MAX_SECONDS)
    clips = get_clips_by_tags(["official"]) or get_clips_by_tags()
    clip = clips[0] if clips else None

    if clip:
        print(f"[Assembler] Using clip: {clip}")
        long_ok = _build_from_clip(clip, audio_path, long_path, audio_duration, vertical=False)
        short_ok = _build_from_clip(clip, audio_path, short_path, short_duration, vertical=True)
        if long_ok or short_ok:
            mark_clip_used(clip)
    else:
        print("[Assembler] No clips found; using a simple placeholder background.")
        long_ok = _build_color(audio_path, long_path, audio_duration, vertical=False)
        short_ok = _build_color(audio_path, short_path, short_duration, vertical=True)

    if not long_ok or not short_ok:
        return None
    return long_path, short_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 assembler.py <audio.mp3> <topic>")
    else:
        print(build_video(sys.argv[1], sys.argv[2]))
