from __future__ import annotations
from .state import GameState, Screen

def about_screen(state: GameState) -> None:
    print("\n===== About =====")
    print("Timed Typer — Network Ops (Python)")
    print("Version: 1.0")
    print("Author: Pantelis Kefalas")
    print("License: MIT")
    print("Tech: Python 3.13, Colorama, PyInstaller")
    print("\n(Press Enter to return to menu)")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    state.set_screen(Screen.MENU)
