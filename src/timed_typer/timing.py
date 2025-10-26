"""
Timing utilities and WPM calculation.
"""
import time

class Stopwatch:
    def __init__(self) -> None:
        self._start = None
        self._elapsed = 0.0

    def start(self) -> None:
        if self._start is None:
            self._start = time.perf_counter()

    def stop(self) -> None:
        if self._start is not None:
            self._elapsed += time.perf_counter() - self._start
            self._start = None

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0

    @property
    def seconds(self) -> float:
        if self._start is None:
            return self._elapsed
        return self._elapsed + (time.perf_counter() - self._start)

def wpm(chars_typed: int, seconds: float) -> float:
    # standard: 5 chars per word
    if seconds <= 0:
        return 0.0
    return (chars_typed / 5.0) * (60.0 / seconds)
