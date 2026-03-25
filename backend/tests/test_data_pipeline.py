from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path

from app.services.data_pipeline import (
    DataPipelineService,
    DummyMarketDataProvider,
    SQLiteFeatureRepository,
    calculate_indicators,
    clean_ohlcv,
    normalize_rows,
)


def test_indicator_pipeline_generates_columns() -> None:
    provider = DummyMarketDataProvider()
    records = provider.fetch("AAPL", "US", dt.date(2024, 1, 1), dt.date(2024, 3, 31))

    cleaned = clean_ohlcv(records)
    featured = calculate_indicators(cleaned)
    normalized = normalize_rows(featured)

    assert len(cleaned) > 40
    assert len(featured) == len(cleaned)
    assert len(normalized) == len(cleaned)

    sample = normalized[-1]
    assert "rsi_14" in sample
    assert "macd" in sample
    assert "bollinger_upper" in sample
    assert "close_norm" in sample


def test_pipeline_saves_into_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / "market_data.db"

    service = DataPipelineService(
        provider=DummyMarketDataProvider(),
        repository=SQLiteFeatureRepository(db_path),
    )

    inserted = service.run(
        symbol="AAPL",
        market="US",
        start_date=dt.date(2024, 1, 1),
        end_date=dt.date(2024, 3, 31),
    )

    assert inserted > 0

    with sqlite3.connect(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM market_features").fetchone()[0]

    assert count == inserted
