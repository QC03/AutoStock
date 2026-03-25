from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from app.services.data_pipeline import (
    DataPipelineService,
    SQLiteFeatureRepository,
    build_provider,
)


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="OHLCV 수집/전처리/저장 파이프라인 실행")
    parser.add_argument("--provider", default="dummy", choices=["dummy", "yfinance"])
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--market", default="US")
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2024-03-31")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parents[1] / "data" / "market_data.db"),
    )

    args = parser.parse_args()

    provider = build_provider(args.provider)
    repository = SQLiteFeatureRepository(args.db_path)
    service = DataPipelineService(provider=provider, repository=repository)

    saved_count = service.run(
        symbol=args.symbol,
        market=args.market,
        start_date=_parse_date(args.start),
        end_date=_parse_date(args.end),
    )

    print(f"saved_rows={saved_count}; db={args.db_path}")


if __name__ == "__main__":
    main()
