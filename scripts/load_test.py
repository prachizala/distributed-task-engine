import asyncio
import time

import httpx

API_BASE_URL = "http://localhost:8000/api/v1"


async def dispatch_single_task(client: httpx.AsyncClient, index: int):
    payload = {
        "task_name": "tasks.data_etl_pipeline",
        "parameters": {"batch_id": index, "records": 500},
        "priority": "normal",
    }
    start = time.perf_counter()
    try:
        resp = await client.post(f"{API_BASE_URL}/tasks/submit", json=payload, timeout=5.0)
        duration_ms = (time.perf_counter() - start) * 1000
        return resp.status_code, duration_ms
    except Exception:
        return 500, 0.0


async def run_benchmark(concurrency: int = 25, total_requests: int = 100):
    print(f"Starting load test: {total_requests} requests with {concurrency} concurrent workers...")
    async with httpx.AsyncClient() as client:
        tasks = [dispatch_single_task(client, i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks)

    successes = [d for status, d in results if status == 202]
    print(f"Results: {len(successes)}/{total_requests} accepted")
    if successes:
        print(f"Avg latency: {sum(successes) / len(successes):.2f}ms")
        print(f"Min latency: {min(successes):.2f}ms | Max: {max(successes):.2f}ms")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
