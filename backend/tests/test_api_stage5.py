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


def _signup_and_login(client: TestClient) -> str:
    signup = client.post("/auth/signup", json={"username": "tester", "password": "pass1234"})
    assert signup.status_code == 200

    login = client.post("/auth/login", json={"username": "tester", "password": "pass1234"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return token


def test_auth_and_order_flow() -> None:
    client, temp_dir, engine = _build_test_client()
    try:
        token = _signup_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        order = client.post(
            "/trading/orders",
            json={"symbol": "AAPL", "side": "BUY", "quantity": 10, "order_type": "MARKET"},
            headers=headers,
        )
        assert order.status_code == 200
        assert order.json()["status"] == "FILLED"

        auto_trade = client.post("/trading/auto-trade", json={"enabled": True}, headers=headers)
        assert auto_trade.status_code == 200
        assert auto_trade.json()["enabled"] is True

        portfolio = client.get("/dashboard/portfolio", headers=headers)
        assert portfolio.status_code == 200
        assert portfolio.json()["cash"] < 100000.0

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


def test_data_and_websocket_endpoints() -> None:
    client, temp_dir, engine = _build_test_client()
    try:
        search = client.get("/data/search", params={"query": "apple"})
        assert search.status_code == 200
        assert any(item["symbol"] == "AAPL" for item in search.json())

        quote = client.get("/data/quote/AAPL")
        assert quote.status_code == 200
        assert quote.json()["symbol"] == "AAPL"

        with client.websocket_connect("/ws/quotes/AAPL") as websocket:
            data = websocket.receive_json()
            assert data["symbol"] == "AAPL"
            assert "price" in data
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        _ = temp_dir
