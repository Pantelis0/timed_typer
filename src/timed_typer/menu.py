"""
Console menus: title + level select.
Keep UI text here so logic stays clean.
"""
from .state import GameState, Screen

def title_menu(state: GameState) -> None:
    print("\n=== Timed Typer — Network Ops ===")
    print("[1] Start")
    print("[2] Level Select")
    print("[3] Practice Mode")
    print("[4] Focus Practice (by Level)")
    print("[5] Self-Test (auto)")
    print("[6] Demo (auto)")
    print("[7] Export Report")
    print("[A] About")              # <-- show About
    print("[Q] Quit")
    choice = input("> ").strip().lower()

    if choice == "1":
        state.set_screen(Screen.PLAY)
    elif choice == "2":
        state.set_screen(Screen.LEVEL_SELECT)
    elif choice == "3":
        state.set_screen(Screen.PRACTICE)
    elif choice == "4":
        state.set_screen(Screen.PRACTICE_LEVEL)
    elif choice == "5":
        state.set_screen(Screen.SELFTEST)
    elif choice == "6":
        state.set_screen(Screen.DEMO)
    elif choice == "7":
        state.set_screen(Screen.REPORT)
    elif choice == "a":
        state.set_screen(Screen.ABOUT)  # <-- route About
    elif choice == "q":
        state.set_screen(Screen.QUIT)





from .storage import is_unlocked, set_unlocked

from .levels import LEVELS
from .state import Screen
from .storage import is_unlocked
from .storage import get_store

def level_select(state):
    store = get_store()
    pbs = store.get("pbs", {})

    print("\n-- Select Level (1-5) --")
    for lid in range(1, 6):
        cfg = LEVELS[lid]
        unlocked = is_unlocked(lid)
        pb = pbs.get(str(lid))
        pb_str = f"  PB: {pb['wpm']:.1f} WPM, {int(pb['accuracy']*100)}%" if pb else ""
        lock_str = "" if unlocked else " (locked)"
        print(f"[{lid}] {cfg.name}{lock_str}{pb_str}")

    print("> ", end="")
    raw = input().strip().lower()
    if raw in ("q", "quit", "back"):
        state.set_screen(Screen.MENU)
        return
    if not raw.isdigit():
        print("Invalid choice.")
        return

    lid = int(raw)
    if lid not in LEVELS:
        print("Invalid level.")
        return
    if not is_unlocked(lid):
        print("Level locked.")
        return

    state.current_level = lid
    state.set_screen(Screen.PLAY)

