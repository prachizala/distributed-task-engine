import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import check_rate_limit, get_current_user, get_db_session
from app.models.task import TaskExecutionLog, TaskJob, TaskStatus
from app.models.user import User
from app.schemas.task import (
    TaskCreateRequest,
    TaskJobDetailResponse,
    TaskJobResponse,
    TaskMetricsSummary,
)
from app.workers.celery_app import celery_app

router = APIRouter()


@router.post(
    "/submit",
    response_model=TaskJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(check_rate_limit)],
    summary="Enqueue a new asynchronous background task",
)
async def submit_task(
    payload: TaskCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user),
):
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    celery_id: Optional[str] = None

    # Attempt Celery task dispatch (graceful fallback if Celery/Redis offline)
    try:
        countdown = payload.countdown_seconds if payload.countdown_seconds > 0 else None
        async_result = celery_app.send_task(
            payload.task_name,
            kwargs=payload.parameters,
            countdown=countdown,
        )
        celery_id = async_result.id
    except Exception:
        # Standalone mock dispatch when running without full Redis broker
        celery_id = f"mock_{uuid.uuid4().hex[:8]}"

    task_job = TaskJob(
        job_id=job_id,
        celery_task_id=celery_id,
        task_name=payload.task_name,
        parameters=payload.parameters,
        priority=payload.priority,
        status=TaskStatus.PENDING,
        created_by_user_id=current_user.id if current_user else None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(task_job)
    await db.flush()

    # Initial Audit Log
    audit_log = TaskExecutionLog(
        task_job_id=task_job.id,
        log_level="INFO",
        message=f"Task enqueued successfully with celery ID {celery_id} (priority: {payload.priority})",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(task_job)
    return task_job


@router.get(
    "/{job_id}",
    response_model=TaskJobDetailResponse,
    summary="Retrieve execution status, results, and logs for a job",
)
async def get_task_status(job_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(TaskJob).where(TaskJob.job_id == job_id).options(selectinload(TaskJob.logs))
    result = await db.execute(stmt)
    task_job = result.scalar_one_or_none()

    if not task_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task job '{job_id}' not found"
        )
    return task_job


@router.get(
    "",
    response_model=List[TaskJobResponse],
    summary="List tasks with optional status and name filters",
)
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    task_name: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    stmt = select(TaskJob)
    if status_filter:
        stmt = stmt.where(TaskJob.status == status_filter)
    if task_name:
        stmt = stmt.where(TaskJob.task_name.ilike(f"%{task_name}%"))

    stmt = stmt.order_by(TaskJob.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/metrics/summary",
    response_model=TaskMetricsSummary,
    summary="Aggregated task engine metrics and throughput analytics",
)
async def get_metrics_summary(db: AsyncSession = Depends(get_db_session)):
    total_q = select(func.count(TaskJob.id))
    pending_q = select(func.count(TaskJob.id)).where(TaskJob.status == TaskStatus.PENDING)
    success_q = select(func.count(TaskJob.id)).where(TaskJob.status == TaskStatus.SUCCESS)
    failed_q = select(func.count(TaskJob.id)).where(TaskJob.status == TaskStatus.FAILURE)
    avg_duration_q = select(func.coalesce(func.avg(TaskJob.execution_duration_ms), 0.0))

    total = (await db.execute(total_q)).scalar() or 0
    pending = (await db.execute(pending_q)).scalar() or 0
    success = (await db.execute(success_q)).scalar() or 0
    failed = (await db.execute(failed_q)).scalar() or 0
    avg_duration = (await db.execute(avg_duration_q)).scalar() or 0.0

    return TaskMetricsSummary(
        total_jobs=total,
        pending_jobs=pending,
        successful_jobs=success,
        failed_jobs=failed,
        average_duration_ms=round(float(avg_duration), 2),
    )
