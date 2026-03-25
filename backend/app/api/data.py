from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.data import IndicatorResponse, QuoteResponse, SymbolItem
from app.services.trading_runtime import engine

router = APIRouter(prefix="/data", tags=["data"])


UNIVERSE = [
    SymbolItem(symbol="AAPL", name="Apple Inc.", market="US"),
    SymbolItem(symbol="MSFT", name="Microsoft Corp.", market="US"),
    SymbolItem(symbol="TSLA", name="Tesla Inc.", market="US"),
    SymbolItem(symbol="NVDA", name="NVIDIA Corp.", market="US"),
]


@router.get("/search", response_model=list[SymbolItem])
def search_symbols(query: str = "") -> list[SymbolItem]:
    keyword = query.strip().lower()
    if not keyword:
        return UNIVERSE
    return [item for item in UNIVERSE if keyword in item.symbol.lower() or keyword in item.name.lower()]


@router.get("/quote/{symbol}", response_model=QuoteResponse)
def get_quote(symbol: str) -> QuoteResponse:
    upper = symbol.upper()
    try:
        price = engine.broker.get_quote(upper)
    except Exception as error:
        raise HTTPException(status_code=404, detail=f"시세를 찾을 수 없습니다: {upper}") from error

    return QuoteResponse(symbol=upper, price=price)


@router.get("/indicators/{symbol}", response_model=IndicatorResponse)
def get_latest_indicators(symbol: str) -> IndicatorResponse:
    upper = symbol.upper()
    db_path = Path(__file__).resolve().parents[3] / "data" / "market_data.db"

    if not db_path.exists():
        raise HTTPException(status_code=404, detail="지표 DB 파일이 존재하지 않습니다.")

    query = """
    SELECT trade_date, sma_20, rsi_14, macd, macd_signal, bollinger_upper, bollinger_lower
    FROM market_features
    WHERE symbol = ?
    ORDER BY trade_date DESC
    LIMIT 1;
    """

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(query, (upper,)).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"지표 데이터를 찾을 수 없습니다: {upper}")

    return IndicatorResponse(
        symbol=upper,
        trade_date=str(row[0]),
        sma_20=float(row[1]),
        rsi_14=float(row[2]),
        macd=float(row[3]),
        macd_signal=float(row[4]),
        bollinger_upper=float(row[5]),
        bollinger_lower=float(row[6]),
    )
