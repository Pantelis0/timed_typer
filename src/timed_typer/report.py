from pathlib import Path

from src.timed_typer.storage import get_store


def generate_report_md(out_path: Path) -> None:
    store = get_store()
    pbs = store.get("pbs", {})
    unlocks = store.get("unlocks", {})
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    out_dir = out_path.parent
    charts = _maybe_make_charts(out_dir, pbs)

    lines = []
    lines.append(f"# Timed Typer — Network Ops (Python)")
    lines.append(f"_Auto-generated: {now}_\n")

    # Q1. Creative goals
    lines.append("## Q1. Creative goals")
    lines.append("- The goal of this project is to create a **console-based typing game** themed around real networking operations (Ping, Traceroute, DNS, HTTP, Firewall).")
    lines.append("- It combines typing speed/accuracy training with a narrative of network commands, offering skills practice in a fun format.")
    lines.append("")

    # Q2. Five levels + transitions
    lines.append("## Q2. Five levels + transitions")
    lines.append("The game has **five core levels**, each unlocking after the previous is passed. The user must meet a target WPM and minimum accuracy to advance.")
    for lvl, cfg in LEVELS.items():
        lines.append(f"- Level {cfg.id} — {cfg.name}: target {cfg.target_wpm} WPM, min accuracy {int(cfg.min_accuracy*100)}%, time budget {cfg.time_budget_s}s.")
    lines.append("Transitions: once a level is passed, the next level is unlocked and becomes selectable via the Level Select screen.")
    lines.append("")

    # Q3. Progress & final success feedback
    lines.append("## Q3. Progress & final success feedback")
    lines.append("- During play: a live HUD shows current WPM, accuracy, streak and remaining time.")
    lines.append("- At the end of each run: a Results card displays final WPM, accuracy, #OK vs #All, typos, and whether the level was passed.")
    lines.append("- On success: the system unlocks the next level, saves a PB if achieved, and gives a toast message like “✅ Level passed! Next level unlocked.”")
    lines.append("")

    # Q4. New functions beyond skeleton
    lines.append("## Q4. New functions beyond skeleton")
    lines.append("- Save system (persistent PBs and unlocks) via JSON storage.")
    lines.append("- Demo mode (`--demo`) that simulates gameplay automatically for verification or demonstration purposes.")
    lines.append("- Self-Test mode (`--selftest`) which runs quick automated checks (word-generation, pass/fail paths) without manual typing.")
    lines.append("- Report export (`--report`) that generates this `REPORT.md`, includes charts (if matplotlib available) and coaching advice.")
    lines.append("- About screen and menu enhancements for usability and presentation.")
    lines.append("")

    # Q5. Code readability & style
    lines.append("## Q5. Code readability & style")
    lines.append("- The codebase is modular: `app.py` (entrypoint), `menu.py`, `game.py`, `play.py`, `storage.py`, `levels.py`, `report.py`, `ui_console.py`, etc.")
    lines.append("- Functions are kept small and focused; logic is separated from UI. Naming is consistent, docstrings used where helpful.")
    lines.append("- Dependencies are minimal (Python standard library + `colorama` + optional `matplotlib`).")
    lines.append("- Packaging via `pyinstaller` enables a single-file executable.")
    lines.append("")

    # Existing Overview & data
    lines.append("## Overview")
    lines.append("- Console typing game about network operations (Ping → Traceroute → DNS → HTTP → Firewall).")
    lines.append("- Modes: Self-tests, Auto Demo, Practice, Focus Practice, Exportable Report.\n")

    lines.append("## Level Targets & Personal Bests")
    lines.append("| Level | Name | Min Accuracy | Target WPM | Time (s) | PB WPM | PB Acc | Unlocked |")
    lines.append("|------:|------|--------------:|-----------:|---------:|-------:|-------:|:--------:|")
    for lvl, cfg in LEVELS.items():
        pb = pbs.get(str(lvl))
        pb_wpm = f"{pb['wpm']:.1f}" if pb else "-"
        pb_acc = f"{pb['accuracy']*100:.0f}%" if pb else "-"
        unlocked = "✅" if unlocks.get(str(lvl), lvl == 1) else "❌"
        lines.append(f"| {cfg.id} | {cfg.name} | {int(cfg.min_accuracy*100)}% | {cfg.target_wpm} | {cfg.time_budget_s} | {pb_wpm} | {pb_acc} | {unlocked} |")
    lines.append("")

    if charts:
        lines.append("## Charts")
        for name in charts:
            lines.append(f"![{name}]({name})")
        lines.append("")

    lines.append("## Coaching Advice")
    lines += _advice_lines(pbs)
    lines.append("")

    lines.append("## How to run")
    lines.append("```bash")
    lines.append("py -m timed_typer.app")
    lines.append("```")
    lines.append("- Headless: `TimedTyper.exe --selftest`, `--demo 3 1.2 0.9`, `--report`")

    out_path.write_text("\n".join(lines), encoding="utf-8")
