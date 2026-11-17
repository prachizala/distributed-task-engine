"""
Locust High-Concurrency Load & Stress Testing Suite.
Simulates concurrent background job enqueuing, client-side idempotency collision,
and status polling throughput against distributed-task-engine.
"""

import uuid

from locust import HttpUser, between, task


class TaskEngineLoadUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def submit_idempotent_task(self):
        """Simulates high-velocity enqueue with unique idempotency keys."""
        client_key = f"client-req-{uuid.uuid4().hex[:12]}"
        headers = {"X-Idempotency-Key": client_key, "Content-Type": "application/json"}
        payload = {
            "task_type": "data_aggregation",
            "parameters": {"batch_size": 500, "region": "ap-south-1"},
        }
        self.client.post("/api/v1/tasks/enqueue", json=payload, headers=headers)

    @task(2)
    def submit_duplicate_idempotency_collision(self):
        """Simulates race-condition collision where the same key is submitted twice simultaneously."""
        colliding_key = "collision-test-static-key"
        headers = {"X-Idempotency-Key": colliding_key, "Content-Type": "application/json"}
        payload = {"task_type": "report_generation", "parameters": {"format": "pdf"}}
        self.client.post("/api/v1/tasks/enqueue", json=payload, headers=headers)

    @task(5)
    def poll_health_and_queue_metrics(self):
        """Polls engine status and health endpoints."""
        self.client.get("/health")
        self.client.get("/api/v1/metrics/queue")
