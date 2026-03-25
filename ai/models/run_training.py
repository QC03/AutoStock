from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai.models.training_pipeline import run_training_pipeline


def _with_korean_comments(summary: dict[str, object]) -> dict[str, object]:
    comments = {
        "dataset": {
            "total_samples": "전체 학습 샘플 수",
            "train": "학습 데이터 수",
            "validation": "검증 데이터 수",
            "test": "테스트 데이터 수",
        },
        "metrics": {
            "accuracy": "정확도(예측 방향 일치 비율)",
            "win_rate": "승률(매수 시그널 중 수익 발생 비율)",
            "sharpe_ratio": "샤프 지수(위험 대비 수익)",
            "max_drawdown": "최대 낙폭(MDD)",
            "trade_count": "매수 거래 발생 횟수",
            "baseline_validation": "베이스라인(이동평균 룰) 검증 성능",
            "baseline_test": "베이스라인(이동평균 룰) 테스트 성능",
            "ml_validation": "머신러닝 모델 검증 성능",
            "ml_test": "머신러닝 모델 테스트 성능",
        },
        "artifacts": {
            "model_path": "저장된 모델 버전 파일 경로",
            "signals_path": "생성된 매수/매도 신호 파일 경로",
        },
    }

    return {
        "_comment_kr": comments,
        **summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="3단계 AI 학습 파이프라인 실행")
    parser.add_argument("--db-path", default=str(Path("backend") / "data" / "market_data.db"))
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--market", default="US")
    parser.add_argument("--model-output", default=str(Path("ai") / "models" / "artifacts"))
    parser.add_argument("--signal-output", default=str(Path("ai") / "signals" / "generated"))

    args = parser.parse_args()

    result = run_training_pipeline(
        database_path=args.db_path,
        symbol=args.symbol,
        market=args.market,
        model_output_dir=args.model_output,
        signal_output_dir=args.signal_output,
    )

    annotated_summary = _with_korean_comments(result.summary)
    print(json.dumps(annotated_summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
