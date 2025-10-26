"""
Level configuration and helpers.
Each level sets targets and word rules.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class LevelConfig:
    id: int
    name: str
    min_accuracy: float   # 0..1
    target_wpm: int
    time_budget_s: int
    allow_symbols: bool = False
    max_word_len: int = 6

LEVELS = {
    1: LevelConfig(1, "Ping",        0.80, 12, 45, False, 4),
    2: LevelConfig(2, "Traceroute",  0.82, 17, 45, True,  6),  # was 18
    3: LevelConfig(3, "DNS",         0.85, 25, 60, True,  7),
    4: LevelConfig(4, "HTTP",        0.87, 32, 60, True,  8),
    5: LevelConfig(5, "Firewall",    0.90, 40, 75, True, 10),
}


def get_level(n: int) -> LevelConfig:
    return LEVELS[n]
