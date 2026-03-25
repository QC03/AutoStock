from __future__ import annotations

import datetime as dt
import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ai.signals.generator import generate_signals_from_probabilities


DEFAULT_FEATURE_COLUMNS = [
    "open_norm",
    "high_norm",
    "low_norm",
    "close_norm",
    "volume_norm",
    "sma_20_norm",
    "rsi_14_norm",
    "macd_norm",
    "macd_signal_norm",
    "bollinger_upper_norm",
    "bollinger_lower_norm",
]


@dataclass
class SplitDataset:
    train: list[dict[str, float | str]]
    validation: list[dict[str, float | str]]
    test: list[dict[str, float | str]]


@dataclass
class TrainResult:
    summary: dict[str, object]
    model_path: Path
    signals_path: Path


class SimpleLogisticRegression:
    def __init__(self, learning_rate: float = 0.1, epochs: int = 500) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights: list[float] = []
        self.bias: float = 0.0

    @staticmethod
    def _sigmoid(value: float) -> float:
        if value >= 0:
            exp_neg = math.exp(-value)
            return 1.0 / (1.0 + exp_neg)
        exp_pos = math.exp(value)
        return exp_pos / (1.0 + exp_pos)

    def fit(self, features: list[list[float]], labels: list[int]) -> None:
        if not features:
            raise ValueError("학습 데이터가 비어 있습니다.")

        feature_count = len(features[0])
        self.weights = [0.0] * feature_count
        self.bias = 0.0

        sample_count = len(features)

        for _ in range(self.epochs):
            gradients_w = [0.0] * feature_count
            gradient_b = 0.0

            for row, label in zip(features, labels):
                linear = self.bias + sum(weight * value for weight, value in zip(self.weights, row))
                prediction = self._sigmoid(linear)
                error = prediction - label

                for index in range(feature_count):
                    gradients_w[index] += error * row[index]
                gradient_b += error

            for index in range(feature_count):
                self.weights[index] -= self.learning_rate * gradients_w[index] / sample_count
            self.bias -= self.learning_rate * gradient_b / sample_count

    def predict_proba(self, features: list[list[float]]) -> list[float]:
        probabilities: list[float] = []
        for row in features:
            linear = self.bias + sum(weight * value for weight, value in zip(self.weights, row))
            probabilities.append(self._sigmoid(linear))
        return probabilities

    def predict(self, features: list[list[float]], threshold: float = 0.5) -> list[int]:
        probabilities = self.predict_proba(features)
        return [1 if probability >= threshold else 0 for probability in probabilities]

    def to_dict(self) -> dict[str, object]:
        return {
            "weights": self.weights,
            "bias": self.bias,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
        }


def load_feature_rows(
    database_path: str | Path,
    symbol: str,
    market: str,
) -> list[dict[str, float | str]]:
    query = """
    SELECT
        trade_date,
        close,
        sma_20,
        open_norm,
        high_norm,
        low_norm,
        close_norm,
        volume_norm,
        sma_20_norm,
        rsi_14_norm,
        macd_norm,
        macd_signal_norm,
        bollinger_upper_norm,
        bollinger_lower_norm
    FROM market_features
    WHERE symbol = ? AND market = ?
    ORDER BY trade_date ASC;
    """

    rows: list[dict[str, float | str]] = []
    with sqlite3.connect(database_path) as connection:
        for item in connection.execute(query, (symbol, market)).fetchall():
            rows.append(
                {
                    "trade_date": str(item[0]),
                    "close": float(item[1]),
                    "sma_20": float(item[2]),
                    "open_norm": float(item[3]),
                    "high_norm": float(item[4]),
                    "low_norm": float(item[5]),
                    "close_norm": float(item[6]),
                    "volume_norm": float(item[7]),
                    "sma_20_norm": float(item[8]),
                    "rsi_14_norm": float(item[9]),
                    "macd_norm": float(item[10]),
                    "macd_signal_norm": float(item[11]),
                    "bollinger_upper_norm": float(item[12]),
                    "bollinger_lower_norm": float(item[13]),
                }
            )

    if len(rows) < 30:
        raise ValueError("학습에 필요한 데이터가 부족합니다. 최소 30건 이상 필요합니다.")

    return rows


def build_supervised_samples(
    rows: list[dict[str, float | str]],
    feature_columns: list[str],
) -> list[dict[str, float | str]]:
    samples: list[dict[str, float | str]] = []

    for index in range(len(rows) - 1):
        current = rows[index]
        next_row = rows[index + 1]

        current_close = float(current["close"])
        next_close = float(next_row["close"])
        next_return = (next_close - current_close) / current_close if current_close != 0 else 0.0
        target = 1 if next_close > current_close else 0
        baseline_prediction = 1 if float(current["close"]) > float(current["sma_20"]) else 0

        sample: dict[str, float | str] = {
            "trade_date": str(current["trade_date"]),
            "target": target,
            "next_return": next_return,
            "baseline_prediction": baseline_prediction,
        }

        for feature in feature_columns:
            sample[feature] = float(current[feature])

        samples.append(sample)

    return samples


def split_dataset_time_series(
    samples: list[dict[str, float | str]],
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
) -> SplitDataset:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio는 0과 1 사이여야 합니다.")
    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio는 0과 1 사이여야 합니다.")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("train_ratio + validation_ratio는 1보다 작아야 합니다.")

    total = len(samples)
    train_end = int(total * train_ratio)
    validation_end = train_end + int(total * validation_ratio)

    if train_end < 10 or validation_end <= train_end or validation_end >= total:
        raise ValueError("분할 후 train/validation/test 크기가 유효하지 않습니다.")

    return SplitDataset(
        train=samples[:train_end],
        validation=samples[train_end:validation_end],
        test=samples[validation_end:],
    )


