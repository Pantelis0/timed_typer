"""
report.py — builds the turn-in report with Q1–Q5 and writes REPORT.md
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from .storage import load_store
from .levels import get_level


def _build_report_text(store: dict) -> str:
    """
    Build markdown answering the required questions:

    Q1. Creative goals
    Q2. Five levels + transitions
    Q3. Progress & final success feedback
    Q4. New functions beyond skeleton
    Q5. Code readability & style
    """

    # pull persistent data from the save system
    unlocks = store.get("unlocks", {})
    pbs = store.get("pbs", {})

    # the game is designed around 5 missions/levels
    level_ids = [1, 2, 3, 4, 5]

    # ---------- helper blocks that generate report sections ----------

    def level_status_block() -> list[str]:
        """
        For Q2: show each level with:
        - UNLOCKED or LOCKED
        - PB (WPM and accuracy %)
        - Level name (Ping / Traceroute / DNS / HTTP / Firewall)
        """
        lines: list[str] = []
        for lvl in level_ids:
            # ex: cfg.name == "Ping", "Traceroute", etc.
            try:
                cfg = get_level(lvl)
                lvl_name = cfg.name
            except Exception:
                lvl_name = f"Level {lvl}"

            is_open = bool(unlocks.get(str(lvl), False))
            status = "UNLOCKED" if is_open else "LOCKED"

            pb = pbs.get(str(lvl))
            if pb:
                wpm_val = pb.get("wpm", 0.0)
                acc_ratio = pb.get("accuracy", 0.0)
                acc_pct = acc_ratio * 100.0
                pb_str = f"{wpm_val:.1f} WPM @ {acc_pct:.1f}% acc"
            else:
                pb_str = "PB: —"

            lines.append(f"- {lvl}. {lvl_name} — {status} — {pb_str}")
        return lines

    def progress_block() -> list[str]:
        """
        For Q3: summarize what the player has actually achieved.
        We consider a level "cleared" if:
          - beating level N unlocked level N+1, OR
          - for the last level, we at least have a PB recorded.
        Also highlight the best run overall.
        """
        lines: list[str] = []

        cleared_levels: list[int] = []
        for lvl in level_ids:
            if lvl < max(level_ids):
                # cleared if next level is unlocked
                nxt = str(lvl + 1)
                if unlocks.get(nxt, False):
                    cleared_levels.append(lvl)
            else:
                # last level: cleared if we have *any* PB saved
                if pbs.get(str(lvl)):
                    cleared_levels.append(lvl)

        if cleared_levels:
            cleared_str = ", ".join(str(x) for x in cleared_levels)
            lines.append(f"- Cleared levels so far: {cleared_str}")
        else:
            lines.append("- Cleared levels so far: none yet")

        # strongest performance = PB with highest WPM
        best_lvl = None
        best_lvl_name = ""
        best_wpm = 0.0
        best_acc_pct = 0.0

        for lvl_str, pb in pbs.items():
            try:
                lvl_int = int(lvl_str)
            except ValueError:
                continue

            wpm_val = pb.get("wpm", 0.0)
            acc_ratio = pb.get("accuracy", 0.0)
            acc_pct = acc_ratio * 100.0

            if wpm_val > best_wpm:
                best_wpm = wpm_val
                best_acc_pct = acc_pct
                try:
                    cfg = get_level(lvl_int)
                    best_lvl_name = cfg.name
                except Exception:
                    best_lvl_name = f"Level {lvl_int}"
                best_lvl = lvl_int

        if best_lvl is not None:
            lines.append(
                f"- Strongest performance: Level {best_lvl} "
                f"({best_lvl_name}) at {best_wpm:.1f} WPM / "
                f"{best_acc_pct:.1f}% accuracy"
            )
        else:
            lines.append("- Strongest performance: (no PBs yet)")

        # describe the feedback loop at the end of a run
        lines.append(
            "- After every run, the game prints feedback:\n"
            "  * ✅ \"Level passed! Next level unlocked.\" when you hit both\n"
            "    target WPM and accuracy without quitting.\n"
            "  * Otherwise it tells you why you failed (too slow vs too many\n"
            "    typos) and gives a tip, e.g. 'Slow down slightly' or 'Push\n"
            "    speed on short words.'"
        )
        return lines

    # ---------- assemble the final markdown body ----------

    lines: list[str] = []

    # Title + timestamp
    lines.append("Report Notes (Timed Typer)")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    # Q1
    lines.append("## Q1. Creative goals")
    lines.append(
        "- Make a high-pressure typing trainer that feels like doing real\n"
        "  network ops work (Ping / Traceroute / DNS / HTTP / Firewall),\n"
        "  not kiddie 'the quick brown fox' drills."
    )
    lines.append(
        "- Force the player to enter short technical strings and symbols\n"
        "  accurately under a live countdown, to build speed *and* accuracy."
    )
    lines.append(
        "- Give it a vibe: terminal HUD, streak counter, live WPM, etc.,\n"
        "  so each level feels like a mission instead of homework."
    )
    lines.append("")

    # Q2
    lines.append("## Q2. Five levels + transitions")
    lines.append(
        "- The game has 5 missions, escalating from Ping to Firewall.\n"
        "  Each mission has its own wordlist and accuracy/WPM target."
    )
    lines.append(
        "- When you pass a mission (hit target WPM and accuracy without\n"
        "  quitting early), the next mission unlocks automatically."
    )
    lines.append("- Current status:")
    lines.extend(level_status_block())
    lines.append(
        "- The Level Select menu shows which levels are UNLOCKED vs LOCKED\n"
        "  and displays your PB for each one."
    )
    lines.append("")

    # Q3
    lines.append("## Q3. Progress & final success feedback")
    lines.extend(progress_block())
    lines.append("")

    # Q4
    lines.append("## Q4. New functions beyond skeleton")
    lines.append(
        "- `storage.py`: full save system. It writes a `profile.json` file\n"
        "  with unlocked levels, PBs (best WPM + accuracy ratio), and\n"
        "  settings. It also does migration: older PBs stored as `acc`\n"
        "  get upgraded to `accuracy` automatically so the menus don't\n"
        "  crash on missing keys.\n"
        "  (Catching missing keys and mismatched names is important:\n"
        "   otherwise you get `KeyError` or `ImportError` when modules try\n"
        "   to access data that isn't there.)"  # see typical causes of ImportError/KeyError :contentReference[oaicite:2]{index=2}
    )
    lines.append(
        "- `GameState.after_level_finish(...)`: called right after you\n"
        "  finish a run. It:\n"
        "    * records PB for that level,\n"
        "    * unlocks the next level if you passed,\n"
        "    * saves to disk,\n"
        "    * refreshes the in-memory unlocked/PBs for the menus."
    )
    lines.append(
        "- Level Select reads the save and shows:\n"
        "    * PB: 32.1 WPM, 97%\n"
        "    * LOCKED/UNLOCKED state\n"
        "  This UI is proof that persistence actually works."
    )
    lines.append(
        "- Export Report (this file): menu option [7] calls\n"
        "  `export_report_to_project_root()`, which turns the runtime\n"
        "  data into a Markdown hand-in. That’s basically a dev tool /\n"
        "  teacher tool wired directly into the game."
    )
    lines.append("")

    # Q5
    lines.append("## Q5. Code readability & style")
    lines.append(
        "- The code is split into focused modules:\n"
        "  * `state.py` = game state machine + screen routing\n"
        "  * `game.py`  = main loop that switches screens\n"
        "  * `menu.py`  = title menu + level select menu\n"
        "  * `play.py`  = the live typing loop with timer, streak,\n"
        "                 WPM/accuracy tracking, pass/fail logic\n"
        "  * `storage.py` = persistence helpers (`record_pb`,\n"
        "                   `unlock_next_level`, etc.)\n"
        "  * `report.py`  = generates this structured Q&A Markdown"
    )
    lines.append(
        "- We fixed circular-import crashes by cleaning up imports so\n"
        "  modules don’t import each other while they’re still loading.\n"
        "  That 'partially initialized module' ImportError is classic\n"
        "  circular import in Python, and the fix is to stop modules from\n"
        "  importing each other at import time or to move shared logic\n"
        "  into a helper module. :contentReference[oaicite:3]{index=3}"
    )
    lines.append(
        "- We fixed NameError / ImportError issues in the menu and report\n"
        "  flow by making sure:\n"
        "    * functions we import (like `export_report_to_project_root`)\n"
        "      actually exist at the top level of the module, and\n"
        "    * variables we print (like `output_path`) are assigned before\n"
        "      we print them. In Python, referencing a name before it is\n"
        "      defined triggers `NameError`. :contentReference[oaicite:4]{index=4}"
    )
    lines.append(
        "- Player UX got attention: on fail you don't just 'lose', you get\n"
        "  targeted advice ('slow down for accuracy' vs 'push speed'),\n"
        "  which is part of the grading story for \"progress & feedback\"."
    )

    # final newline for nice file ending
    return "\n".join(lines) + "\n"


def export_report_to_project_root() -> Path:
    """
    Called by game.py when the player chooses [7] Export Report.

    1. Load the save (profile.json) via storage.load_store()
    2. Build the Q1–Q5 narrative
    3. Write REPORT.md in the current working directory
    4. Return that path so game.py can print it
    """
    store = load_store()
    text = _build_report_text(store)

    out_path = Path.cwd() / "REPORT.md"
    out_path.write_text(text, encoding="utf-8")
    return out_path
