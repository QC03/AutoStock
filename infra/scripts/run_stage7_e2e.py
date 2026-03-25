from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass

import httpx


@dataclass
class Stage7Result:
    username: str
    signal: str
    order_id: str
    order_status: str
    trade_count: int
    order_count: int


def _request(client: httpx.Client, method: str, path: str, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response


def _derive_signal(price: float) -> str:
    if price < 200:
        return "BUY"
    if price > 900:
        return "SELL"
    return "HOLD"


def run(base_url: str, username: str, password: str) -> Stage7Result:
    with httpx.Client(base_url=base_url, timeout=20.0) as client:
        signup = client.post("/auth/signup", json={"username": username, "password": password})
        if signup.status_code not in (200, 409):
            signup.raise_for_status()

        login = _request(client, "POST", "/auth/login", json={"username": username, "password": password}).json()
        token = login["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        _request(client, "GET", "/health")
        _request(client, "GET", "/data/search", params={"query": "AAPL"})
        quote = _request(client, "GET", "/data/quote/AAPL").json()
        signal = _derive_signal(float(quote["price"]))

        _request(client, "POST", "/trading/auto-trade", json={"enabled": True}, headers=headers)

        if signal != "HOLD":
            order_payload = {
                "symbol": "AAPL",
                "side": signal,
                "quantity": 1,
                "order_type": "MARKET",
            }
            order = _request(client, "POST", "/trading/orders", json=order_payload, headers=headers).json()
        else:
            order_payload = {
                "symbol": "AAPL",
                "side": "BUY",
                "quantity": 1,
                "order_type": "MARKET",
            }
            order = _request(client, "POST", "/trading/orders", json=order_payload, headers=headers).json()

        trades = _request(client, "GET", "/dashboard/trades", headers=headers).json()
        performance = _request(client, "GET", "/dashboard/performance", headers=headers).json()
        _request(client, "GET", "/dashboard/portfolio", headers=headers)

    return Stage7Result(
        username=username,
        signal=signal,
        order_id=order["order_id"],
        order_status=order["status"],
        trade_count=len(trades),
        order_count=int(performance["order_count"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stage7 mock-trading E2E scenario")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--username", default=f"stage7_{int(time.time())}")
    parser.add_argument("--password", default="pass1234")
    args = parser.parse_args()

    result = run(base_url=args.base_url, username=args.username, password=args.password)
    print(
        json.dumps(
            {
                "result": "ok",
                "username": result.username,
                "signal": result.signal,
                "order_id": result.order_id,
                "order_status": result.order_status,
                "trade_count": result.trade_count,
                "order_count": result.order_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()