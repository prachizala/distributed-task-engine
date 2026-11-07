import enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskJob(Base):
    __tablename__ = "task_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    task_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        String(50), default=TaskStatus.PENDING, index=True, nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        String(50), default=TaskPriority.NORMAL, nullable=False
    )

    # Payload & Execution Results
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit & Timestamps
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    logs: Mapped[list["TaskExecutionLog"]] = relationship(
        "TaskExecutionLog", back_populates="task_job", cascade="all, delete-orphan"
    )


class TaskExecutionLog(Base):
    __tablename__ = "task_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_jobs.id"), nullable=False, index=True
    )
    log_level: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    task_job: Mapped["TaskJob"] = relationship("TaskJob", back_populates="logs")
