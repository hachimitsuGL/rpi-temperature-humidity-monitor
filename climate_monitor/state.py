"""In-memory latest reading and time series for the local web dashboard."""

import threading
import time
from collections import deque

from .config import HISTORY_MAX_POINTS


class MonitorState:
    def __init__(self, max_points=HISTORY_MAX_POINTS):
        self._lock = threading.Lock()
        self._current = {
            "temperature": None,
            "humidity": None,
            "temp_status": "unknown",
            "hum_status": "unknown",
            "updated_at": None,
        }
        self._history = deque(maxlen=max_points)

    def update(self, temperature, humidity, temp_status, hum_status):
        timestamp = time.time()
        label = time.strftime("%H:%M:%S", time.localtime(timestamp))
        with self._lock:
            self._current.update({
                "temperature": float(temperature),
                "humidity": float(humidity),
                "temp_status": temp_status,
                "hum_status": hum_status,
                "updated_at": label,
            })
            self._history.append({
                "timestamp": timestamp,
                "time": label,
                "temperature": float(temperature),
                "humidity": float(humidity),
            })

    def current(self):
        with self._lock:
            return dict(self._current)

    def history(self):
        with self._lock:
            return list(self._history)
