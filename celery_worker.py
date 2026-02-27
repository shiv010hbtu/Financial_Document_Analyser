# celery_worker.py
## Celery Worker Configuration for Queue-based Processing

import os
from dotenv import load_dotenv
load_dotenv()

from celery import Celery

# Redis as message broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks_worker"]  # tasks_worker.py file se tasks load karega
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,         # Task started status track karo
    task_acks_late=True,             # Task complete hone ke baad acknowledge karo
    worker_prefetch_multiplier=1,    # Ek worker ek task le — fair distribution
    task_routes={
        "tasks_worker.analyze_document_task": {"queue": "financial_analysis"}
    }
)
