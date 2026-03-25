from __future__ import annotations


def generate_signals_from_probabilities(
    probabilities: list[float],
    buy_threshold: float = 0.55,
    sell_threshold: float = 0.45,
) -> list[str]:
    signals: list[str] = []
    for probability in probabilities:
        if probability >= buy_threshold:
            signals.append("BUY")
        elif probability <= sell_threshold:
            signals.append("SELL")
        else:
            signals.append("HOLD")
    return signals
