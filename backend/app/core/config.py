from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "AutoStock API"
    jwt_secret: str = os.getenv("AUTOSTOCK_JWT_SECRET", "autostock-dev-secret-key-at-least-32-bytes")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("AUTOSTOCK_CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )
    database_url: str = os.getenv(
        "AUTOSTOCK_DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parents[2] / 'data' / 'autostock_app.db'}",
    )


settings = Settings()
