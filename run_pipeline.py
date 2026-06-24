# -*- coding: utf-8 -*-
"""
GTA6 Pipeline - Master Orchestrator v2
Full pipeline: scrape -> script -> voice -> assemble -> caption -> upload -> log
Run this manually or via cron.
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Add pipeline dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import build_queue, mark_topic_used
from script_gen import generate_script
from voiceover import run as generate_voiceover
from assembler import build_video
from thumbnail import generate_thumbnail
from captions import add_captions_to_both
from youtube_upload import upload_to_youtube
from clips_manager import scan_clips_folder, get_library_summary
from logger import log_run, print_stats
from config import AUTO_UPLOAD, REVIEW_DIR, ensure_directories


def copy_to_review(paths):
    """Copy finished assets into the review folder for quick SSH checks."""
    ensure_directories()
    copied = []
    for path in paths:
        if path and os.path.exists(path):
            destination = os.path.join(REVIEW_DIR, os.path.basename(path))
            shutil.copy2(path, destination)
            copied.append(destination)
    return copied


def run_pipeline(dry_run=False):
    """
    Full pipeline run.
    dry_run=True skips upload (test mode)
    """
    print(f"\n{'='*55}")
    print(f"  GTA6 AUTOMATED PIPELINE")
    print(f"  {datetime.now().strftime('%A %d %B %Y - %H:%M')}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*55}\n")

    topic = None
    long_path = None
    short_path = None

    try:
        # ── STEP 1: Check clips library ───────────────────────────
        print("[1/7] Checking clips library...")
        scan_clips_folder()

        # ── STEP 2: Scrape topics ──────────────────────────────────
        print("[2/7] Scraping trending topics...")
        topics = build_queue()

        if not topics:
            print("[ERROR] No topics found. Exiting.")
            log_run("N/A", "failed", error="No topics scraped")
            return

        topic_item = topics[0]
        topic = topic_item["title"]
        print(f"       Selected: {topic}")

        # ── STEP 3: Generate script ────────────────────────────────
        print("[3/7] Generating script...")
        script_path, script_text = generate_script(topic_item)
        print(f"       Script: {script_path}")

        # ── STEP 4: Generate voiceover ─────────────────────────────
        print("[4/7] Generating voiceover...")
        audio_path = generate_voiceover(script_path)
        print(f"       Audio: {audio_path}")

        # ── STEP 5: Assemble video ─────────────────────────────────
        print("[5/7] Assembling video...")
        result = build_video(audio_path, topic_item)

        if not result:
            print("[ERROR] Assembly failed. Check clips folder.")
            log_run(topic, "failed", error="Video assembly failed - no clips")
            return

        long_path, short_path = result
        print(f"       Long form: {long_path}")
        print(f"       Short form: {short_path}")

        # ── STEP 6: Generate captions ──────────────────────────────
        print("[6/7] Generating & burning captions...")
        long_captioned, short_captioned = add_captions_to_both(long_path, short_path, audio_path)

        # ── STEP 7: Generate thumbnail ─────────────────────────────
        print("[7/7] Generating thumbnail...")
        thumb_path = generate_thumbnail(topic_item)

        review_files = copy_to_review([long_captioned, short_captioned, thumb_path, script_path])
        if review_files:
            print("\n[REVIEW] Files copied for checking:")
            for path in review_files:
                print(f"  {path}")

        # ── UPLOAD ─────────────────────────────────────────────────
        if dry_run or not AUTO_UPLOAD:
            reason = "DRY RUN" if dry_run else "REVIEW MODE"
            print(f"\n[{reason}] Skipping upload.")
            print(f"  Long form ready:  {long_captioned}")
            print(f"  Short form ready: {short_captioned}")
            print(f"  Thumbnail ready:  {thumb_path}")
            log_run(topic, "success", error=f"{reason.lower()} - not uploaded")
        else:
            print("\n[UPLOAD] Uploading to YouTube...")
            upload_results = upload_to_youtube(
                long_captioned,
                short_captioned,
                topic,
                thumb_path
            )
            long_id = upload_results.get("long_form_id")
            short_id = upload_results.get("short_form_id")
            log_run(topic, "success", long_id=long_id, short_id=short_id)

        mark_topic_used(topic_item)

        # ── DONE ───────────────────────────────────────────────────
        print(f"\n{'='*55}")
        print(f"  PIPELINE COMPLETE")
        if not dry_run and AUTO_UPLOAD:
            print(f"  Long form:  https://youtube.com/watch?v={long_id}")
            print(f"  Short form: https://youtube.com/watch?v={short_id}")
        else:
            print(f"  Review folder: {REVIEW_DIR}")
        print(f"{'='*55}\n")

    except Exception as e:
        error_msg = str(e)
        print(f"\n[PIPELINE ERROR] {error_msg}")
        log_run(topic or "unknown", "failed", error=error_msg)
        raise


def run_stats():
    """Just print current stats."""
    print_stats()
    get_library_summary()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "dry":
            run_pipeline(dry_run=True)
        elif sys.argv[1] == "stats":
            run_stats()
        elif sys.argv[1] == "clips":
            scan_clips_folder()
            get_library_summary()
    else:
        run_pipeline(dry_run=False)
