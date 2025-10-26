"""
Game loop orchestrator: transitions, timers, word dispatch.
"""
from .state import GameState, Screen
from .menu import title_menu, level_select
from .play import play_level
from .practice import practice_mode

from .practice_level import practice_level

from .selftest import run_self_tests

from .demo import run_demo

from .report import export_report_to_project_root
from .about import about_screen  # <-- add this import

def run_game() -> None:
    state = GameState()
    while state.running:
        if state.screen == Screen.MENU:
            title_menu(state)
        elif state.screen == Screen.LEVEL_SELECT:
            level_select(state)
        elif state.screen == Screen.PLAY:
            play_level(state)
        elif state.screen == Screen.PRACTICE:
            practice_mode(state)
        elif state.screen == Screen.PRACTICE_LEVEL:
            practice_level(state)
        elif state.screen == Screen.SELFTEST:
            run_self_tests(state)
        elif state.screen == Screen.DEMO:
            run_demo(state)
        elif state.screen == Screen.REPORT:
            path = export_report_to_project_root()
            print(f"\nReport written to: {path}")
            print("(Press Enter to return to menu)")
            try: input()
            except (KeyboardInterrupt, EOFError): pass
            state.set_screen(Screen.MENU)
        elif state.screen == Screen.ABOUT:        # <-- handle About
            about_screen(state)
        elif state.screen == Screen.RESULTS:
            state.set_screen(Screen.MENU)
        elif state.screen == Screen.QUIT:
            state.running = False

