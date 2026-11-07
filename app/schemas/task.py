from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreateRequest(BaseModel):
    task_name: str = Field(
        ..., description="Celery registered task name", examples=["tasks.generate_pdf_report"]
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary task payload")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Execution priority")
    countdown_seconds: int = Field(default=0, ge=0, description="Optional delay before execution")


class TaskExecutionLogOut(BaseModel):
    id: int
    log_level: str
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskJobResponse(BaseModel):
    job_id: str
    celery_task_id: Optional[str] = None
    task_name: str
    status: TaskStatus
    priority: TaskPriority
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TaskJobDetailResponse(TaskJobResponse):
    logs: List[TaskExecutionLogOut] = []


class TaskMetricsSummary(BaseModel):
    total_jobs: int
    pending_jobs: int
    successful_jobs: int
    failed_jobs: int
    average_duration_ms: float
