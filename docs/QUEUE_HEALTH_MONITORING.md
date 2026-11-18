# Queue Health Monitoring Architecture

## Health Metrics
1. Worker Heartbeat interval: 5 seconds
2. Exponential backoff factor: 2.0 with randomized jitter (+/- 15%)
3. Dead Letter Queue (DLQ) threshold: 5 retries