def _to_matrix(
    samples: list[dict[str, float | str]],
    feature_columns: list[str],
) -> tuple[list[list[float]], list[int], list[float]]:
    features = [[float(sample[column]) for column in feature_columns] for sample in samples]
    labels = [int(sample["target"]) for sample in samples]
    returns = [float(sample["next_return"]) for sample in samples]
    return features, labels, returns


def calculate_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for truth, pred in zip(y_true, y_pred) if truth == pred)
    return correct / len(y_true)


def calculate_win_rate(predictions: list[int], next_returns: list[float]) -> float:
    trade_results = [result for prediction, result in zip(predictions, next_returns) if prediction == 1]
    if not trade_results:
        return 0.0
    wins = sum(1 for result in trade_results if result > 0)
    return wins / len(trade_results)


def calculate_sharpe_ratio(strategy_returns: list[float], risk_free_rate_daily: float = 0.0) -> float:
    if not strategy_returns:
        return 0.0

    excess_returns = [value - risk_free_rate_daily for value in strategy_returns]
    mean = sum(excess_returns) / len(excess_returns)
    variance = sum((value - mean) ** 2 for value in excess_returns) / len(excess_returns)
    std = math.sqrt(variance)

    if std == 0:
        return 0.0
    return (mean / std) * math.sqrt(252)


def calculate_max_drawdown(strategy_returns: list[float]) -> float:
    if not strategy_returns:
        return 0.0

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for daily_return in strategy_returns:
        equity *= 1.0 + daily_return
        peak = max(peak, equity)
        drawdown = (equity - peak) / peak
        max_drawdown = min(max_drawdown, drawdown)

    return abs(max_drawdown)


def evaluate_predictions(
    labels: list[int],
    predictions: list[int],
    next_returns: list[float],
) -> dict[str, float]:
    strategy_returns = [prediction * next_return for prediction, next_return in zip(predictions, next_returns)]

    return {
        "accuracy": round(calculate_accuracy(labels, predictions), 6),
        "win_rate": round(calculate_win_rate(predictions, next_returns), 6),
        "sharpe_ratio": round(calculate_sharpe_ratio(strategy_returns), 6),
        "max_drawdown": round(calculate_max_drawdown(strategy_returns), 6),
        "trade_count": float(sum(1 for prediction in predictions if prediction == 1)),
    }


def save_model_version(
    model: SimpleLogisticRegression,
    feature_columns: list[str],
    output_dir: str | Path,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = output_path / f"model_{timestamp}.json"

    payload = {
        "created_at": dt.datetime.now().isoformat(),
        "feature_columns": feature_columns,
        "model": model.to_dict(),
    }

    model_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return model_path


def save_signals(
    trade_dates: list[str],
    probabilities: list[float],
    signals: list[str],
    output_dir: str | Path,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    signals_path = output_path / f"signals_{timestamp}.json"

    rows = [
        {
            "trade_date": trade_date,
            "probability": round(probability, 6),
            "signal": signal,
        }
        for trade_date, probability, signal in zip(trade_dates, probabilities, signals)
    ]

    signals_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return signals_path


def run_training_pipeline(
    database_path: str | Path,
    symbol: str,
    market: str,
    model_output_dir: str | Path,
    signal_output_dir: str | Path,
    feature_columns: list[str] | None = None,
) -> TrainResult:
    columns = feature_columns or DEFAULT_FEATURE_COLUMNS

    raw_rows = load_feature_rows(database_path=database_path, symbol=symbol, market=market)
    samples = build_supervised_samples(rows=raw_rows, feature_columns=columns)
    split = split_dataset_time_series(samples=samples)

    train_x, train_y, _ = _to_matrix(split.train, columns)
    val_x, val_y, val_returns = _to_matrix(split.validation, columns)
    test_x, test_y, test_returns = _to_matrix(split.test, columns)

    baseline_val_predictions = [int(sample["baseline_prediction"]) for sample in split.validation]
    baseline_test_predictions = [int(sample["baseline_prediction"]) for sample in split.test]

    model = SimpleLogisticRegression(learning_rate=0.25, epochs=600)
    model.fit(train_x, train_y)

    val_predictions = model.predict(val_x)
    test_predictions = model.predict(test_x)
    test_probabilities = model.predict_proba(test_x)

    signals = generate_signals_from_probabilities(test_probabilities)

    model_path = save_model_version(model=model, feature_columns=columns, output_dir=model_output_dir)
    signals_path = save_signals(
        trade_dates=[str(sample["trade_date"]) for sample in split.test],
        probabilities=test_probabilities,
        signals=signals,
        output_dir=signal_output_dir,
    )

    summary: dict[str, object] = {
        "dataset": {
            "total_samples": len(samples),
            "train": len(split.train),
            "validation": len(split.validation),
            "test": len(split.test),
        },
        "metrics": {
            "baseline_validation": evaluate_predictions(val_y, baseline_val_predictions, val_returns),
            "baseline_test": evaluate_predictions(test_y, baseline_test_predictions, test_returns),
            "ml_validation": evaluate_predictions(val_y, val_predictions, val_returns),
            "ml_test": evaluate_predictions(test_y, test_predictions, test_returns),
        },
        "artifacts": {
            "model_path": str(model_path),
            "signals_path": str(signals_path),
        },
    }

    return TrainResult(summary=summary, model_path=model_path, signals_path=signals_path)
