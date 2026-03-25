from __future__ import annotations

from pydantic import BaseModel


class PortfolioResponse(BaseModel):
    cash: float
    total_value: float
    total_unrealized_pnl: float
    positions: list[dict[str, float | int | str]]


class TradeHistoryItem(BaseModel):
    symbol: str
    side: str
    quantity: int
    price: float
    status: str
    created_at: str


class PerformanceResponse(BaseModel):
    order_count: int
    buy_count: int
    sell_count: int
    notional: float
