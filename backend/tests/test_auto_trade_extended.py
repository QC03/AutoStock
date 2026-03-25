from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.services.trading_runtime import reset_runtime


def _build_test_client() -> tuple[TestClient, TemporaryDirectory, Engine]:
    temp_dir = TemporaryDirectory()
    db_path = Path(temp_dir.name) / "test_app.db"

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    reset_runtime()
    return TestClient(app), temp_dir, engine


def _signup_and_login(client: TestClient, username: str = "tester2") -> str:
    signup = client.post("/auth/signup", json={"username": username, "password": "pass1234"})
    assert signup.status_code == 200

    login = client.post("/auth/login", json={"username": username, "password": "pass1234"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return token


def test_auto_trade_config_and_activity() -> None:
    client, temp_dir, engine = _build_test_client()
    try:
        token = _signup_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        get_default = client.get("/trading/auto-trade/config", headers=headers)
        assert get_default.status_code == 200
        assert get_default.json()["strategy"] == "rsi_macd"

        set_config = client.post(
            "/trading/auto-trade/config",
            json={
                "strategy": "momentum",
                "symbols": ["AAPL", "MSFT"],
                "quantity": 2,
                "interval_seconds": 7,
                "max_loss_pct": 6,
            },
            headers=headers,
        )
        assert set_config.status_code == 200
        assert set_config.json()["strategy"] == "momentum"
        assert set_config.json()["quantity"] == 2

        turn_on = client.post("/trading/auto-trade", json={"enabled": True}, headers=headers)
        assert turn_on.status_code == 200
        assert turn_on.json()["enabled"] is True

        activity = client.get("/trading/auto-trade/activity", headers=headers)
        assert activity.status_code == 200
        assert activity.json()["enabled"] is True
        assert activity.json()["running"] is True
        assert activity.json()["strategy"] == "momentum"

        turn_off = client.post("/trading/auto-trade", json={"enabled": False}, headers=headers)
        assert turn_off.status_code == 200
        assert turn_off.json()["enabled"] is False

        activity_after = client.get("/trading/auto-trade/activity", headers=headers)
        assert activity_after.status_code == 200
        assert activity_after.json()["enabled"] is False
        assert activity_after.json()["running"] is False
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        _ = temp_dir
