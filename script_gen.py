# -*- coding: utf-8 -*-
"""Template-based script generator for source-backed GTA 6 videos."""

import json
import os
import re
from datetime import datetime

from config import CHANNEL_NAME, SCRIPTS_DIR, ensure_directories


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "gta6-topic"


def _normalise_topic(topic):
    if isinstance(topic, dict):
        return topic
    return {
        "id": _slug(str(topic)),
        "title": str(topic),
        "source": "manual",
        "url": "",
        "score": 0,
        "risk": "medium" if "leak" in str(topic).lower() else "low",
    }


def _disclaimer(topic):
    if topic.get("risk") == "medium":
        return (
            "Quick note before we start: anything described as a leak or rumor "
            "should be treated as unconfirmed unless Rockstar confirms it."
        )
    return "This breakdown sticks to public information and clearly labelled community discussion."


def _long_script(topic):
    title = topic["title"]
    url = topic.get("url") or "No direct source URL saved"
    return f"""GTA 6 update: {title}

{_disclaimer(topic)}

Here is the clean breakdown.

First, the reason this matters is simple: GTA 6 is still in the pre-release hype cycle, so every official detail, trailer frame, community theory, and search trend gets pulled apart fast. The goal here is not to overhype one random post. The goal is to separate what is actually useful from what is just noise.

The topic today is: {title}.

The source logged for this video is: {url}

Point one: what we actually know. If this came from an official source, it can be treated as a solid detail. If it came from Reddit, YouTube discussion, or community speculation, it should be treated as a signal of what players are currently interested in, not as confirmed game information.

Point two: why the community cares. For GTA 6, players are watching for map size, enterable buildings, heist structure, money-making systems, police behavior, online features, vehicles, weapons, side activities, and whether Vice City and Leonida feel dense enough to support years of content.

Point three: what to watch next. The most reliable clues usually come from new Rockstar posts, trailer descriptions, store page updates, age-rating listings, investor call wording, official screenshots, and later on, hands-on gameplay. Random claims without a clear source should stay in the rumor box.

So the practical takeaway is this: {title} is worth watching, but it should be judged by the strength of the source. If it connects to official material, it may shape what players can expect. If it is only community chatter, it is still useful as a trend because it shows what people want covered next.

For this channel, the plan is to keep tracking GTA 6 news, map details, heist theories, money guides, trailer breakdowns, and eventually post-release routes that actually help players make progress.

Bottom line: stay excited, but stay sharp. The best GTA 6 content is going to come from clear sources, fast updates, and guides that are useful after the hype dies down.

That is the update for now. More GTA 6 breakdowns, guides, and release coverage are coming soon.
"""


def _short_script(topic):
    title = topic["title"]
    return f"""GTA 6 quick update.

Today's topic is: {title}.

The important thing is to separate confirmed details from community speculation. Official Rockstar material matters most. Rumors can show what players are searching for, but they are not confirmation.

Watch this topic if it connects to the map, heists, money systems, vehicles, or online features.

Follow for more GTA 6 news, guides, and quick breakdowns.
"""


def generate_script(topic):
    """
    Generate long and short scripts.

    Returns the long-form script path and text to match the existing
    orchestrator interface.
    """
    ensure_directories()
    topic = _normalise_topic(topic)
    slug = _slug(topic["title"])
    date_prefix = datetime.now().strftime("%Y%m%d-%H%M%S")

    long_text = _long_script(topic)
    short_text = _short_script(topic)

    long_path = os.path.join(SCRIPTS_DIR, f"{date_prefix}-{slug}-long.txt")
    short_path = os.path.join(SCRIPTS_DIR, f"{date_prefix}-{slug}-short.txt")
    meta_path = os.path.join(SCRIPTS_DIR, f"{date_prefix}-{slug}-meta.json")

    with open(long_path, "w", encoding="utf-8") as f:
        f.write(long_text)
    with open(short_path, "w", encoding="utf-8") as f:
        f.write(short_text)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "channel": CHANNEL_NAME,
            "topic": topic,
            "long_script": long_path,
            "short_script": short_path,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }, f, indent=2)

    print(f"[Script] Long script: {long_path}")
    print(f"[Script] Short script: {short_path}")
    return long_path, long_text


if __name__ == "__main__":
    generate_script("Everything officially known about the GTA 6 map so far")
