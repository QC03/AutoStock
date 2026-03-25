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
    db_path = Path(temp_dir.name) / "stage7_test.db"

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


def _auth_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    signup = client.post("/auth/signup", json={"username": username, "password": password})
    assert signup.status_code == 200

    login = client.post("/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _derive_signal(price: float) -> str:
    if price < 200:
        return "BUY"
    if price > 900:
        return "SELL"
    return "HOLD"


def test_stage7_mock_account_e2e() -> None:
    client, temp_dir, engine = _build_test_client()
    try:
        headers = _auth_headers(client, username="stage7_user", password="pass1234")

        health = client.get("/health")
        assert health.status_code == 200

        search = client.get("/data/search", params={"query": "AAPL"})
        assert search.status_code == 200
        assert any(item["symbol"] == "AAPL" for item in search.json())

        quote = client.get("/data/quote/AAPL")
        assert quote.status_code == 200
        price = float(quote.json()["price"])

        toggle = client.post("/trading/auto-trade", json={"enabled": True}, headers=headers)
        assert toggle.status_code == 200
        assert toggle.json()["enabled"] is True

        signal = _derive_signal(price)
        order = client.post(
            "/trading/orders",
            json={
                "symbol": "AAPL",
                "side": signal if signal != "HOLD" else "BUY",
                "quantity": 1,
                "order_type": "MARKET",
            },
            headers=headers,
        )
        assert order.status_code == 200
        assert order.json()["status"] == "FILLED"

        trades = client.get("/dashboard/trades", headers=headers)
        assert trades.status_code == 200
        assert len(trades.json()) >= 1

        performance = client.get("/dashboard/performance", headers=headers)
        assert performance.status_code == 200
        assert performance.json()["order_count"] >= 1
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        _ = temp_dir