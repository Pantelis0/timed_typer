"""
Scoring, accuracy, streaks, pass/fail checks.
"""
from dataclasses import dataclass
from .levels import LevelConfig

@dataclass
class RunStats:
    words_total: int = 0
    words_ok: int = 0
    typos: int = 0
    chars_ok: int = 0
    wpm_live: float = 0.0
    accuracy: float = 1.0

def update_accuracy(stats: RunStats) -> None:
    attempts = stats.words_total + stats.typos
    stats.accuracy = (stats.words_ok / attempts) if attempts else 1.0

def passed_level(cfg: LevelConfig, stats: RunStats, wpm_final: float) -> bool:
    return stats.accuracy >= cfg.min_accuracy and wpm_final >= cfg.target_wpm
