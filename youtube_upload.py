# -*- coding: utf-8 -*-
"""
GTA6 Pipeline - YouTube Auto Uploader
Handles OAuth, uploads long form + sets thumbnail, metadata, tags
"""

import os
import json
import pickle
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

GTA6_TAGS = [
    "GTA 6", "Grand Theft Auto 6", "GTA VI", "GTA 6 leak",
    "GTA 6 gameplay", "GTA 6 news", "GTA 6 update", "GTA 6 2026",
    "Rockstar Games", "GTA 6 Vice City", "GTA 6 Leonida",
    "GTA 6 trailer", "GTA Online", "GTA 6 release date",
    "GTA 6 money glitch", "GTA 6 heist", "GTA 6 tips"
]

DESCRIPTION_TEMPLATE = """
{topic}

Everything you need to know about GTA 6 - leaks, updates, gameplay breakdowns and more.

Stay ahead of every GTA 6 update. Subscribe and hit the bell so you never miss a video.

--

TIMESTAMPS
0:00 - Introduction
0:30 - {topic}
{duration_marker} - Wrap Up

--

#GTA6 #GrandTheftAuto6 #GTAVI #Rockstar #GTA6Leak #GTA6News #GTA6Update
"""


def get_authenticated_service():
    """Handle OAuth - runs browser auth on first use, token cached after."""
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "token.pickle")
    secrets_path = os.path.join(os.path.dirname(__file__), "client_secrets.json")

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secrets_path):
                raise FileNotFoundError(
                    "client_secrets.json not found.\n"
                    "Download it from Google Cloud Console:\n"
                    "  APIs & Services > Credentials > OAuth 2.0 Client > Download JSON\n"
                    "Place it in ~/gta6-pipeline/client_secrets.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            # On Pi with no browser: use --noauth_local_webserver equivalent
            creds = flow.run_local_server(port=8080, open_browser=False)

        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path, title, description, thumbnail_path=None, is_short=False):
    """Upload a video to YouTube with full metadata."""
    from googleapiclient.http import MediaFileUpload

    print(f"[YouTube] Authenticating...")
    service = get_authenticated_service()

    if is_short:
        full_title = f"{title[:80]} #Shorts"
        category_id = "20"  # Gaming
    else:
        full_title = title[:100]
        category_id = "20"

    body = {
        "snippet": {
            "title": full_title,
            "description": description,
            "tags": GTA6_TAGS,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    print(f"[YouTube] Uploading: {os.path.basename(video_path)}")
    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024  # 1MB chunks - safe for Pi
    )

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[YouTube] Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"[YouTube] Uploaded successfully: https://youtube.com/watch?v={video_id}")

    # Set thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        print(f"[YouTube] Setting thumbnail...")
        service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        ).execute()
        print(f"[YouTube] Thumbnail set.")

    return video_id


def upload_to_youtube(long_path, short_path, topic_title, thumbnail_path=None):
    """Main function called by orchestrator."""
    timestamp = datetime.now().strftime("%d %b %Y").upper()
    
    description = DESCRIPTION_TEMPLATE.format(
        topic=topic_title,
        duration_marker="8:00"
    )

    results = {}

    # Upload long form
    if long_path and os.path.exists(long_path):
        long_title = f"GTA 6 - {topic_title} ({timestamp})"
        vid_id = upload_video(long_path, long_title, description, thumbnail_path, is_short=False)
        results["long_form_id"] = vid_id

    # Upload short form
    if short_path and os.path.exists(short_path):
        short_title = f"GTA 6 {topic_title[:50]}"
        short_desc = f"GTA 6 latest - {topic_title}\n\n#GTA6 #GTA6Shorts #Shorts #GrandTheftAuto6"
        vid_id = upload_video(short_path, short_title, short_desc, is_short=True)
        results["short_form_id"] = vid_id

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 youtube_upload.py <long_video.mp4> <topic title>")
    else:
        upload_to_youtube(sys.argv[1], None, sys.argv[2])
