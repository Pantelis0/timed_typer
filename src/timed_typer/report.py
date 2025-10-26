from __future__ import annotations
from pathlib import Path
from datetime import datetime

from .levels import LEVELS
from .storage import get_store
from .ui_console import toast

# Optional: charts (Matplotlib). If missing, we just skip images.
def _maybe_make_charts(out_dir: Path, pbs: dict) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []

    names, wpm_vals, acc_vals, wpm_targets, acc_targets = [], [], [], [], []
    for lvl, cfg in LEVELS.items():
        names.append(cfg.name)
        pb = pbs.get(str(lvl))
        wpm_vals.append(pb["wpm"] if pb else 0.0)
        acc_vals.append((pb["accuracy"] * 100.0) if pb else 0.0)
        wpm_targets.append(cfg.target_wpm)
        acc_targets.append(cfg.min_accuracy * 100.0)

    paths = []

    # WPM chart
    plt.figure()
    plt.bar(names, wpm_vals, label="PB WPM")
    plt.plot(names, wpm_targets, marker="o", label="Target WPM")
    plt.legend()
    wpm_png = out_dir / "report_wpm.png"
    plt.savefig(wpm_png, bbox_inches="tight")
    plt.close()
    paths.append(str(wpm_png.name))

    # Accuracy chart
    plt.figure()
    plt.bar(names, acc_vals, label="PB Acc (%)")
    plt.plot(names, acc_targets, marker="o", label="Target Acc (%)")
    plt.legend()
    acc_png = out_dir / "report_acc.png"
    plt.savefig(acc_png, bbox_inches="tight")
    plt.close()
    paths.append(str(acc_png.name))

    return paths

def _advice_lines(pbs: dict) -> list[str]:
    lines = []
    from .levels import get_level
    worst_gap = None
    for lvl in sorted(LEVELS.keys()):
        cfg = get_level(lvl)
        pb = pbs.get(str(lvl))
        if not pb:
            lines.append(f"- **{cfg.name}**: No PB yet. Run a `--demo {lvl} 1.1 0.9` to preview pacing.")
            continue
        gap_wpm = cfg.target_wpm - pb["wpm"]
        gap_acc = (cfg.min_accuracy*100) - (pb["accuracy"]*100)
        tips = []
        if gap_wpm > 0.5:
            tips.append(f"+{gap_wpm:.1f} WPM")
        if gap_acc > 0.5:
            tips.append(f"+{gap_acc:.0f}% acc")
        if tips:
            lines.append(f"- **{cfg.name}**: needs {' & '.join(tips)} — focus on short tokens, nail first 3 letters.")
            if worst_gap is None or gap_wpm + (gap_acc/4) > worst_gap[0]:
                worst_gap = (gap_wpm + (gap_acc/4), cfg.name)
        else:
            lines.append(f"- **{cfg.name}**: ✅ Meets target. Maintain consistency.")
    if worst_gap:
        lines.append(f"\n**Priority focus:** {worst_gap[1]} (biggest combined gap).")
    return lines

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
    lines.append("## Overview")
    lines.append("- Console typing game about network operations (Ping → Traceroute → DNS → HTTP → Firewall + secret).")
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

def export_report_to_project_root() -> Path:
    out = Path.cwd() / "REPORT.md"
    generate_report_md(out)
    return out
