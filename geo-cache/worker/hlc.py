"""
Hybrid Logical Clock (HLC).

Produces timestamps of the form (physical_time_ms, logical_counter, node_id)
that are monotonically increasing locally, and give a deterministic total
order across nodes (physical time first, logical counter breaks ties from
the same millisecond, node_id breaks ties if both are equal).
"""

import time
import threading


class HLC:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._lock = threading.Lock()
        self._last_physical = 0
        self._counter = 0

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def tick(self):
        """Call when a local event happens (e.g. a local write)."""
        with self._lock:
            now = self._now_ms()
            if now > self._last_physical:
                self._last_physical = now
                self._counter = 0
            else:
                self._counter += 1
            return (self._last_physical, self._counter, self.node_id)

    def update(self, remote_ts):
        """Call when a remote timestamp is received, to fold it into our clock."""
        remote_physical, remote_counter, _ = remote_ts
        with self._lock:
            now = self._now_ms()
            new_physical = max(self._last_physical, remote_physical, now)
            if new_physical == self._last_physical == remote_physical:
                self._counter = max(self._counter, remote_counter) + 1
            elif new_physical == self._last_physical:
                self._counter += 1
            elif new_physical == remote_physical:
                self._counter = remote_counter + 1
            else:
                self._counter = 0
            self._last_physical = new_physical
            return (self._last_physical, self._counter, self.node_id)


def compare(ts_a, ts_b) -> int:
    """Return -1, 0, or 1 comparing two (physical, counter, node_id) timestamps."""
    if ts_a[:2] != ts_b[:2]:
        return -1 if ts_a[:2] < ts_b[:2] else 1
    # physical+counter tie -> break with node_id, deterministic across all replicas
    if ts_a[2] == ts_b[2]:
        return 0
    return -1 if ts_a[2] < ts_b[2] else 1
