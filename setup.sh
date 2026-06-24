#!/bin/bash
# GTA6 Pipeline - Raspberry Pi setup
# Usage: bash setup.sh

set -e

PROJECT_DIR="${HOME}/gta6-pipeline"
VENV_DIR="${PROJECT_DIR}/.venv"

echo ""
echo "================================================"
echo "  GTA6 Pipeline - Raspberry Pi Setup"
echo "================================================"
echo ""

echo "[1/6] Installing system packages..."
sudo apt update
sudo apt install -y ffmpeg python3-pip python3-venv git curl

echo "[2/6] Creating project folders..."
mkdir -p "${PROJECT_DIR}"
cd "${PROJECT_DIR}"
mkdir -p clips scripts audio output thumbnails queue logs data review

echo "[3/6] Creating Python virtual environment..."
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip wheel

echo "[4/6] Installing Python packages..."
if [ -f requirements.txt ]; then
  "${VENV_DIR}/bin/pip" install -r requirements.txt
else
  "${VENV_DIR}/bin/pip" install edge-tts Pillow requests google-api-python-client google-auth-oauthlib google-auth-httplib2 openai-whisper yt-dlp
fi

echo "[5/6] Installing yt-dlp command..."
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

echo "[6/6] Installing daily review-mode cron job..."
CRON_JOB="0 9 * * * cd ${PROJECT_DIR} && ${VENV_DIR}/bin/python run_pipeline.py >> logs/cron.log 2>&1"
( crontab -l 2>/dev/null | grep -v "gta6-pipeline" ; echo "$CRON_JOB" ) | crontab -

echo ""
echo "================================================"
echo "  SETUP COMPLETE"
echo "================================================"
echo ""
echo "Next:"
echo "  1. Copy this project into ${PROJECT_DIR} if you have not already."
echo "  2. Add clips with: ${VENV_DIR}/bin/python clips_manager.py download"
echo "  3. Test with: ${VENV_DIR}/bin/python run_pipeline.py dry"
echo "  4. Check finished drafts in: ${PROJECT_DIR}/review"
echo ""
echo "Uploads are disabled by default. Set GTA6_AUTO_UPLOAD=true only after testing."
