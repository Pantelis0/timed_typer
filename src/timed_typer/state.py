"""
Central state machine for screen flow.
"""
from enum import Enum, auto
from enum import Enum, auto

class Screen(Enum):
    MENU = auto()
    LEVEL_SELECT = auto()
    PLAY = auto()
    RESULTS = auto()
    PRACTICE = auto()
    PRACTICE_LEVEL = auto()
    SELFTEST = auto()
    DEMO = auto()
    REPORT = auto()
    ABOUT = auto()
    QUIT = auto()

# src/timed_typer/state.py
from enum import Enum, auto

class GameState:
    def __init__(self) -> None:
        self.screen = Screen.MENU
        self.current_level = 1
        self.running = True
        self.stats = {}

    def set_screen(self, next_screen: Screen) -> None:
        self.screen = next_screen




