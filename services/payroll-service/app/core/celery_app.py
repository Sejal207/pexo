from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "payroll_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.generate_pdf",
        "app.tasks.send_payslip_email",
        "app.tasks.refresh_dashboard_cache",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    # False even in eager mode: a real `.delay()` against a real broker never
    # blocks the caller on the task's outcome, so a failing task must not
    # surface as an exception at the call site here either — only in the
    # task's own recorded result.
    task_eager_propagates=False,
    beat_schedule={
        "refresh-dashboard-kpis-every-10-mins": {
            "task": "app.tasks.refresh_dashboard_cache.refresh_dashboard_cache",
            "schedule": 600.0,
        },
    },
)

if settings.CELERY_TASK_ALWAYS_EAGER:
    # Normally only the worker process (started with `celery -A celery_worker
    # worker`) imports `include=[...]`, registering these tasks — the web
    # process never needs their (heavier, native-dep) implementations.
    # Eager mode runs tasks inline in whichever process calls send_task(),
    # so that process needs them registered too.
    celery_app.loader.import_default_modules()
