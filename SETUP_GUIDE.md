# GTA 6 Pipeline Setup Guide

This guide takes you from a fresh Raspberry Pi 4B to an automated review-mode GTA 6 content pipeline.

The pipeline is designed to create finished draft videos and put them in `review/`. Public uploads are disabled by default until you deliberately enable them.

## 1. Prepare The Pi

Update the Pi:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git rsync ffmpeg python3-pip python3-venv curl
```

Create the project folder:

```bash
mkdir -p ~/gta6-pipeline
```

## 2. Copy The Project Over SSH

### Option A: Windows PowerShell

From PowerShell on your main PC, run this from the project folder:

```powershell
.\deploy_to_pi.ps1 -PiHost YOUR_PI_IP -PiUser pi
```

Example:

```powershell
.\deploy_to_pi.ps1 -PiHost 192.168.1.42 -PiUser pi
```

This creates a zip, copies it with `scp`, extracts it on the Pi, and leaves the project at:

```text
~/gta6-pipeline
```

### Option B: Manual Windows SCP

If you do not want to use the helper script, make a zip of the project folder, then run:

```powershell
scp .\gta6-pipeline.zip pi@YOUR_PI_IP:~/gta6-pipeline.zip
ssh pi@YOUR_PI_IP
mkdir -p ~/gta6-pipeline
unzip -o ~/gta6-pipeline.zip -d ~/gta6-pipeline
rm ~/gta6-pipeline.zip
```

### Option C: Git

If you put this project in a Git repository, SSH into the Pi and clone it:

```bash
git clone YOUR_REPO_URL ~/gta6-pipeline
```

## 3. Run The Installer

On the Pi:

```bash
cd ~/gta6-pipeline
bash setup.sh
```

This installs:

- FFmpeg for video assembly.
- Python virtual environment in `~/gta6-pipeline/.venv`.
- Python packages for voice, thumbnails, captions, and YouTube upload.
- `yt-dlp`.
- A 9am daily cron job in review mode.

If your project lives at `~/gta6-pipeline`, the virtual environment will be:

```bash
~/gta6-pipeline/.venv
```

## 4. Add Source Clips

Download official trailer clips:

```bash
cd ~/gta6-pipeline
.venv/bin/python clips_manager.py download
```

You can also place your own allowed footage in:

```text
~/gta6-pipeline/clips/
```

Then register it:

```bash
.venv/bin/python clips_manager.py scan
```

Use official trailers, your own gameplay, or footage you have permission to use. Do not redistribute stolen build footage, private leaks, or third-party videos you do not have rights to use.

## 5. Run A Dry Test

```bash
cd ~/gta6-pipeline
.venv/bin/python run_pipeline.py dry
```

Expected result:

- A topic queue is created in `data/topic_queue.json`.
- A script is saved in `scripts/`.
- Audio is saved in `audio/`.
- Long and short videos are saved in `output/`.
- Review copies are saved in `review/`.
- Upload is skipped.

Check the review folder:

```bash
ls -lh ~/gta6-pipeline/review
```

## 6. Daily Automation

The installer adds a cron job:

```bash
0 9 * * * cd /home/pi/gta6-pipeline && /home/pi/gta6-pipeline/.venv/bin/python run_pipeline.py >> logs/cron.log 2>&1
```

View cron:

```bash
crontab -l
```

View logs:

```bash
tail -n 100 ~/gta6-pipeline/logs/cron.log
```

## 7. Review Mode

By default, `run_pipeline.py` does not upload publicly. It creates files in:

```text
~/gta6-pipeline/review/
```

This is the safest early workflow:

1. Let the Pi generate drafts.
2. Check the title, script, audio, short, long video, and thumbnail.
3. Upload manually until the output quality is consistently good.

## 8. YouTube Upload Setup

Only do this after review-mode testing is stable.

1. Go to Google Cloud Console.
2. Create a project.
3. Enable YouTube Data API v3.
4. Create OAuth credentials for a Desktop app.
5. Download the JSON file.
6. Rename it to:

```text
client_secrets.json
```

7. Place it in:

```text
~/gta6-pipeline/client_secrets.json
```

Run the uploader once interactively:

```bash
cd ~/gta6-pipeline
.venv/bin/python youtube_upload.py output/YOUR_VIDEO.mp4 "Test GTA 6 Upload"
```

The Pi will print an auth URL. Open it on your main computer, log in, and complete the OAuth flow.

## 9. Enable Automatic Uploads

Automatic public uploads are controlled by an environment variable:

```bash
export GTA6_AUTO_UPLOAD=true
```

To enable it for cron, edit cron:

```bash
crontab -e
```

Change the job to:

```bash
0 9 * * * cd /home/pi/gta6-pipeline && GTA6_AUTO_UPLOAD=true /home/pi/gta6-pipeline/.venv/bin/python run_pipeline.py >> logs/cron.log 2>&1
```

Recommended: keep this off until you have reviewed at least 10-20 generated drafts.

## 10. Useful Commands

Run pipeline in safe dry mode:

```bash
.venv/bin/python run_pipeline.py dry
```

Run pipeline in review mode:

```bash
.venv/bin/python run_pipeline.py
```

Show stats:

```bash
.venv/bin/python run_pipeline.py stats
```

Show clip library:

```bash
.venv/bin/python run_pipeline.py clips
```

Scan new clips:

```bash
.venv/bin/python clips_manager.py scan
```

Watch the cron log:

```bash
tail -f logs/cron.log
```

## 11. Content Rules

For pre-release content:

- Prefer official Rockstar sources and public community discussion.
- Label rumors and leaks as unconfirmed.
- Do not use stolen files, private footage, leaked builds, or copyrighted third-party videos.
- Keep scripts source-aware.

For post-release content:

- Use your own captured gameplay where possible.
- Focus on money routes, heists, collectible guides, beginner guides, update explainers, and efficient progression.
- Avoid building the channel around patched exploits or account-risk methods.

## 12. Troubleshooting

If voice generation fails, check:

```bash
.venv/bin/python -c "import edge_tts; print('edge-tts ok')"
```

If video assembly fails, check:

```bash
ffmpeg -version
ffprobe -version
```

If captions are slow, keep Whisper on the `tiny` model in `captions.py`.

If uploads fail, check:

- `client_secrets.json` is in the project root.
- OAuth has been completed.
- The YouTube Data API v3 is enabled.
- The account has not hit upload or API quota limits.
