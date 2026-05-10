from __future__ import annotations
import json
import os
from pathlib import Path

_APP_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "ImageViewer"
STATE_FILE = _APP_DIR / "state.json"


def save(state: dict):
    try:
        _APP_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load() -> dict:
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}
