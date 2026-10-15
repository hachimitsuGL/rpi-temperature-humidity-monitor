"""Thread-safe comfort thresholds shared by buttons and the Flask API."""

import threading
from dataclasses import dataclass

from .config import DEFAULT_COMFORT


@dataclass(frozen=True)
class ComfortRange:
    min_t: int
    max_t: int
    min_h: int
    max_h: int


class ComfortSettings:
    def __init__(self):
        self._values = dict(DEFAULT_COMFORT)
        self._lock = threading.Lock()

    def snapshot(self):
        with self._lock:
            return ComfortRange(**self._values)

    def adjust(self, field, amount):
        """Preserve the original +/-1 behavior without introducing new limits."""
        with self._lock:
            if field not in self._values:
                raise ValueError(f"Unknown comfort setting: {field}")
            self._values[field] += amount
            return self._values[field]
