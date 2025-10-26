from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any

APP_NAME = "TimedTyper"
VERSION = "1.0"

def _profile_dir() -> Path:
    # Windows: %LOCALAPPDATA%\TimedTyper  /  Others: ~/.timed_typer
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d

DEFAULT_PATH = _profile_dir() / "profile.json"

DEFAULT_STORE = {
    "version": VERSION,
    "pbs": {},        # { "1": {"wpm": float, "accuracy": float} }
    "unlocks": {"1": True},  # level 1 unlocked by default
    "settings": dict(seed=42, color=True)
}

def _load(path: Path | None = None) -> Dict[str, Any]:
    path = path or DEFAULT_PATH
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_STORE))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(json.dumps(DEFAULT_STORE))

def _save(store: Dict[str, Any], path: Path | None = None) -> None:
    path = path or DEFAULT_PATH
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")

# === Public API ===

def get_store() -> Dict[str, Any]:
    return _load()

def save_pb(level_id: int, wpm: float, accuracy: float) -> None:
    store = _load()
    key = str(level_id)
    cur = store.get("pbs", {}).get(key)
    # Save only if better WPM or equal WPM with better accuracy
    if (not cur) or (wpm > cur["wpm"]) or (wpm == cur["wpm"] and accuracy > cur["accuracy"]):
        store.setdefault("pbs", {})[key] = {"wpm": float(wpm), "accuracy": float(accuracy)}
    _save(store)

def set_unlocked(level_id: int, unlocked: bool = True) -> None:
    store = _load()
    store.setdefault("unlocks", {})[str(level_id)] = bool(unlocked)
    _save(store)

def is_unlocked(level_id: int) -> bool:
    store = _load()
    return store.get("unlocks", {}).get(str(level_id), False if level_id != 1 else True)

def set_setting(name: str, value) -> None:
    store = _load()
    store.setdefault("settings", {})[name] = value
    _save(store)

def get_setting(name: str, default=None):
    store = _load()
    return store.get("settings", {}).get(name, default)
