"""
Dead-Letter Queue (DLQ) Eviction Metric Counter
Maintains cumulative metric counters for failed or expired background task payloads.
"""
from typing import Dict, Any

class DLQEvictionCounter:
    def __init__(self):
        self._counts: Dict[str, int] = {}

    def record_eviction(self, reason: str) -> None:
        self._counts[reason] = self._counts.get(reason, 0) + 1

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_evictions": sum(self._counts.values()),
            "by_reason": dict(self._counts)
        }

if __name__ == "__main__":
    c = DLQEvictionCounter()
    c.record_eviction("TTL_EXPIRED")
    c.record_eviction("TTL_EXPIRED")
    c.record_eviction("MAX_RETRIES_EXCEEDED")
    m = c.get_metrics()
    assert m["total_evictions"] == 3
    assert m["by_reason"]["TTL_EXPIRED"] == 2
    print("DLQ eviction counter unit tests passed!")
