"""
practice_level.py — practice on a chosen level's word pool (no timer)
"""
from __future__ import annotations
from typing import Optional

from .state import GameState, Screen
from .levels import get_level
from .words import words_for_level, _pool_for_level  # reuse pool builder
from .timing import Stopwatch, wpm
from .scoring import RunStats, update_accuracy
from .ui_console import render_hud_practice, toast, results_card


HELP_TEXT = "Commands: :skip/s, :q/quit/exit, :help/h"

def _next_word(pool: list[str], prev: Optional[str]) -> str:
    # avoid immediate repeats
    if not pool:
        return ""
    if prev is None:
        return pool[0]
    i = (pool.index(prev) + 1) % len(pool) if prev in pool else 0
    return pool[i]

def practice_level(state: GameState) -> None:
    # Ask level number
    print("\n-- Focus Practice: choose level (1-5), or 'q' to cancel")
    choice = input("> ").strip().lower()
    if choice in ("q", "quit", "exit"):
        state.set_screen(Screen.MENU)
        return
    if not choice.isdigit() or not (1 <= int(choice) <= 5):
        toast("Invalid choice.")
        state.set_screen(Screen.MENU)
        return

    level_num = int(choice)
    cfg = get_level(level_num)
    pool = _pool_for_level(cfg)
    if not pool:
        toast("No words for this level.")
        state.set_screen(Screen.MENU)
        return

    stats = RunStats()
    streak = 0
    best_streak = 0
    clock = Stopwatch()
    clock.start()

    toast(f"Focus Practice: Level {cfg.id} — {cfg.name}. 'q' to exit. {HELP_TEXT}")

    # deterministic rotation through pool (helps memorize patterns)
    idx = 0
    target = pool[idx]
    prev: Optional[str] = None

    while True:
        elapsed = int(clock.seconds)
        stats.wpm_live = wpm(stats.chars_ok, max(clock.seconds, 1e-6))
        update_accuracy(stats)
        render_hud_practice(elapsed, stats.wpm_live, stats.accuracy, streak)

        try:
            user = input(f"Type: {target}\n> ")
        except (KeyboardInterrupt, EOFError):
            toast("⏹ Leaving practice.")
            break

        raw = user.strip()
        cmd = raw.lower()

        if cmd in (":help","help",":h","h"):
            toast(HELP_TEXT); continue
        if cmd in (":q","q","quit","exit"):
            toast("↩ Back to menu."); break
        if cmd in (":skip",":s","skip","s"):
            streak = 0
            prev = target
            idx = (idx + 1) % len(pool)
            target = pool[idx]
            if target == prev:
                idx = (idx + 1) % len(pool)
                target = pool[idx]
            continue
        if raw == "":
            toast("(Empty input) " + HELP_TEXT); continue

        stats.words_total += 1
        if raw == target:
            stats.words_ok += 1
            stats.chars_ok += len(target)
            streak += 1
            best_streak = max(best_streak, streak)
            prev = target
            idx = (idx + 1) % len(pool)
            target = pool[idx]
            if target == prev:
                idx = (idx + 1) % len(pool)
                target = pool[idx]
        else:
            stats.typos += 1  # <-- add this
            streak = 0
            toast("Mismatch. Tip: lock the first 3 letters cleanly.")

    clock.stop()
    final_seconds = max(clock.seconds, 1e-6)
    final_wpm = wpm(stats.chars_ok, final_seconds)
    update_accuracy(stats)

    results_card(f"Practice L{cfg.id} — {cfg.name}", stats, final_wpm)
    toast(f"Best streak: {best_streak}")
    toast("(Press Enter to return to menu)")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    state.set_screen(Screen.MENU)
