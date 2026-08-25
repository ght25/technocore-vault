"""Atomic monotonic nonce generator to prevent replay or collision errors."""

from __future__ import annotations

import time


class NonceTracker:
    """Generates strictly monotonically increasing 1-19 digit nonces."""

    def __init__(self) -> None:
        self._last_nonce = 0

    def next_nonce(self) -> str:
        """Return next unique high-resolution nonce string."""
        now = time.time_ns()
        if now <= self._last_nonce:
            now = self._last_nonce + 1
        self._last_nonce = now
        return str(now)
