from __future__ import annotations

from pydantic import BaseModel


class SymbolItem(BaseModel):
    symbol: str
    name: str
    market: str


class QuoteResponse(BaseModel):
    symbol: str
    price: float


class IndicatorResponse(BaseModel):
    symbol: str
    trade_date: str
    sma_20: float
    rsi_14: float
    macd: float
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
