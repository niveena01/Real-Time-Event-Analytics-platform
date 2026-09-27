from celery import Celery
from app.config import settings

celery_app = Celery(
    "event_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "process-batch-events-every-second": {
            "task": "app.workers.tasks.process_event_batch",
            "schedule": 1.0,
        },
    },
)