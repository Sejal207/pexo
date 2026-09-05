"""
Runs an async coroutine from a sync Celery task body. In production, a task
executes in a fresh worker process/thread with no event loop already
running, so a plain `asyncio.run(coro)` is enough. But with
CELERY_TASK_ALWAYS_EAGER=True (local testing, no broker), `send_task(...)`
runs the task inline in the caller's own process — which, called from a
FastAPI request handler, already has a running event loop, and
`asyncio.run()` cannot be nested inside one. Detect that case and fall back
to running the coroutine in a fresh loop on a separate thread instead.
"""
import asyncio
import concurrent.futures
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()
