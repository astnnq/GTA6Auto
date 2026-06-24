# -*- coding: utf-8 -*-
"""Voiceover generation using free local orchestration with edge-tts."""

import asyncio
import os
import re
import shutil
import subprocess
import wave
from datetime import datetime

from config import AUDIO_DIR, DEFAULT_VOICE, ensure_directories


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "voiceover"


def _read_script(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        return f.read().strip()


async def _edge_tts_to_file(text, output_path):
    import edge_tts

    communicate = edge_tts.Communicate(text, DEFAULT_VOICE)
    await communicate.save(output_path)


def _fallback_silence(output_path, seconds=90):
    print("[Voice] edge-tts unavailable; creating silent placeholder audio.")
    if shutil.which("ffmpeg"):
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t", str(seconds),
            "-q:a", "9",
            "-acodec", "libmp3lame",
            output_path,
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        return output_path if os.path.exists(output_path) else None

    wav_path = output_path.replace(".mp3", ".wav")
    sample_rate = 44100
    frames = b"\x00\x00" * sample_rate * seconds
    with wave.open(wav_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(frames)
    return wav_path


def run(script_path):
    """Generate an MP3 voiceover for a script file."""
    ensure_directories()
    text = _read_script(script_path)
    base = os.path.splitext(os.path.basename(script_path))[0]
    output_path = os.path.join(AUDIO_DIR, f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(base)}.mp3")

    print(f"[Voice] Generating voiceover with {DEFAULT_VOICE}...")
    try:
        asyncio.run(_edge_tts_to_file(text, output_path))
    except Exception as exc:
        print(f"[Voice] edge-tts failed: {exc}")
        fallback = _fallback_silence(output_path)
        if not fallback:
            raise RuntimeError("Voiceover generation failed and ffmpeg fallback was unavailable")
        output_path = fallback

    print(f"[Voice] Audio saved: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 voiceover.py <script.txt>")
    else:
        run(sys.argv[1])
