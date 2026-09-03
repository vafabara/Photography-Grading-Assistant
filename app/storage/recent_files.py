import json
from pathlib import Path

RECENT_FILES_PATH = Path(__file__).resolve().parents[2] / "recent_files.json"
MAX_RECENT_FILES = 5


def load_recent_files():
    if not RECENT_FILES_PATH.exists():
        return []

    try:
        with open(RECENT_FILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def add_recent_file(path):
    recent = load_recent_files()
    path = str(path)

    if path in recent:
        recent.remove(path)

    recent.insert(0, path)
    recent = recent[:MAX_RECENT_FILES]

    try:
        with open(RECENT_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
    except OSError:
        pass

    return recent