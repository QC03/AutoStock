from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.services.auto_trade_runner import auto_trade_runner
import app.models  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    auto_trade_runner.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    auto_trade_runner.stop()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
