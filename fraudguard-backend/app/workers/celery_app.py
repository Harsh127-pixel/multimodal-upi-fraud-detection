import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "fraudguard_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.workers.audio_task",
        "app.workers.graph_task",   # M6 nightly retraining
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # ── Celery Beat Schedule ──────────────────────────────────────────
    beat_schedule={
        "m6-nightly-graph-retrain": {
            "task": "app.workers.graph_task.retrain_graph_model",
            "schedule": crontab(hour=2, minute=0),   # every night at 2 AM UTC
        },
    },
)
