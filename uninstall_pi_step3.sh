#!/bin/bash
# Remove the GTA6 pipeline setup installed by setup.sh.
# This keeps your source files unless you choose to remove the whole project.

set -e

PROJECT_DIR="${HOME}/gta6-pipeline"

echo "Removing GTA6 pipeline cron job..."
( crontab -l 2>/dev/null | grep -v "gta6-pipeline" ) | crontab - || true

echo "Removing Python virtual environment and generated folders..."
rm -rf "${PROJECT_DIR}/.venv"
rm -rf "${PROJECT_DIR}/audio"
rm -rf "${PROJECT_DIR}/output"
rm -rf "${PROJECT_DIR}/review"
rm -rf "${PROJECT_DIR}/thumbnails"
rm -rf "${PROJECT_DIR}/tmp"
rm -rf "${PROJECT_DIR}/pip-cache"
rm -rf "${PROJECT_DIR}/__pycache__"
find "${PROJECT_DIR}" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Removing yt-dlp command installed by setup.sh..."
sudo rm -f /usr/local/bin/yt-dlp

echo "Clearing Python and apt caches..."
rm -rf "${HOME}/.cache/pip"
rm -rf "${HOME}/.cache/whisper"
sudo apt clean
sudo apt autoremove -y

echo ""
echo "Optional: remove system packages installed by setup.sh."
echo "Run this only if you do not need them for anything else:"
echo "  sudo apt remove -y ffmpeg python3-pip python3-venv git curl"
echo "  sudo apt autoremove -y"
echo ""
echo "Storage after cleanup:"
df -h
