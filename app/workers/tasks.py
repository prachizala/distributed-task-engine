import random
import time
from typing import Any, Dict

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="tasks.generate_pdf_report")
def generate_pdf_report(self, report_name: str, records_count: int = 500) -> Dict[str, Any]:
    """
    Simulates high-CPU compute job (report compilation and data export).
    """
    time.sleep(1.5)
    return {
        "status": "completed",
        "report_name": report_name,
        "processed_records": records_count,
        "output_format": "application/pdf",
        "file_size_kb": random.randint(120, 2400),
    }


@celery_app.task(bind=True, name="tasks.dispatch_email_notifications")
def dispatch_email_notifications(
    self, recipients: list[str], subject: str, template: str
) -> Dict[str, Any]:
    """
    Simulates batch I/O asynchronous email dispatch with retry logic.
    """
    time.sleep(1.0)
    return {
        "status": "dispatched",
        "total_sent": len(recipients),
        "subject": subject,
        "template_used": template,
    }


@celery_app.task(bind=True, name="tasks.data_etl_pipeline")
def data_etl_pipeline(self, source_url: str, destination_table: str) -> Dict[str, Any]:
    """
    Simulates an ETL pipeline ingestion job.
    """
    time.sleep(2.0)
    return {
        "status": "ingested",
        "source": source_url,
        "target": destination_table,
        "rows_inserted": random.randint(1000, 50000),
    }
