"""Task queue latency percentile and health metric calculator."""

import math


class LatencyPercentileCalculator:
    """Calculates P50, P90, P95, and P99 latency percentiles across execution metrics."""

    @staticmethod
    def calculate_percentile(latencies_ms: list[float], percentile: float) -> float:
        """Returns the calculated percentile latency value."""
        if not latencies_ms:
            return 0.0
        sorted_vals = sorted(latencies_ms)
        k = (len(sorted_vals) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_vals[int(k)]
        d0 = sorted_vals[int(f)] * (c - k)
        d1 = sorted_vals[int(c)] * (k - f)
        return d0 + d1
