"""
Word pools and generator per level (no immediate repeats).
"""
from __future__ import annotations
import random
from typing import List, Optional
from .levels import LevelConfig

# Base pool everyone can see (short, easy)
BASE_WORDS = [
    "net", "ping", "host", "path", "cache", "route", "trace", "domain",
    "resolve", "get", "post", "port", "allow", "deny", "udp", "tcp",
]

# Level-flavored extras
L1_PING = ["net", "ping", "host", "port", "tcp", "udp", "get", "post", "path", "deny"]
L2_TRACEROUTE = ["trace", "hop", "path", "route", "pkt", "ttl", "lat", "ms"]
L3_DNS = ["dns", "domain", "cache", "resolve", "ttl", "zone", "ns", "cname", "txt"]
L4_HTTP = ["http", "api", "/api", "GET", "POST", "200", "404", "json", "auth"]
L5_FIREWALL = ["rule", "allow", "deny", "proto", "src", "dst", "port=443", "allow[udp]", "deny[tcp]"]

SYMBOL_TOKENS = ["/api", "GET", "POST", "port=443", "allow[udp]", "deny[tcp]"]


def _pool_for_level(cfg: LevelConfig) -> List[str]:
    if cfg.id == 1:
        pool = L1_PING
    elif cfg.id == 2:
        pool = L2_TRACEROUTE + L1_PING
    elif cfg.id == 3:
        pool = L3_DNS + L1_PING
    elif cfg.id == 4:
        pool = L4_HTTP + L1_PING
    else:
        pool = L5_FIREWALL + L1_PING

    if cfg.allow_symbols:
        pool += SYMBOL_TOKENS

    # Enforce max length, but always keep symbol tokens
    filtered = [w for w in pool if len(w) <= cfg.max_word_len or w in SYMBOL_TOKENS]
    # Make sure we have variety
    if len(filtered) < 10:
        filtered = list(set(filtered + BASE_WORDS))
    return filtered


def _next_word(pool: List[str], prev: Optional[str]) -> str:
    """Pick a word different from the previous one (avoid immediate repeats)."""
    choice = random.choice(pool)
    if prev is None:
        return choice
    # simple re-roll
    tries = 0
    while choice == prev and tries < 10:
        choice = random.choice(pool)
        tries += 1
    return choice


def words_for_level(cfg: LevelConfig, n: int) -> List[str]:
    """
    Build a word sequence of length n with no immediate repeats.
    """
    pool = _pool_for_level(cfg)
    out: List[str] = []
    prev: Optional[str] = None
    for _ in range(n):
        w = _next_word(pool, prev)
        out.append(w)
        prev = w
    return out


def check_input(target: str, typed: str) -> tuple[bool, int]:
    """
    Returns (complete_correct, first_error_index or -1).
    complete_correct=True only if typed == target.
    """
    if not target.startswith(typed):
        for i, (a, b) in enumerate(zip(target, typed)):
            if a != b:
                return (False, i)
        return (False, len(typed))
    return (typed == target, -1)
