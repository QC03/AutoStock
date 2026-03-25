from __future__ import annotations

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    symbol: str
    side: str
    quantity: int = Field(gt=0)
    order_type: str = "MARKET"
    limit_price: float | None = None


class OrderResponse(BaseModel):
    id: int
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: float
    status: str
    reason: str


class AutoTradeToggleRequest(BaseModel):
    enabled: bool


class AutoTradeToggleResponse(BaseModel):
    enabled: bool
