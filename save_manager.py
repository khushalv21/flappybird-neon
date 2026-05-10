"""Persistent save data – high scores, unlocked themes, settings."""
import json
import os
from datetime import datetime
from pathlib import Path

SAVE_DIR = Path.home() / ".flappybird_neon"
SAVE_FILE = SAVE_DIR / "save.json"

_DEFAULT = {
    "high_score": 0,
    "top_scores": [],
    "unlocked_themes": ["cyberpunk"],
    "selected_theme": "cyberpunk",
    "music_on": True,
    "sfx_on": True,
}


def load():
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        # merge with defaults for forward compat
        for k, v in _DEFAULT.items():
            data.setdefault(k, v)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(_DEFAULT)


def save(data):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_score(data, score, theme_name):
    if score > data["high_score"]:
        data["high_score"] = score
    data["top_scores"].append({
        "score": score,
        "theme": theme_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    data["top_scores"].sort(key=lambda x: x["score"], reverse=True)
    data["top_scores"] = data["top_scores"][:10]
    return data
