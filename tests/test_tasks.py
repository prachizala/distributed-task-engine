import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_task_and_fetch_status(async_client: AsyncClient):
    task_payload = {
        "task_name": "tasks.generate_pdf_report",
        "parameters": {"report_name": "Q3_Workforce_Payroll", "records_count": 1200},
        "priority": "high",
        "countdown_seconds": 0,
    }
    submit_resp = await async_client.post("/api/v1/tasks/submit", json=task_payload)
    assert submit_resp.status_code == 202
    job_data = submit_resp.json()
    assert "job_id" in job_data
    assert job_data["status"] == "PENDING"
    assert job_data["priority"] == "high"

    # Query status by job_id
    job_id = job_data["job_id"]
    status_resp = await async_client.get(f"/api/v1/tasks/{job_id}")
    assert status_resp.status_code == 200
    detail_data = status_resp.json()
    assert detail_data["job_id"] == job_id
    assert len(detail_data["logs"]) >= 1
    assert "enqueued successfully" in detail_data["logs"][0]["message"]


@pytest.mark.asyncio
async def test_list_tasks_and_metrics_summary(async_client: AsyncClient):
    # Submit 2 jobs
    await async_client.post(
        "/api/v1/tasks/submit", json={"task_name": "tasks.data_etl_pipeline", "priority": "normal"}
    )
    await async_client.post(
        "/api/v1/tasks/submit", json={"task_name": "tasks.dispatch_email", "priority": "low"}
    )

    list_resp = await async_client.get("/api/v1/tasks?limit=10")
    assert list_resp.status_code == 200
    jobs = list_resp.json()
    assert len(jobs) >= 2

    # Query metrics
    metrics_resp = await async_client.get("/api/v1/tasks/metrics/summary")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["total_jobs"] >= 2


@pytest.mark.asyncio
async def test_enqueue_idempotency_with_client_key(async_client: AsyncClient):
    key = "client-tx-uuid-998877"
    task_payload = {
        "task_name": "tasks.generate_pdf_report",
        "parameters": {"report_name": "Financial_Audit_2026"},
        "priority": "critical",
    }
    # First submit
    resp1 = await async_client.post(
        "/api/v1/tasks/submit", json=task_payload, headers={"Idempotency-Key": key}
    )
    assert resp1.status_code == 202
    data1 = resp1.json()

    # Second submit with the identical Idempotency-Key
    resp2 = await async_client.post(
        "/api/v1/tasks/submit", json=task_payload, headers={"Idempotency-Key": key}
    )
    assert resp2.status_code in (200, 202)
    data2 = resp2.json()

    # Must return the EXACT same job_id and no duplicate created
    assert data1["job_id"] == data2["job_id"]
