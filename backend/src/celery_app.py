"""
Celery Application Configuration

Configures Celery with Redis as the message broker for background task processing.
Used for long-running jobs like video processing, AI analysis, and Playwright sessions.

NOTE: Celery is optional. When ENABLE_BACKGROUND_JOBS=false (default), video
processing runs synchronously. Set ENABLE_BACKGROUND_JOBS=true and provide
REDIS_URL for background processing.
"""

import os
from config import settings

# Only initialize Celery if background jobs are enabled
celery_app = None

if settings.enable_background_jobs:
    from celery import Celery

    # Get Redis URL from settings
    REDIS_URL = settings.redis_url

    # Heroku Redis uses rediss:// for SSL, Celery needs special config
    if REDIS_URL.startswith("rediss://"):
        # Heroku Redis requires SSL without certificate verification
        REDIS_URL = f"{REDIS_URL}?ssl_cert_reqs=none"

    # Create Celery app
    celery_app = Celery(
        "tastemaker",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["tasks"]  # Module containing task definitions
    )

    # Celery configuration
    celery_app.conf.update(
        # Task settings
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,

        # Task execution settings
        task_acks_late=True,  # Acknowledge after task completes (safer)
        task_reject_on_worker_lost=True,  # Requeue if worker dies
        worker_prefetch_multiplier=1,  # One task at a time per worker

        # Result backend settings
        result_expires=86400,  # Results expire after 24 hours

        # Task time limits (in seconds)
        task_soft_time_limit=600,  # 10 minutes soft limit
        task_time_limit=900,  # 15 minutes hard limit

        # Retry settings
        task_default_retry_delay=60,  # Wait 1 minute before retry
        task_max_retries=3,

        # Worker settings
        worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory cleanup)

        # Logging
        worker_hijack_root_logger=False,
    )

    # Optional: Define task routes for different queues
    celery_app.conf.task_routes = {
        "tasks.process_video_audit_task": {"queue": "video"},
        "tasks.process_playwright_audit_task": {"queue": "playwright"},
        "tasks.extract_frame_values_task": {"queue": "ai"},
    }

    # For local development without multiple queues, use default queue
    celery_app.conf.task_default_queue = "default"


def is_celery_available() -> bool:
    """Check if Celery is available and configured."""
    return celery_app is not None
