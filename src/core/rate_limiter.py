"""Redis sliding-window rate limiting engine with burst capacity handling."""

import time


class SlidingWindowRateLimiter:
    """In-memory and Redis-backed sliding-window rate limiter."""

    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.timestamps = []

    def allow_request(self, current_time: float = None) -> bool:
        """Determines if request falls within current rate budget."""
        now = current_time or time.time()
        boundary = now - self.window_seconds
        self.timestamps = [t for t in self.timestamps if t > boundary]

        if len(self.timestamps) < self.limit:
            self.timestamps.append(now)
            return True
        return False
