# -*- coding: utf-8 -*-
"""
GTA6 Pipeline - Logger & Tracker
Logs every run, tracks videos produced, upload status, errors.
"""

import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "pipeline_history.json")
DAILY_LOG = os.path.join(os.path.dirname(__file__), "logs", "daily.log")


def load_history():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {"runs": [], "total_videos": 0, "total_shorts": 0, "errors": 0}


def save_history(history):
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)


def log_run(topic, status, long_id=None, short_id=None, error=None):
    """Log a pipeline run result."""
    history = load_history()
    
    entry = {
        "timestamp": str(datetime.now()),
        "topic": topic,
        "status": status,  # "success", "partial", "failed"
        "youtube_long_id": long_id,
        "youtube_short_id": short_id,
        "error": error
    }
    
    history["runs"].append(entry)
    
    if status == "success":
        if long_id:
            history["total_videos"] = history.get("total_videos", 0) + 1
        if short_id:
            history["total_shorts"] = history.get("total_shorts", 0) + 1
    elif status == "failed":
        history["errors"] = history.get("errors", 0) + 1
    
    save_history(history)
    
    # also write to plain text log
    with open(DAILY_LOG, "a") as f:
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {status.upper()} | {topic}"
        if long_id:
            line += f" | YT: {long_id}"
        if error:
            line += f" | ERR: {error[:80]}"
        f.write(line + "\n")
    
    return entry


def print_stats():
    """Print pipeline performance summary."""
    history = load_history()
    runs = history.get("runs", [])
    
    total = len(runs)
    success = sum(1 for r in runs if r["status"] == "success")
    failed = sum(1 for r in runs if r["status"] == "failed")
    
    print(f"\n{'='*45}")
    print(f"  GTA6 PIPELINE STATS")
    print(f"{'='*45}")
    print(f"  Total runs:      {total}")
    print(f"  Successful:      {success}")
    print(f"  Failed:          {failed}")
    print(f"  Videos uploaded: {history.get('total_videos', 0)}")
    print(f"  Shorts uploaded: {history.get('total_shorts', 0)}")
    
    if runs:
        print(f"\n  RECENT RUNS:")
        for r in runs[-5:][::-1]:
            ts = r["timestamp"][:16]
            status = r["status"].upper()
            topic = r["topic"][:45]
            print(f"  [{ts}] {status:8} | {topic}")
    
    print(f"{'='*45}\n")


if __name__ == "__main__":
    print_stats()
