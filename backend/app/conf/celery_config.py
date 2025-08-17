import os
from celery import Celery
from app.conf.app_settings import app_settings

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery instance
celery_app = Celery(
    "hr_backend_api",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.workers.cv_processing_worker"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Task routing
celery_app.conf.task_routes = {
    "app.workers.cv_processing_worker.process_cv_processing": {"queue": "cv_processing"},
}

# Queue configuration
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_queues = {
    "default": {},
    "cv_processing": {
        "exchange": "cv_processing",
        "routing_key": "cv_processing",
    },
}
