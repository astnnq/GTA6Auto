# GTA 6 Content Pipeline Review

## Current State

The repo is a starter skeleton, not a working end-to-end pipeline yet.

Existing modules:

- `run_pipeline.py` - top-level orchestrator for scrape -> script -> voice -> assemble -> captions -> thumbnail -> upload.
- `clips_manager.py` - registers clips and can download official trailer sources with `yt-dlp`.
- `captions.py` - creates SRT captions with local Whisper and burns them into long/short videos.
- `youtube_upload.py` - uploads long and short videos to YouTube using OAuth.
- `logger.py` - records run history and basic stats.
- `setup.sh` - Raspberry Pi setup script.

Missing modules imported by `run_pipeline.py`:

- `scraper.py`
- `script_gen.py`
- `voiceover.py`
- `assembler.py`
- `thumbnail.py`
- `config.py`

Because those files do not exist yet, `run_pipeline.py` cannot currently start.

## Main Recommendation

Build this as a queue-based production system, not a single all-or-nothing script.

The Pi should run small jobs that create drafts, score them, and place finished videos into an approval folder. Uploading should be automatic only after the system proves itself for a while.

Recommended flow:

1. Collect topic candidates.
2. Score and deduplicate topics.
3. Generate a source-backed outline.
4. Generate script variants for long and short form.
5. Run a safety/quality check.
6. Generate voiceover.
7. Assemble videos from approved footage.
8. Add captions.
9. Generate thumbnail and metadata.
10. Save to a review queue.
11. Upload only approved items.

This keeps the workflow close to 99% automated while still avoiding bad uploads, copyright issues, low-quality hallucinated claims, and platform strikes.

## Content Safety Rules

For pre-release GTA 6 content:

- Prefer official Rockstar posts, trailers, screenshots, patents, interviews, store listings, and public community discussion.
- Treat leaks as unverified and avoid directly redistributing leaked footage, images, files, private data, or stolen material.
- Do not present rumors as fact.
- Keep a source list for every script.
- Use wording like "reportedly", "community theory", or "unconfirmed" where appropriate.

For post-release content:

- Use your own captured gameplay where possible.
- Prioritize money guides, heist routes, collectible guides, setup guides, beginner tips, and patch update explainers.
- Avoid building the channel around exploits that could be patched quickly or violate platform/game terms.

## Pi-Friendly Stack

Good local/free options:

- Topic collection: Reddit JSON/RSS, Google Trends RSS/manual export, YouTube RSS feeds, public web pages.
- Script generation: local small model if quality is acceptable, or optional external API when enabled.
- Voice: `edge-tts` for free generated speech.
- Captions: `whisper tiny` or `whisper base`; tiny is safer for Pi speed.
- Editing: `ffmpeg`.
- Scheduling: cron or systemd timer.
- Logging/state: JSON at first, SQLite once the queue grows.

Be careful with:

- Fully scraping YouTube trending pages. APIs/RSS are more stable and less likely to break.
- Heavy local LLMs on a Raspberry Pi 4B. The Pi can orchestrate, edit, and upload, but script generation may be slow unless the model is tiny.
- Downloading third-party videos. Use official/allowed assets or your own footage.

## Immediate Build Order

1. Add a `config.py` or `.env` loader for API keys, channel settings, and automation limits.
2. Add `scraper.py` that produces topic candidates with source URLs and confidence scores.
3. Add a queue file or SQLite database so topics are not repeated.
4. Add `script_gen.py` with source-grounded prompts and required disclaimers for unverified topics.
5. Add `voiceover.py` using `edge-tts`.
6. Add `assembler.py` with simple, reliable FFmpeg templates for long and short formats.
7. Add `thumbnail.py` using Pillow templates.
8. Add a review mode that writes final files to `review/` before upload.
9. Add upload rate limits and a cooldown so the account does not spam.
10. Add health checks and daily summary logging.

## Operational Limits To Add

- Maximum uploads per day.
- Minimum source count per video.
- Blocklist for risky topics and phrases.
- Duplicate topic detection.
- Failed-run retry limit.
- Disk cleanup for old audio, temporary renders, and failed drafts.
- A manual approval flag before public upload.

## Suggested Folder Structure

```text
gta6-pipeline/
  config.py
  run_pipeline.py
  scraper.py
  script_gen.py
  voiceover.py
  assembler.py
  thumbnail.py
  captions.py
  youtube_upload.py
  clips_manager.py
  logger.py
  data/
    topics.json
    queue.json
    sources.json
  clips/
  audio/
  scripts/
  output/
  thumbnails/
  review/
  logs/
```

## Viability

The idea is viable, but the best version is "automated drafting with lightweight human approval", especially before release. Fully unattended public uploading is the risky part. The channel will be stronger if the automation is built around source tracking, repeatable templates, and original captured footage once the game launches.
