# -*- coding: utf-8 -*-
"""
Topic collector for the GTA 6 pipeline.

Uses public JSON/RSS endpoints where possible, stores a scored queue locally,
and falls back to safe evergreen topics when the network is unavailable.
"""

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from config import (
    BLOCKED_TERMS,
    MAX_TOPICS_PER_RUN,
    QUEUE_FILE,
    REDDIT_SOURCES,
    SEED_TOPICS,
    USED_TOPICS_FILE,
    YOUTUBE_RSS_FEEDS,
    ensure_directories,
)

USER_AGENT = "gta6-content-pipeline/1.0"


def _load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _is_blocked(title):
    title_lower = title.lower()
    return any(term in title_lower for term in BLOCKED_TERMS)


def _risk_for(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ["leak", "leaked", "rumor", "rumour"]):
        return "medium"
    return "low"


def _request_text(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        print(f"[Scraper] Certificate check failed for public feed, retrying once: {url}")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            return response.read().decode("utf-8", errors="replace")


def _reddit_topics():
    topics = []
    for url in REDDIT_SOURCES:
        try:
            payload = json.loads(_request_text(url))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            print(f"[Scraper] Reddit source failed: {url} ({exc})")
            continue

        for child in payload.get("data", {}).get("children", []):
            data = child.get("data", {})
            title = data.get("title", "").strip()
            if not title or _is_blocked(title):
                continue
            if "gta" not in title.lower() and "rockstar" not in title.lower():
                continue

            topics.append({
                "id": _slug(title),
                "title": title,
                "source": "reddit",
                "url": "https://www.reddit.com" + data.get("permalink", ""),
                "score": int(data.get("score", 0)) + int(data.get("num_comments", 0)),
                "risk": _risk_for(title),
                "collected_at": datetime.now().isoformat(timespec="seconds"),
            })
    return topics


def _youtube_topics():
    topics = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for url in YOUTUBE_RSS_FEEDS:
        try:
            root = ET.fromstring(_request_text(url))
        except (urllib.error.URLError, TimeoutError, ET.ParseError, OSError) as exc:
            print(f"[Scraper] YouTube RSS failed: {url} ({exc})")
            continue

        for entry in root.findall("atom:entry", ns):
            title_node = entry.find("atom:title", ns)
            link_node = entry.find("atom:link", ns)
            title = title_node.text.strip() if title_node is not None and title_node.text else ""
            if not title or _is_blocked(title):
                continue
            link = link_node.attrib.get("href", url) if link_node is not None else url
            topics.append({
                "id": _slug(title),
                "title": title,
                "source": "youtube_rss",
                "url": link,
                "score": 50,
                "risk": "low",
                "collected_at": datetime.now().isoformat(timespec="seconds"),
            })
    return topics


def _dedupe(topics):
    best = {}
    for topic in topics:
        key = topic.get("id") or _slug(topic["title"])
        topic["id"] = key
        if key not in best or topic.get("score", 0) > best[key].get("score", 0):
            best[key] = topic
    return list(best.values())


def mark_topic_used(topic):
    used = _load_json(USED_TOPICS_FILE, {"topics": []})
    topic_id = topic.get("id") if isinstance(topic, dict) else _slug(str(topic))
    if topic_id not in used["topics"]:
        used["topics"].append(topic_id)
    used["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_json(USED_TOPICS_FILE, used)


def build_queue():
    """Collect, score, dedupe, and persist topic candidates."""
    ensure_directories()
    used = set(_load_json(USED_TOPICS_FILE, {"topics": []}).get("topics", []))

    topics = []
    topics.extend(_reddit_topics())
    topics.extend(_youtube_topics())
    topics.extend({**topic, "id": _slug(topic["title"])} for topic in SEED_TOPICS)

    queue = [
        topic for topic in _dedupe(topics)
        if topic["id"] not in used and not _is_blocked(topic["title"])
    ]
    queue.sort(key=lambda item: item.get("score", 0), reverse=True)
    queue = queue[:MAX_TOPICS_PER_RUN]

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "count": len(queue),
        "topics": queue,
    }
    _save_json(QUEUE_FILE, payload)
    print(f"[Scraper] Queue ready with {len(queue)} topic(s)")
    time.sleep(0.2)
    return queue


if __name__ == "__main__":
    for item in build_queue():
        print(f"{item['score']:>5} | {item['source']:<11} | {item['title']}")
