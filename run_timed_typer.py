import sys
from timed_typer.app import main as app_main

def _teacher_batch() -> None:
    # Run a short demo for levels 1..5, then export report, print quick advice.
    from timed_typer.demo import _simulate_run
    from timed_typer.report import export_report_to_project_root
    from timed_typer.levels import LEVELS, get_level
    from timed_typer.storage import get_store
    print("== Teacher batch: demos + report ==")
    for lvl in range(1, 6):
        print(f"-- Demo L{lvl} ({LEVELS[lvl].name}) @1.05x, acc 0.92 --")
        _simulate_run(level_id=lvl, speed_factor=1.05, acc_target=0.92)
    path = export_report_to_project_root()
    print(f"\nReport written: {path}")

    # Quick advice based on PB gaps
    store = get_store()
    pbs = store.get("pbs", {})
    print("\n== Coaching Advice ==")
    for lvl in range(1, 6):
        cfg = get_level(lvl)
        pb = pbs.get(str(lvl))
        if not pb:
            print(f"- {cfg.name}: No PB recorded yet.")
            continue
        gap_wpm = cfg.target_wpm - pb["wpm"]
        gap_acc = (cfg.min_accuracy*100) - (pb["accuracy"]*100)
        need = []
        if gap_wpm > 0.5: need.append(f"+{gap_wpm:.1f} WPM")
        if gap_acc > 0.5: need.append(f"+{gap_acc:.0f}% Acc")
        msg = "OK" if not need else ("Needs " + " & ".join(need))
        print(f"- {cfg.name}: {msg}")

def _cli():
    if len(sys.argv) <= 1:
        return False  # menu

    cmd = sys.argv[1].lower()

    if cmd in ("--selftest", "-t"):
        from timed_typer.state import GameState
        from timed_typer.selftest import run_self_tests
        s = GameState()
        run_self_tests(s)
        return True

    if cmd in ("--report", "-r"):
        from timed_typer.report import export_report_to_project_root
        path = export_report_to_project_root()
        print(f"Report written to: {path}")
        return True

    if cmd in ("--demo", "-d"):
        from timed_typer.demo import _simulate_run
        from timed_typer.levels import LEVELS
        try:
            level = int(sys.argv[2])
        except Exception:
            print("Usage: --demo <level 1-5> [speed=1.0] [acc=0.90]")
            return True
        if level not in LEVELS:
            print("Error: level must be 1..5")
            return True
        speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        acc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.90
        speed = 1.0 if speed <= 0 else speed
        acc = 0.0 if acc < 0 else (1.0 if acc > 1 else acc)
        _simulate_run(level_id=level, speed_factor=speed, acc_target=acc)
        return True

    if cmd in ("--teacher", "--batch"):
        _teacher_batch()
        return True

    return False

if __name__ == "__main__":
    if not _cli():
        app_main()
