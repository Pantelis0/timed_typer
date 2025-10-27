from __future__ import annotations

from enum import Enum, auto
from . import storage


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


class GameState:
    def __init__(self) -> None:
        # which screen are we currently showing?
        self.screen = Screen.MENU

        # which level is selected for play() etc.
        self.current_level = 1

        # main loop flag
        self.running = True

        # last run stats (optional UI use)
        self.stats = {}

        # persistent profile data (PBs, unlocks, settings)
        # this is loaded from JSON on disk
        self.store = storage.load_store()
        self.unlocked = self.store.get("unlocks", {})
        self.pbs = self.store.get("pbs", {})

    def set_screen(self, next_screen: Screen) -> None:
        self.screen = next_screen

    def level_is_unlocked(self, lvl: int) -> bool:
        # ask storage layer if this level is unlocked in the save file
        return bool(self.store.get("unlocks", {}).get(str(lvl), False))

    def after_level_finish(
        self,
        level_id: int,
        wpm: float,
        acc: float,
        passed: bool,
    ) -> None:
        """
        Called once at the end of play_level().

        - record/update PB for this level
        - if passed, unlock the next level
        - save progress to disk
        - refresh our cached view (self.unlocked, self.pbs)
        """
        # update PB in memory
        storage.record_pb(self.store, level_id, wpm, acc)

        # unlock next level if the run "passed"
        if passed:
            storage.unlock_next_level(self.store, level_id)

        # write JSON save file safely
        storage.save_store(self.store)

        # refresh cached views for menus
        self.unlocked = self.store.get("unlocks", {})
        self.pbs = self.store.get("pbs", {})
