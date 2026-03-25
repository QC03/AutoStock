from __future__ import annotations

import sqlite3
import datetime as dt
from pathlib import Path

from ai.models.training_pipeline import (
    DEFAULT_FEATURE_COLUMNS,
    build_supervised_samples,
    load_feature_rows,
    run_training_pipeline,
    split_dataset_time_series,
)


def _create_test_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS market_features (
                symbol TEXT NOT NULL,
                market TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                sma_20 REAL NOT NULL,
                rsi_14 REAL NOT NULL,
                macd REAL NOT NULL,
                macd_signal REAL NOT NULL,
                bollinger_upper REAL NOT NULL,
                bollinger_lower REAL NOT NULL,
                open_norm REAL NOT NULL,
                high_norm REAL NOT NULL,
                low_norm REAL NOT NULL,
                close_norm REAL NOT NULL,
                volume_norm REAL NOT NULL,
                sma_20_norm REAL NOT NULL,
                rsi_14_norm REAL NOT NULL,
                macd_norm REAL NOT NULL,
                macd_signal_norm REAL NOT NULL,
                bollinger_upper_norm REAL NOT NULL,
                bollinger_lower_norm REAL NOT NULL,
                PRIMARY KEY (symbol, market, trade_date)
            );
            """
        )

        rows = []
        base_price = 100.0
        start_date = dt.date(2024, 1, 1)
        for day in range(80):
            close = base_price + day * 0.4 + ((day % 5) - 2) * 0.1
            sma_20 = close - 0.2
            norm = min(1.0, max(0.0, day / 79))
            trade_date = (start_date + dt.timedelta(days=day)).isoformat()
            rows.append(
                (
                    "AAPL",
                    "US",
                    trade_date,
                    close - 0.3,
                    close + 0.4,
                    close - 0.5,
                    close,
                    100000 + day * 100,
                    sma_20,
                    50 + day * 0.1,
                    0.1 * day,
                    0.08 * day,
                    close + 1.0,
                    close - 1.0,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                    norm,
                )
            )

        connection.executemany(
            """
            INSERT OR REPLACE INTO market_features (
                symbol, market, trade_date, open, high, low, close, volume,
                sma_20, rsi_14, macd, macd_signal, bollinger_upper, bollinger_lower,
                open_norm, high_norm, low_norm, close_norm, volume_norm,
                sma_20_norm, rsi_14_norm, macd_norm, macd_signal_norm,
                bollinger_upper_norm, bollinger_lower_norm
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?
            )
            """,
            rows,
        )
        connection.commit()


def test_split_and_training_pipeline(tmp_path: Path) -> None:
    db_path = tmp_path / "market_data.db"
    _create_test_db(db_path)

    rows = load_feature_rows(db_path, "AAPL", "US")
    samples = build_supervised_samples(rows, DEFAULT_FEATURE_COLUMNS)
    split = split_dataset_time_series(samples)

    assert len(split.train) > 10
    assert len(split.validation) > 5
    assert len(split.test) > 5

    result = run_training_pipeline(
        database_path=db_path,
        symbol="AAPL",
        market="US",
        model_output_dir=tmp_path / "models",
        signal_output_dir=tmp_path / "signals",
    )

    assert result.model_path.exists()
    assert result.signals_path.exists()

    ml_test = result.summary["metrics"]["ml_test"]
    baseline_test = result.summary["metrics"]["baseline_test"]

    assert "sharpe_ratio" in ml_test
    assert "max_drawdown" in ml_test
    assert "win_rate" in baseline_test
