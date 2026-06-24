# -*- coding: utf-8 -*-
"""
GTA6 Pipeline - Auto Caption Burner
Uses OpenAI Whisper (local, free) to generate and burn subtitles.
Captions massively improve retention and watch time on both YouTube and Shorts.
"""

import subprocess
import os
import json
import shutil

WHISPER_MODEL = "tiny"  # tiny = fast on Pi, good enough for clean TTS audio


def transcribe_audio(audio_path):
    """
    Run Whisper on the voiceover to get a timed SRT file.
    Returns path to the SRT file.
    """
    if not shutil.which("whisper"):
        print("[Captions] Whisper is not installed - skipping auto captions.")
        return None

    print(f"[Captions] Transcribing audio with Whisper ({WHISPER_MODEL})...")
    
    # output goes same place as audio file
    output_dir = os.path.dirname(audio_path)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    cmd = [
        "whisper",
        audio_path,
        "--model", WHISPER_MODEL,
        "--output_dir", output_dir,
        "--output_format", "srt",
        "--language", "en"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    
    if os.path.exists(srt_path):
        print(f"[Captions] SRT generated: {srt_path}")
        return srt_path
    else:
        print(f"[Captions] Whisper failed: {result.stderr[:200]}")
        return None


def burn_captions_to_video(video_path, srt_path, output_path, style="youtube"):
    """
    Burn captions directly into video using FFmpeg.
    style: 'youtube' = bottom centre, white text with black outline
           'shorts'  = middle of screen, larger text for vertical
    """
    if not srt_path or not os.path.exists(srt_path):
        print("[Captions] No SRT file - skipping caption burn")
        # just copy the video as-is
        shutil.copy2(video_path, output_path)
        return output_path

    print(f"[Captions] Burning captions ({style} style)...")

    if style == "shorts":
        # Large, centered captions for vertical video
        subtitle_filter = (
            f"subtitles='{srt_path}':force_style='"
            "FontName=Arial,"
            "FontSize=18,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=3,"
            "Bold=1,"
            "Alignment=10,"   # centre middle
            "MarginV=400"
            "'"
        )
    else:
        # Standard YouTube captions at bottom
        subtitle_filter = (
            f"subtitles='{srt_path}':force_style='"
            "FontName=Arial,"
            "FontSize=14,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=2,"
            "Bold=1,"
            "Alignment=2,"   # bottom centre
            "MarginV=40"
            "'"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", subtitle_filter,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-preset", "fast",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(output_path):
        print(f"[Captions] Captioned video saved: {output_path}")
        return output_path
    else:
        print(f"[Captions] Caption burn failed: {result.stderr[:300]}")
        # fall back to uncaptioned
        shutil.copy2(video_path, output_path)
        return output_path


def add_captions_to_both(long_path, short_path, audio_path):
    """
    Full caption pipeline - transcribe once, burn to both videos.
    Called by the main orchestrator.
    Returns paths to captioned versions.
    """
    # transcribe once from audio (cleaner than transcribing from video)
    srt_path = transcribe_audio(audio_path)

    # burn to long form
    long_captioned = long_path.replace(".mp4", "_captioned.mp4")
    burn_captions_to_video(long_path, srt_path, long_captioned, style="youtube")

    # burn to short form
    short_captioned = short_path.replace(".mp4", "_captioned.mp4")
    burn_captions_to_video(short_path, srt_path, short_captioned, style="shorts")

    return long_captioned, short_captioned


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        srt = transcribe_audio(sys.argv[1])
        if srt:
            out = sys.argv[2].replace(".mp4", "_captioned.mp4")
            burn_captions_to_video(sys.argv[2], srt, out)
    else:
        print("Usage: python3 captions.py <audio.mp3> <video.mp4>")
