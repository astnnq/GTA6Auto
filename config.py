# -*- coding: utf-8 -*-
"""
Central settings for the GTA 6 content pipeline.

Defaults are intentionally conservative: the pipeline creates review-ready
videos, but does not publish automatically until AUTO_UPLOAD is set to True.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
QUEUE_FILE = os.path.join(DATA_DIR, "topic_queue.json")
USED_TOPICS_FILE = os.path.join(DATA_DIR, "used_topics.json")

SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")
REVIEW_DIR = os.path.join(BASE_DIR, "review")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

CHANNEL_NAME = "GTA 6 Intel"
DEFAULT_VOICE = os.getenv("GTA6_VOICE", "en-GB-RyanNeural")

AUTO_UPLOAD = os.getenv("GTA6_AUTO_UPLOAD", "false").lower() == "true"
MAX_TOPICS_PER_RUN = int(os.getenv("GTA6_MAX_TOPICS_PER_RUN", "12"))
SHORT_MAX_SECONDS = int(os.getenv("GTA6_SHORT_MAX_SECONDS", "55"))
LONG_TARGET_SECONDS = int(os.getenv("GTA6_LONG_TARGET_SECONDS", "480"))

REDDIT_SOURCES = [
    "https://www.reddit.com/r/GTA6/hot.json?limit=25",
    "https://www.reddit.com/r/GrandTheftAutoVI/hot.json?limit=25",
]

YOUTUBE_RSS_FEEDS = [
    # Rockstar Games official channel.
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC6VcWc1rAoWdBCM0JxrRQ3A",
]

SEED_TOPICS = [
    {
        "title": "Everything officially known about the GTA 6 map so far",
        "source": "seed",
        "url": "https://www.rockstargames.com/VI",
        "score": 40,
        "risk": "low",
    },
    {
        "title": "GTA 6 Vice City and Leonida details from the official trailers",
        "source": "seed",
        "url": "https://www.rockstargames.com/VI",
        "score": 38,
        "risk": "low",
    },
    {
        "title": "GTA 6 release window, platforms, and what players should expect",
        "source": "seed",
        "url": "https://www.rockstargames.com/VI",
        "score": 35,
        "risk": "low",
    },
]

BLOCKED_TERMS = [
    "download leak",
    "leaked build",
    "stolen files",
    "private footage",
    "source code",
]


def ensure_directories():
    """Create the folders used by the pipeline."""
    for path in [
        DATA_DIR,
        SCRIPTS_DIR,
        AUDIO_DIR,
        OUTPUT_DIR,
        THUMBNAILS_DIR,
        REVIEW_DIR,
        LOGS_DIR,
    ]:
        os.makedirs(path, exist_ok=True)
