"""
play.py — runs one level (console version) with commands, coaching, and safe interrupts
"""
from __future__ import annotations
import math
from typing import Tuple

from .state import GameState, Screen
from .levels import get_level
from .words import words_for_level, check_input
from .timing import Stopwatch, wpm
from .scoring import RunStats, update_accuracy, passed_level
from .storage import save_pb
from .ui_console import render_hud, toast, results_card


HELP_TEXT = "Commands: :skip/s, :q/menu/quit/exit, :help/h"


def play_level(state: GameState) -> None:
    """Run the currently selected level until time runs out or words are done."""
    cfg = get_level(state.current_level)

    # 1) Prepare runtime variables
    minutes = cfg.time_budget_s / 60.0
    target_words_count = max(20, math.ceil(cfg.target_wpm * minutes * 1.2))
    words = words_for_level(cfg, target_words_count)

    stats = RunStats()
    streak = 0
    interrupted = False  # track manual exits

    # 2) Start the clock
    clock = Stopwatch()
    clock.start()

    i = 0
    while clock.seconds < cfg.time_budget_s and i < len(words):
        remaining = max(0, int(cfg.time_budget_s - clock.seconds))
        # live WPM from chars_ok so far
        stats.wpm_live = wpm(stats.chars_ok, max(clock.seconds, 1e-6))
        update_accuracy(stats)
        render_hud(cfg.name, remaining, stats.wpm_live, stats.accuracy, streak)

        target = words[i]

        try:
            user = input(f"Type: {target}\n> ")
        except (KeyboardInterrupt, EOFError):
            toast("⏹ Interrupted — ending level.")
            interrupted = True
            break

        # If time expired while typing, break gracefully
        if clock.seconds >= cfg.time_budget_s:
            break

        raw = user.strip()
        cmd = raw.lower()

        # --- command handling (both with and without ':') ---
        if cmd in (":help", "help", ":h", "h"):
            toast(HELP_TEXT)
            continue
        if cmd in (":q", ":menu", "q", "menu", "quit", "exit"):
            toast("↩ Exiting to menu…")
            interrupted = True
            break
        if cmd in (":skip", ":s", "skip", "s"):
            stats.typos += 1
            streak = 0
            i += 1
            continue
        if raw == "":
            # empty input: gentle nudge, no penalty
            toast(f"(Empty input) {HELP_TEXT}")
            continue

        # --- normal evaluation ---
        stats.words_total += 1
        complete, first_err = _evaluate_attempt(target, raw)

        if complete:
            stats.words_ok += 1
            stats.chars_ok += len(target)
            streak += 1
            i += 1
        else:
            stats.typos += 1
            streak = 0
            if first_err >= 0:
                toast(f"Mismatch at pos {first_err+1}. Try again. ({HELP_TEXT})")

    # 3) Stop the clock, compute final metrics
    clock.stop()
    final_seconds = max(clock.seconds, 1e-6)
    final_wpm = wpm(stats.chars_ok, final_seconds)
    update_accuracy(stats)

    # 4) Results + persistence
    results_card(cfg.name, stats, final_wpm)

    passed = (not interrupted) and passed_level(cfg, stats, final_wpm)
    if passed:
        toast("✅ Level passed! Next level unlocked.")
        save_pb(state.current_level, final_wpm, stats.accuracy)
    elif interrupted:
        toast("📝 Run ended early (no unlock).")
    else:
        need_wpm = cfg.target_wpm
        need_acc = int(cfg.min_accuracy * 100)
        have_wpm = final_wpm
        have_acc = int(stats.accuracy * 100)
        toast(f"❌ Not passed. Need ≥{need_wpm} WPM and ≥{need_acc}% acc.")
        toast(f"   You had {have_wpm:.1f} WPM and {have_acc}% acc.")
        if have_acc < need_acc and have_wpm >= need_wpm - 2:
            toast("Tip: Slow down slightly; focus on clean first 3 letters.")
        elif have_wpm < need_wpm and have_acc >= need_acc - 2:
            toast("Tip: You’re accurate—push speed on short words.")
        else:
            toast("Tip: Aim for small streaks of 3–5 perfect words.")

    # 5) Pause here, then go back to MENU explicitly
    toast("(Press Enter to return to menu)")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    state.set_screen(Screen.MENU)
    return


def _evaluate_attempt(target: str, typed: str) -> Tuple[bool, int]:
    """
    Uses check_input(target, typed) but enforces: only exact matches count.
    Returns (complete_correct, first_error_index_or_minus1).
    """
    complete, first_err = check_input(target, typed)
    return complete, first_err
