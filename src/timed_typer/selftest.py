"""
selftest.py — automated, non-interactive checks for the game
(derives targets from level config so PASS/FAIL are accurate)
"""
from __future__ import annotations
from math import ceil
from typing import List, Tuple

from .state import GameState, Screen
from .levels import get_level
from .words import words_for_level
from .timing import wpm as wpm_calc
from .scoring import RunStats, update_accuracy, passed_level
from .storage import save_pb
from .ui_console import toast, results_card


def _assert_no_immediate_repeats(words: List[str]) -> tuple[bool, int]:
    for i in range(1, len(words)):
        if words[i] == words[i - 1]:
            return (False, i)
    return (True, -1)


def _calc_words_ok_for_accuracy(words_total: int, target_acc: float) -> Tuple[int, int]:
    """
    We simulate attempts with 'words_total' entries, where we count typos as (words_total - words_ok).
    Accuracy formula in our game: accuracy = words_ok / (words_total + typos) = words_ok / (2*words_total - words_ok).
    Solve for words_ok given target_acc 'a':
        words_ok * (1 + a) = 2 * a * words_total  => words_ok = ceil( (2*a*words_total) / (1 + a) )
    Then typos = words_total - words_ok (never negative).
    """
    a = max(0.0, min(0.999, target_acc))
    words_ok = ceil((2 * a * words_total) / (1.0 + a))
    words_ok = max(0, min(words_total, words_ok))
    typos = max(0, words_total - words_ok)
    return words_ok, typos


def _simulate_level_with_targets(level_id: int, wpm_margin: float, acc_margin: float) -> tuple[RunStats, float, bool]:
    """
    Simulate a run based on the level's true targets + margins.
    wpm_margin: how much above/below the target_wpm we aim (-5 for fail, +2 for pass, etc.)
    acc_margin: how much above the min_accuracy we aim (e.g., +0.03)
    """
    cfg = get_level(level_id)
    sample = words_for_level(cfg, 40)  # just to compute realistic chars_ok

    # Use a fixed words_total for stable numbers in results cards
    words_total = 20
    target_wpm = max(1.0, cfg.target_wpm + wpm_margin)
    target_acc = max(0.0, min(0.99, cfg.min_accuracy + acc_margin))

    # Calculate words_ok/typos to achieve target_acc under our accuracy formula
    words_ok, typos = _calc_words_ok_for_accuracy(words_total, target_acc)

    # chars from the first 'words_ok' correct words (approx)
    chars_ok = sum(len(w) for w in sample[:words_ok]) or 1

    # Choose seconds so WPM matches target_wpm:
    # WPM = (chars_ok/5) * (60/seconds)  => seconds = (chars_ok/5) * 60 / target_wpm
    seconds = ((chars_ok / 5.0) * 60.0) / max(target_wpm, 0.1)

    # Build stats and evaluate
    stats = RunStats(words_total=words_total, words_ok=words_ok, typos=typos, chars_ok=chars_ok)
    update_accuracy(stats)
    final_wpm = wpm_calc(chars_ok, seconds)
    did_pass = passed_level(cfg, stats, final_wpm)

    # Show a results card for visibility
    results_card(f"SELFTEST L{cfg.id} — {cfg.name}", stats, final_wpm)
    if did_pass:
        toast("✅ Would pass. (Saving PB & unlocking for realism.)")
        save_pb(cfg.id, final_wpm, stats.accuracy)
    else:
        toast("❌ Would NOT pass. (Fail path OK)")
    print("")  # spacing

    return stats, final_wpm, did_pass


def run_self_tests(state: GameState) -> None:
    print("\n=== SELF-TEST (auto) ===")

    # ---- Test A: no immediate repeats on each level ----
    print("\n[TEST A] Word generation: no immediate duplicate words")
    all_ok = True
    for lvl in range(1, 6):
        cfg = get_level(lvl)
        seq = words_for_level(cfg, 60)
        ok, idx = _assert_no_immediate_repeats(seq)
        mark = "PASS" if ok else f"FAIL (dup at i={idx}: '{seq[idx]}')"
        print(f"  Level {lvl} — {cfg.name}: {mark}")
        all_ok = all_ok and ok
    if not all_ok:
        toast("⚠ Word repeat test found issues.")
    else:
        toast("👍 No immediate repeats across levels.")
    print("")

    # ---- Test B: Level 1 PASS (slightly above both targets) ----
    print("[TEST B] Simulated Level 1 — expect PASS (targets + small margins)")
    _simulate_level_with_targets(level_id=1, wpm_margin=+2.0, acc_margin=+0.03)

    # ---- Test C: Level 2 PASS (targets + small margins) ----
    print("[TEST C] Simulated Level 2 — expect PASS (targets + small margins)")
    _simulate_level_with_targets(level_id=2, wpm_margin=+2.0, acc_margin=+0.03)

    # ---- Test D: Level 3 FAIL (WPM under target; accuracy fine) ----
    print("[TEST D] Simulated Level 3 — expect FAIL (under target WPM)")
    _simulate_level_with_targets(level_id=3, wpm_margin=-5.0, acc_margin=+0.05)

    toast("(Self-tests complete) Press Enter to return to menu")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    state.set_screen(Screen.MENU)
