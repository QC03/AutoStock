from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import dataclass

import httpx


@dataclass
class PerfStat:
    endpoint: str
    avg_ms: float
    p95_ms: float
    max_ms: float


def _measure(client: httpx.Client, endpoint: str, repeats: int) -> PerfStat:
    timings_ms: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        response = client.get(endpoint)
        response.raise_for_status()
        elapsed_ms = (time.perf_counter() - start) * 1000
        timings_ms.append(elapsed_ms)

    q = statistics.quantiles(timings_ms, n=100)
    return PerfStat(
        endpoint=endpoint,
        avg_ms=round(statistics.mean(timings_ms), 3),
        p95_ms=round(q[94], 3),
        max_ms=round(max(timings_ms), 3),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure stage7 API latency")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--repeats", type=int, default=20)
    args = parser.parse_args()

    endpoints = [
        "/health",
        "/data/search?query=AAPL",
        "/data/quote/AAPL",
    ]

    with httpx.Client(base_url=args.base_url, timeout=10.0) as client:
        stats = [_measure(client, endpoint, args.repeats) for endpoint in endpoints]

    print(
        json.dumps(
            {
                "base_url": args.base_url,
                "repeats": args.repeats,
                "results": [
                    {
                        "endpoint": item.endpoint,
                        "avg_ms": item.avg_ms,
                        "p95_ms": item.p95_ms,
                        "max_ms": item.max_ms,
                    }
                    for item in stats
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()