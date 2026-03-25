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


class AutoTradeConfigRequest(BaseModel):
    strategy: str = "rsi_macd"
    symbols: list[str] = ["AAPL", "MSFT", "TSLA", "NVDA"]
    quantity: int = Field(default=1, ge=1, le=100)
    interval_seconds: int = Field(default=10, ge=3, le=300)
    max_loss_pct: float = Field(default=5.0, ge=1.0, le=30.0)


class AutoTradeConfigResponse(BaseModel):
    strategy: str
    symbols: list[str]
    quantity: int
    interval_seconds: int
    max_loss_pct: float


class AutoTradeActivityResponse(BaseModel):
    enabled: bool
    running: bool
    strategy: str
    symbols: list[str]
    quantity: int
    interval_seconds: int
    next_run_in_seconds: int | None = None
    last_run_at: str | None = None
    last_action: str | None = None
    last_symbol: str | None = None
    last_signal: str | None = None
    last_message: str | None = None
