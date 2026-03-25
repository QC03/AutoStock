from __future__ import annotations

from fastapi import FastAPI

from app.api import api_router
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
