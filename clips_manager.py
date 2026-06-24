# -*- coding: utf-8 -*-
"""
GTA6 Pipeline - Clips Manager
Downloads trailers, organises footage library, tracks what's been used.
Install yt-dlp first: pip3 install yt-dlp
"""

import os
import json
import subprocess
from datetime import datetime

CLIPS_DIR = os.path.join(os.path.dirname(__file__), "clips")
METADATA_FILE = os.path.join(CLIPS_DIR, "library.json")

# Official GTA 6 trailers - add more as Rockstar releases them
OFFICIAL_SOURCES = [
    {
        "id": "trailer1",
        "url": "https://www.youtube.com/watch?v=QdBZExpgErs",
        "title": "GTA 6 Trailer 1 Official",
        "tags": ["vice_city", "lucia", "jason", "official"]
    },
    {
        "id": "trailer2",
        "url": "https://www.youtube.com/watch?v=i1VTvSyLfRo",
        "title": "GTA 6 Trailer 2 Official",
        "tags": ["gameplay", "map", "official", "leonida"]
    }
]

# Subreddits and channels to monitor for leaked/community footage
# NOTE: Only download content that is clearly user-created or fair use
COMMUNITY_SOURCES = [
    "https://www.reddit.com/r/GTA6/",
    "https://www.reddit.com/r/GrandTheftAutoVI/"
]


def load_library():
    """Load the clips metadata library."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"clips": [], "last_updated": None}


def save_library(library):
    with open(METADATA_FILE, "w") as f:
        json.dump(library, f, indent=2)


def download_official_trailers():
    """Download official Rockstar trailers via yt-dlp."""
    os.makedirs(CLIPS_DIR, exist_ok=True)
    library = load_library()
    downloaded_ids = [c["id"] for c in library["clips"]]

    for source in OFFICIAL_SOURCES:
        if source["id"] in downloaded_ids:
            print(f"[Clips] Already have: {source['title']}")
            continue

        output_path = os.path.join(CLIPS_DIR, f"{source['id']}.mp4")
        print(f"[Clips] Downloading: {source['title']}")

        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "--merge-output-format", "mp4",
            "-o", output_path,
            source["url"]
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            library["clips"].append({
                "id": source["id"],
                "title": source["title"],
                "path": output_path,
                "tags": source["tags"],
                "size_mb": round(size_mb, 1),
                "use_count": 0,
                "downloaded": str(datetime.now())
            })
            print(f"[Clips] Downloaded: {source['title']} ({size_mb:.1f}MB)")
        else:
            print(f"[Clips] Failed: {source['title']}")
            print(result.stderr[:200])

    library["last_updated"] = str(datetime.now())
    save_library(library)
    return library


def add_manual_clip(file_path, title, tags=None):
    """
    Register a manually added clip (screenshot, leaked footage etc).
    Call this when you drop something into the /clips folder manually.
    """
    library = load_library()
    
    if not os.path.exists(file_path):
        print(f"[Clips] File not found: {file_path}")
        return

    clip_id = os.path.splitext(os.path.basename(file_path))[0]
    existing = [c["id"] for c in library["clips"]]
    
    if clip_id in existing:
        print(f"[Clips] Already registered: {clip_id}")
        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    library["clips"].append({
        "id": clip_id,
        "title": title,
        "path": file_path,
        "tags": tags or ["manual"],
        "size_mb": round(size_mb, 1),
        "use_count": 0,
        "added": str(datetime.now())
    })
    
    save_library(library)
    print(f"[Clips] Registered: {title} ({size_mb:.1f}MB)")


def get_clips_by_tags(tags=None):
    """Get clips filtered by tags. Returns all if no tags specified."""
    library = load_library()
    clips = library["clips"]
    
    if not tags:
        return [c["path"] for c in clips if os.path.exists(c["path"])]
    
    matched = []
    for clip in clips:
        if any(t in clip.get("tags", []) for t in tags):
            if os.path.exists(clip["path"]):
                matched.append(clip["path"])
    
    return matched


def mark_clip_used(clip_path):
    """Track how many times each clip has been used."""
    library = load_library()
    for clip in library["clips"]:
        if clip["path"] == clip_path:
            clip["use_count"] = clip.get("use_count", 0) + 1
            clip["last_used"] = str(datetime.now())
    save_library(library)


def get_library_summary():
    """Print a summary of the clips library."""
    library = load_library()
    clips = library["clips"]
    total_size = sum(c.get("size_mb", 0) for c in clips)
    
    print(f"\n{'='*40}")
    print(f"CLIPS LIBRARY SUMMARY")
    print(f"{'='*40}")
    print(f"Total clips:  {len(clips)}")
    print(f"Total size:   {total_size:.1f} MB")
    print(f"Last updated: {library.get('last_updated', 'Never')}")
    print(f"\nClips:")
    for c in clips:
        tags = ", ".join(c.get("tags", []))
        uses = c.get("use_count", 0)
        print(f"  [{uses}x used] {c['title']} - {c.get('size_mb',0):.1f}MB - [{tags}]")
    print(f"{'='*40}\n")


def scan_clips_folder():
    """Scan clips folder and auto-register any untracked MP4s."""
    os.makedirs(CLIPS_DIR, exist_ok=True)
    library = load_library()
    registered_paths = [c["path"] for c in library["clips"]]
    
    new_count = 0
    for filename in os.listdir(CLIPS_DIR):
        if filename.endswith((".mp4", ".mov", ".mkv")):
            full_path = os.path.join(CLIPS_DIR, filename)
            if full_path not in registered_paths:
                title = os.path.splitext(filename)[0].replace("_", " ")
                add_manual_clip(full_path, title, tags=["untagged"])
                new_count += 1
    
    if new_count:
        print(f"[Clips] Auto-registered {new_count} new clips")
    else:
        print(f"[Clips] Library up to date")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        get_library_summary()
    elif sys.argv[1] == "download":
        download_official_trailers()
    elif sys.argv[1] == "scan":
        scan_clips_folder()
    elif sys.argv[1] == "summary":
        get_library_summary()
    elif sys.argv[1] == "add" and len(sys.argv) >= 4:
        add_manual_clip(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  python3 clips_manager.py download    - Download official trailers")
        print("  python3 clips_manager.py scan        - Register new clips in /clips folder")
        print("  python3 clips_manager.py summary     - Show library summary")
        print("  python3 clips_manager.py add <path> <title>  - Register a specific clip")
