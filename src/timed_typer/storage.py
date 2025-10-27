from __future__ import annotations

import json, os, tempfile
from pathlib import Path
from typing import Dict, Any
from copy import deepcopy

APP_NAME = "TimedTyper"
VERSION = "1.0"


def _profile_dir() -> Path:
    """
    Profile directory for save data.
    Windows:  %LOCALAPPDATA%\\TimedTyper
    Others:   ~/TimedTyper
    We create it if it's missing.
    """
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


# Where we save the player's progress (PBs, unlocks, settings).
DEFAULT_PATH = _profile_dir() / "profile.json"

# Persistent data layout:
#   "pbs": { "1": {"wpm": float, "accuracy": float}, ... }
#          accuracy is stored 0.0–1.0, not percent.
#   "unlocks": { "1": True, "2": True, ... }
#   "settings": misc stuff like color mode etc.
DEFAULT_STORE: Dict[str, Any] = {
    "version": VERSION,
    "pbs": {},
    "unlocks": {"1": True},  # Level 1 unlocked by default
    "settings": {
        "seed": 42,
        "color": True,
    },
}


def _deepcopy_default() -> Dict[str, Any]:
    # fresh copy so we never mutate DEFAULT_STORE globally
    return deepcopy(DEFAULT_STORE)


def load_store(path: Path | None = None) -> Dict[str, Any]:
    """
    Read the JSON save file from disk into a dict.
    If file doesn't exist or it's corrupted, fall back to defaults.

    We also forward-merge DEFAULT_STORE so that
    new keys (like new settings) appear for old players.
    """
    path = path or DEFAULT_PATH
    if not path.exists():
        return _deepcopy_default()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # corrupt / unreadable -> start clean
        return _deepcopy_default()

    # start with defaults, then merge user data
    store = _deepcopy_default()
    for key in ("pbs", "unlocks", "settings", "version"):
        if key in data:
            if isinstance(store.get(key), dict) and isinstance(data.get(key), dict):
                store[key].update(data[key])
            else:
                store[key] = data[key]

    # MIGRATION: old builds saved PBs with "acc" instead of "accuracy".
    # Upgrade them in memory now so rest of the code never KeyErrors.
    for lvl, pb in list(store.get("pbs", {}).items()):
        if isinstance(pb, dict):
            if "accuracy" not in pb and "acc" in pb:
                pb["accuracy"] = pb["acc"]
                del pb["acc"]

    return store


def save_store(store: Dict[str, Any], path: Path | None = None) -> None:
    """
    Safely write the current store dict to disk as JSON.

    We write to a temp file and then replace the real file in one move.
    That avoids half-written files if the game crashes mid-save.
    (Writing dicts to JSON files with json.dump is a common way to persist
    game state / progress in Python.)  # ref: json.dump usage :contentReference[oaicite:3]{index=3}
    """
    path = path or DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix="profile.", suffix=".json", dir=str(path.parent)
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
        os.replace(tmp_name, path)
    finally:
        # best-effort cleanup if replace failed
        if os.path.exists(tmp_name):
            try:
                os.remove(tmp_name)
            except OSError:
                pass


def record_pb(store: Dict[str, Any], level_id: int, wpm_val: float, acc_val: float) -> None:
    """
    Update personal best (PB) for a level in *store*.

    PB format we guarantee everywhere:
        {"wpm": <float>, "accuracy": <float 0.0-1.0>}

    We keep the BEST of old vs new for both speed and accuracy.
    We also migrate any legacy "acc" keys to "accuracy" so the rest of
    the game (like menu.py) can safely read pb["accuracy"] without crashing.
    A KeyError happens if you try to access a dict key that doesn't exist,
    so normalizing keys prevents that.  :contentReference[oaicite:4]{index=4}
    """
    k = str(level_id)

    old_pb = store["pbs"].get(k)
    if isinstance(old_pb, dict):
        # migrate old schema {"wpm": X, "acc": Y} -> {"wpm": X, "accuracy": Y}
        if "accuracy" not in old_pb and "acc" in old_pb:
            old_pb["accuracy"] = old_pb["acc"]
            del old_pb["acc"]

    new_pb = {
        "wpm": wpm_val,
        "accuracy": acc_val,  # still ratio, e.g. 0.95 means 95%
    }

    if old_pb is None:
        store["pbs"][k] = new_pb
    else:
        best_wpm = max(old_pb.get("wpm", 0.0), new_pb["wpm"])
        best_acc = max(old_pb.get("accuracy", 0.0), new_pb["accuracy"])
        store["pbs"][k] = {"wpm": best_wpm, "accuracy": best_acc}


def unlock_next_level(store: Dict[str, Any], just_cleared: int) -> None:
    """
    Mark the next level as unlocked in *store*.
    Example: beat level 1 -> unlock "2".
    """
    nxt = str(just_cleared + 1)
    store.setdefault("unlocks", {})
    store["unlocks"][nxt] = True


# ---------------------------------------------------------------------------
# Backwards-compat shim layer
#
# Your older code (menu.py, selftest.py, etc.) imports functions like:
#   get_store, is_unlocked, set_unlocked, save_pb
# and expects them to exist in storage.py. After refactoring, if those names
# disappear you get ImportError: cannot import name 'X'. This is normal in
# Python when code imports a symbol that the module doesn't define. :contentReference[oaicite:5]{index=5}
#
# We re-expose those names here so the rest of the app keeps working without
# rewriting every file at once.
# ---------------------------------------------------------------------------

def get_store() -> Dict[str, Any]:
    """
    Old API expected by menu.py.
    Return a fresh copy of the persisted store from disk.
    """
    return load_store()


def is_unlocked(level_id: int) -> bool:
    """
    Old API expected by menu.py.
    Return True/False if this level id is unlocked in the save file.
    """
    store = load_store()
    return bool(store.get("unlocks", {}).get(str(level_id), False))


def set_unlocked(level_id: int, value: bool = True) -> None:
    """
    Old API used by menu/debug code.
    Force a level to be unlocked (or relock it), then save.
    """
    store = load_store()
    if value:
        store.setdefault("unlocks", {})
        store["unlocks"][str(level_id)] = True
    else:
        store.setdefault("unlocks", {})
        store["unlocks"].pop(str(level_id), None)
    save_store(store)


def save_store_alias(store: Dict[str, Any]) -> None:
    """
    Some legacy code might call save_store_alias(...) instead of save_store(...).
    Keep it so imports don't explode.
    """
    save_store(store)


def save_pb(level_id: int, wpm_val: float, acc_val: float) -> None:
    """
    Old API used by selftest.py and early play code.
    Writes a PB for this level straight to disk.
    Steps:
      1. load_store()
      2. record_pb(...)
      3. save_store(...)
    """
    store = load_store()
    record_pb(store, level_id, wpm_val, acc_val)
    save_store(store)
