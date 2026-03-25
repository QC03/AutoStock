from __future__ import annotations

import os
from typing import Any

try:
    from celery import Celery
except ImportError:  # pragma: no cover
    Celery = None  # type: ignore[misc,assignment]


def create_celery_app() -> Any:
    if Celery is None:
        return None

    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    app = Celery("autostock_trading", broker=broker_url, backend=backend_url)

    app.conf.timezone = "Asia/Seoul"
    app.conf.enable_utc = False
    app.conf.beat_schedule = {
        "market-open-job": {
            "task": "backend.app.services.trading_scheduler.run_market_open_job",
            "schedule": {"hour": 9, "minute": 0},
        },
        "market-close-job": {
            "task": "backend.app.services.trading_scheduler.run_market_close_job",
            "schedule": {"hour": 15, "minute": 30},
        },
    }

    return app


celery_app = create_celery_app()


if celery_app is not None:

    @celery_app.task(name="backend.app.services.trading_scheduler.run_market_open_job")
    def run_market_open_job() -> str:
        return "market_open_job_triggered"


    @celery_app.task(name="backend.app.services.trading_scheduler.run_market_close_job")
    def run_market_close_job() -> str:
        return "market_close_job_triggered"

else:

    def run_market_open_job() -> str:
        return "celery_not_installed"


    def run_market_close_job() -> str:
        return "celery_not_installed"
