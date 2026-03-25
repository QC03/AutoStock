from __future__ import annotations

import asyncio
import json
import random
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.trading_runtime import engine

router = APIRouter(tags=["ws"])


@router.websocket("/ws/quotes/{symbol}")
async def stream_quotes(websocket: WebSocket, symbol: str) -> None:
    await websocket.accept()
    upper = symbol.upper()

    try:
        price = engine.broker.get_quote(upper)
    except Exception:
        await websocket.send_text(json.dumps({"error": f"unknown symbol: {upper}"}, ensure_ascii=False))
        await websocket.close()
        return

    try:
        while True:
            price += random.uniform(-0.5, 0.5)
            price = max(0.1, price)
            engine.broker.set_quote(upper, round(price, 4))
            payload = {
                "symbol": upper,
                "price": round(price, 4),
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await websocket.send_text(json.dumps(payload, ensure_ascii=False))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
