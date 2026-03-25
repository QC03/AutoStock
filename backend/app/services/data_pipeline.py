from __future__ import annotations

import datetime as dt
import importlib
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class OHLCVRecord:
    symbol: str
    market: str
    trade_date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataProvider(Protocol):
    def fetch(
        self,
        symbol: str,
        market: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> list[OHLCVRecord]:
        ...


class DummyMarketDataProvider:
    def fetch(
        self,
        symbol: str,
        market: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> list[OHLCVRecord]:
        rows: list[OHLCVRecord] = []
        cursor = start_date
        base_price = 100.0
        day_index = 0

        while cursor <= end_date:
            if cursor.weekday() < 5:
                seasonal = math.sin(day_index / 5.0) * 2.0
                close = max(1.0, base_price + seasonal + (day_index * 0.15))
                open_price = max(1.0, close - 0.4)
                high = close + 0.8
                low = max(0.1, close - 1.0)
                volume = 100000 + day_index * 250

                rows.append(
                    OHLCVRecord(
                        symbol=symbol,
                        market=market,
                        trade_date=cursor,
                        open=round(open_price, 4),
                        high=round(high, 4),
                        low=round(low, 4),
                        close=round(close, 4),
                        volume=float(volume),
                    )
                )
            cursor += dt.timedelta(days=1)
            day_index += 1

        return rows


class YahooFinanceDataProvider:
    def fetch(
        self,
        symbol: str,
        market: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> list[OHLCVRecord]:
        try:
            yf = importlib.import_module("yfinance")
        except ImportError as error:
            raise RuntimeError(
                "yfinance가 설치되어 있지 않습니다. `pip install yfinance` 후 다시 시도하세요."
            ) from error

        dataframe = yf.download(
            symbol,
            start=start_date.isoformat(),
            end=(end_date + dt.timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        if dataframe.empty:
            return []

        rows: list[OHLCVRecord] = []
        for index, row in dataframe.iterrows():
            rows.append(
                OHLCVRecord(
                    symbol=symbol,
                    market=market,
                    trade_date=index.date(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
            )
        return rows


def build_provider(name: str) -> MarketDataProvider:
    normalized = name.strip().lower()
    providers: dict[str, MarketDataProvider] = {
        "dummy": DummyMarketDataProvider(),
        "yfinance": YahooFinanceDataProvider(),
    }
    if normalized not in providers:
        available = ", ".join(sorted(providers.keys()))
        raise ValueError(f"지원하지 않는 provider입니다: {name}. 사용 가능: {available}")
    return providers[normalized]


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def clean_ohlcv(records: list[OHLCVRecord]) -> list[OHLCVRecord]:
    deduplicated: dict[tuple[str, str, dt.date], OHLCVRecord] = {}

    for record in records:
        if min(record.open, record.high, record.low, record.close) <= 0:
            continue
        if record.volume < 0:
            continue
        key = (record.symbol, record.market, record.trade_date)
        deduplicated[key] = record

    cleaned = list(deduplicated.values())
    cleaned.sort(key=lambda item: item.trade_date)
    return cleaned


def _sma(values: list[float], window: int, current_index: int) -> float:
    if current_index + 1 < window:
        return 0.0
    subset = values[current_index - window + 1 : current_index + 1]
    return sum(subset) / window


def _ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [values[0]]
    for value in values[1:]:
        previous = result[-1]
        result.append((value - previous) * alpha + previous)
    return result


def calculate_indicators(records: list[OHLCVRecord]) -> list[dict[str, float | str]]:
    if not records:
        return []

    closes = [item.close for item in records]
    ema12 = _ema_series(closes, 12)
    ema26 = _ema_series(closes, 26)
    macd_line = [short - long for short, long in zip(ema12, ema26)]
    macd_signal = _ema_series(macd_line, 9)

    enriched: list[dict[str, float | str]] = []

    gains: list[float] = [0.0]
    losses: list[float] = [0.0]
    for index in range(1, len(closes)):
        change = closes[index] - closes[index - 1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))

    for index, record in enumerate(records):
        sma20 = _sma(closes, 20, index)

        if index + 1 >= 20:
            window_values = closes[index - 19 : index + 1]
            mean = sum(window_values) / len(window_values)
            variance = sum((value - mean) ** 2 for value in window_values) / len(window_values)
            std_dev = math.sqrt(variance)
            boll_upper = mean + (std_dev * 2)
            boll_lower = mean - (std_dev * 2)
        else:
            boll_upper = 0.0
            boll_lower = 0.0

        if index >= 14:
            avg_gain = sum(gains[index - 13 : index + 1]) / 14
            avg_loss = sum(losses[index - 13 : index + 1]) / 14
            rs = _safe_divide(avg_gain, avg_loss)
            rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100.0
        else:
            rsi = 0.0

        enriched.append(
            {
                "symbol": record.symbol,
                "market": record.market,
                "trade_date": record.trade_date.isoformat(),
                "open": record.open,
                "high": record.high,
                "low": record.low,
                "close": record.close,
                "volume": record.volume,
                "sma_20": round(sma20, 6),
                "rsi_14": round(rsi, 6),
                "macd": round(macd_line[index], 6),
                "macd_signal": round(macd_signal[index], 6),
                "bollinger_upper": round(boll_upper, 6),
                "bollinger_lower": round(boll_lower, 6),
            }
        )

    return enriched


def normalize_rows(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    if not rows:
        return []

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "sma_20",
        "rsi_14",
        "macd",
        "macd_signal",
        "bollinger_upper",
        "bollinger_lower",
    ]

    mins: dict[str, float] = {}
    maxs: dict[str, float] = {}

    for column in numeric_columns:
        values = [float(row[column]) for row in rows]
        mins[column] = min(values)
        maxs[column] = max(values)

    normalized: list[dict[str, float | str]] = []
    for row in rows:
        copied = dict(row)
        for column in numeric_columns:
            minimum = mins[column]
            maximum = maxs[column]
            value = float(row[column])
            if maximum == minimum:
                copied[f"{column}_norm"] = 0.0
            else:
                copied[f"{column}_norm"] = round((value - minimum) / (maximum - minimum), 6)
        normalized.append(copied)

    return normalized


class SQLiteFeatureRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
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
            connection.commit()

    def upsert(self, rows: list[dict[str, float | str]]) -> int:
        if not rows:
            return 0

        query = """
        INSERT INTO market_features (
            symbol, market, trade_date, open, high, low, close, volume,
            sma_20, rsi_14, macd, macd_signal, bollinger_upper, bollinger_lower,
            open_norm, high_norm, low_norm, close_norm, volume_norm,
            sma_20_norm, rsi_14_norm, macd_norm, macd_signal_norm,
            bollinger_upper_norm, bollinger_lower_norm
        ) VALUES (
            :symbol, :market, :trade_date, :open, :high, :low, :close, :volume,
            :sma_20, :rsi_14, :macd, :macd_signal, :bollinger_upper, :bollinger_lower,
            :open_norm, :high_norm, :low_norm, :close_norm, :volume_norm,
            :sma_20_norm, :rsi_14_norm, :macd_norm, :macd_signal_norm,
            :bollinger_upper_norm, :bollinger_lower_norm
        )
        ON CONFLICT(symbol, market, trade_date) DO UPDATE SET
            open=excluded.open,
            high=excluded.high,
            low=excluded.low,
            close=excluded.close,
            volume=excluded.volume,
            sma_20=excluded.sma_20,
            rsi_14=excluded.rsi_14,
            macd=excluded.macd,
            macd_signal=excluded.macd_signal,
            bollinger_upper=excluded.bollinger_upper,
            bollinger_lower=excluded.bollinger_lower,
            open_norm=excluded.open_norm,
            high_norm=excluded.high_norm,
            low_norm=excluded.low_norm,
            close_norm=excluded.close_norm,
            volume_norm=excluded.volume_norm,
            sma_20_norm=excluded.sma_20_norm,
            rsi_14_norm=excluded.rsi_14_norm,
            macd_norm=excluded.macd_norm,
            macd_signal_norm=excluded.macd_signal_norm,
            bollinger_upper_norm=excluded.bollinger_upper_norm,
            bollinger_lower_norm=excluded.bollinger_lower_norm;
        """

        with sqlite3.connect(self.database_path) as connection:
            connection.executemany(query, rows)
            connection.commit()

        return len(rows)


class DataPipelineService:
    def __init__(self, provider: MarketDataProvider, repository: SQLiteFeatureRepository) -> None:
        self.provider = provider
        self.repository = repository

    def run(
        self,
        symbol: str,
        market: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> int:
        fetched = self.provider.fetch(symbol=symbol, market=market, start_date=start_date, end_date=end_date)
        cleaned = clean_ohlcv(fetched)
        featured = calculate_indicators(cleaned)
        normalized = normalize_rows(featured)
        return self.repository.upsert(normalized)
