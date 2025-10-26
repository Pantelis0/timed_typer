"""
demo.py — auto-play visualization: shows the real HUD progressing without user input
"""
from __future__ import annotations
import random

from .state import GameState, Screen
from .levels import get_level
from .words import words_for_level
from .timing import wpm as wpm_calc
from .scoring import RunStats, update_accuracy
from .ui_console import render_hud, toast, results_card


def _simulate_run(level_id: int, speed_factor: float, acc_target: float) -> None:
    """
    Simulate a level run without blocking/sleeping.
    - speed_factor: 1.0 = roughly target WPM, >1.0 faster, <1.0 slower
    - acc_target: probability of a correct word (0.0..1.0)
    We "advance" time mathematically and print HUD frames to visualize progress.
    """
    cfg = get_level(level_id)
    # pick enough words for the whole time budget
    minutes = cfg.time_budget_s / 60.0
    approx_words = max(20, int(cfg.target_wpm * minutes * 1.4))
    seq = words_for_level(cfg, approx_words)

    stats = RunStats()
    elapsed = 0.0  # synthetic time in seconds
    chars_ok = 0

    # Derive simulated WPM target from config and speed_factor
    target_wpm = max(1.0, cfg.target_wpm * speed_factor)

    i = 0
    while elapsed < cfg.time_budget_s and i < len(seq):
        # Compute how long it would take to type the next word at target_wpm.
        word = seq[i]
        word_chars = len(word)
        # seconds = (chars/5) * 60 / WPM
        sec_per_word = (word_chars / 5.0) * (60.0 / target_wpm)

        # Decide if this attempt is correct based on acc_target
        is_ok = (random.random() <= acc_target)
        stats.words_total += 1

        if is_ok:
            stats.words_ok += 1
            chars_ok += word_chars
            i += 1
        else:
            stats.typos += 1
            # stay on same word (like real game), but we still advance some time
            # you could optionally nudge to next word on typo: i += 1

        elapsed += sec_per_word

        # Live HUD (uses remaining time like normal play)
        stats.chars_ok = chars_ok
        stats.wpm_live = wpm_calc(chars_ok, max(elapsed, 1e-6))
        update_accuracy(stats)
        remaining = max(0, int(cfg.time_budget_s - elapsed))
        render_hud(cfg.name, remaining, stats.wpm_live, stats.accuracy,
                   streak=0)  # we don't simulate streaks here

    # Final numbers
    final_wpm = wpm_calc(chars_ok, max(elapsed, 1e-6))
    update_accuracy(stats)
    results_card(f"DEMO — {cfg.name}", stats, final_wpm)

    # Simple pass/fail message vs actual level targets
    need_wpm = float(cfg.target_wpm)
    need_acc = int(cfg.min_accuracy * 100)
    have_acc = int(stats.accuracy * 100)
    EPS = 1e-9  # tolerate float rounding
    if (stats.accuracy + EPS) >= cfg.min_accuracy and (final_wpm + EPS) >= need_wpm:
        toast("✅ Demo meets the level targets.")
    else:
        toast(f"❌ Demo below target. Need ≥{need_wpm:.0f} WPM & ≥{need_acc}% acc. "
              f"(Had {final_wpm:.1f} WPM, {have_acc}% acc.)")

    toast("(Press Enter to return to menu)")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass


def run_demo(state: GameState) -> None:
    print("\n-- Demo (auto) --")
    lvl = input("Choose level 1-5 (or 'q' to cancel): ").strip().lower()
    if lvl in ("q", "quit", "exit"):
        state.set_screen(Screen.MENU)
        return
    if not lvl.isdigit() or not (1 <= int(lvl) <= 5):
        toast("Invalid level.")
        state.set_screen(Screen.MENU)
        return
    level_id = int(lvl)

    try:
        speed = float(input("Speed factor (1.0=target WPM, 1.2=faster, 0.8=slower) [1.0]: ") or "1.0")
    except ValueError:
        speed = 1.0
    try:
        acc = float(input("Accuracy target (0.0..1.0) [0.90]: ") or "0.90")
    except ValueError:
        acc = 0.90
    acc = max(0.0, min(1.0, acc))

    _simulate_run(level_id=level_id, speed_factor=speed, acc_target=acc)
    state.set_screen(Screen.MENU)
