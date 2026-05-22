from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "graph",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "parse-avito": {
        "task": "app.workers.tasks.run_avito_parser",
        "schedule": settings.parser_avito_interval_seconds,
    },
    "parse-youla": {
        "task": "app.workers.tasks.run_youla_parser",
        "schedule": settings.parser_youla_interval_seconds,
    },
    "parse-vk": {
        "task": "app.workers.tasks.run_vk_parser",
        "schedule": settings.parser_vk_interval_seconds,
    },
    "reset-daily-limits": {
        "task": "app.workers.tasks.reset_daily_limits",
        "schedule": crontab(hour=0, minute=0),
    },
    "sync-premium-membership": {
        "task": "app.workers.tasks.sync_premium_membership",
        "schedule": 300.0,
    },
    "cleanup-old-listings": {
        "task": "app.workers.tasks.cleanup_old_listings",
        "schedule": crontab(hour=3, minute=0),
    },
}
