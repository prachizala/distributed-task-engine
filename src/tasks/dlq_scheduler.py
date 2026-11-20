"""Dead-letter queue (DLQ) and exponential backoff retry policy for asynchronous tasks."""


class DLQRetryPolicy:
    """Calculates exponential backoff delay with jitter ceiling."""

    def __init__(self, base_delay: int = 2, max_delay: int = 300, max_retries: int = 5):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries

    def calculate_delay_seconds(self, retry_attempt: int) -> int:
        """Returns exponential backoff interval in seconds: min(base * 2^attempt, max_delay)."""
        if retry_attempt >= self.max_retries:
            return -1  # Send to permanent Dead-Letter Queue
        delay = self.base_delay * (2**retry_attempt)
        return min(delay, self.max_delay)
