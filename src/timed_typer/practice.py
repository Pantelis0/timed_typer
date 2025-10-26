"""
practice.py — no-timer practice lane to build WPM (elapsed time + no immediate repeats)
"""
from __future__ import annotations
import random
from typing import Optional

from .state import GameState, Screen
from .timing import Stopwatch, wpm
from .scoring import RunStats, update_accuracy
from .ui_console import render_hud_practice, toast, results_card

HELP_TEXT = "Practice: type words fast. Commands: :skip/s, :q/quit/exit, :help/h"

# Short, speed-friendly words
PRACTICE_WORDS = [
    "net","host","ping","path","port","tcp","udp","get","post","deny","allow",
    "cache","route","trace","dns","api","http","ip","hop","pkt","vpn"
]

def next_word(prev: Optional[str]) -> str:
    """Pick a word different from the previous one (avoid immediate repeats)."""
    choice = random.choice(PRACTICE_WORDS)
    if prev is None:
        return choice
    # Re-roll until different (the list is small; this is fine)
    while choice == prev:
        choice = random.choice(PRACTICE_WORDS)
    return choice

def practice_mode(state: GameState) -> None:
    stats = RunStats()
    streak = 0
    best_streak = 0

    clock = Stopwatch()
    clock.start()

    toast("Practice mode ON — type fast; 'q' to exit. " + HELP_TEXT)

    prev_word: Optional[str] = None
    target = next_word(prev_word)

    while True:
        # Show live HUD with elapsed seconds
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

        # commands
        if cmd in (":help","help",":h","h"):
            toast(HELP_TEXT); continue
        if cmd in (":q","q","quit","exit"):
            toast("↩ Back to menu."); break
        if cmd in (":skip",":s","skip","s"):
            streak = 0
            prev_word = target
            target = next_word(prev_word)
            continue
        if raw == "":
            toast("(Empty input) " + HELP_TEXT); continue

        # evaluate (exact match)
        stats.words_total += 1
        if raw == target:
            stats.words_ok += 1
            stats.chars_ok += len(target)
            streak += 1
            best_streak = max(best_streak, streak)
            prev_word = target
            target = next_word(prev_word)
        else:
            stats.typos += 1  # <-- add this
            streak = 0
            toast("Mismatch. Tip: lock the first 3 letters cleanly.")

    # ===== end-of-session results =====
    clock.stop()
    final_seconds = max(clock.seconds, 1e-6)
    final_wpm = wpm(stats.chars_ok, final_seconds)
    update_accuracy(stats)

    results_card("Practice", stats, final_wpm)
    toast(f"Best streak: {best_streak}")
    toast("(Press Enter to return to menu)")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

    state.set_screen(Screen.MENU)
