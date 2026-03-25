from __future__ import annotations

import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.trade import AutoTradeSetting, TradeOrder
from app.services.trading_engine import OrderRequest, OrderSide, OrderType
from app.services.trading_runtime import engine

SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA"]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_config() -> dict[str, object]:
    return {
        "strategy": "rsi_macd",
        "symbols": SYMBOLS.copy(),
        "quantity": 1,
        "interval_seconds": 10,
        "max_loss_pct": 5.0,
    }


def _default_activity() -> dict[str, object | None]:
    return {
        "running": False,
        "last_run_at": None,
        "last_action": None,
        "last_symbol": None,
        "last_signal": None,
        "last_message": None,
    }


def _load_indicators(symbol: str) -> dict[str, float] | None:
    db_path = Path(__file__).resolve().parents[3] / "data" / "market_data.db"
    if not db_path.exists():
        return None

    query = """
    SELECT rsi_14, macd, macd_signal
    FROM market_features
    WHERE symbol = ?
    ORDER BY trade_date DESC
    LIMIT 1;
    """

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(query, (symbol,)).fetchone()

    if row is None:
        return None
    return {
        "rsi_14": float(row[0]),
        "macd": float(row[1]),
        "macd_signal": float(row[2]),
    }


def _signal_from_indicators(strategy: str, indicators: dict[str, float] | None) -> str:
    if indicators is None:
        return "HOLD"

    rsi = indicators["rsi_14"]
    macd = indicators["macd"]
    macd_signal = indicators["macd_signal"]

    if strategy == "momentum":
        if macd > macd_signal:
            return "BUY"
        if macd < macd_signal:
            return "SELL"
        return "HOLD"

    if strategy == "mean_reversion":
        if rsi < 35:
            return "BUY"
        if rsi > 65:
            return "SELL"
        return "HOLD"

    if rsi < 30:
        return "BUY"
    if rsi > 70:
        return "SELL"
    return "HOLD"


class AutoTradeRunner:
    def __init__(self, interval_seconds: float = 10.0) -> None:
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_signal_by_user_symbol: dict[tuple[int, str], str] = {}
        self._user_config: dict[int, dict[str, object]] = {}
        self._user_activity: dict[int, dict[str, object | None]] = {}
        self._next_run_at: dict[int, float] = {}
        self._enabled_state: dict[int, bool] = {}
        self._lock = threading.Lock()

    def get_user_config(self, user_id: int) -> dict[str, object]:
        with self._lock:
            if user_id not in self._user_config:
                self._user_config[user_id] = _default_config()
            return dict(self._user_config[user_id])

    def set_user_config(self, user_id: int, payload: dict[str, object]) -> dict[str, object]:
        with self._lock:
            current = self._user_config.get(user_id, _default_config())
            current.update(payload)
            current["symbols"] = [str(symbol).upper() for symbol in list(current.get("symbols", SYMBOLS))]
            current["quantity"] = max(1, int(current.get("quantity", 1)))
            current["interval_seconds"] = max(3, int(current.get("interval_seconds", 10)))
            current["max_loss_pct"] = float(current.get("max_loss_pct", 5.0))
            self._user_config[user_id] = current
            self._next_run_at[user_id] = 0.0
            return dict(current)

    def set_user_enabled(self, user_id: int, enabled: bool) -> None:
        with self._lock:
            self._enabled_state[user_id] = enabled
            if user_id not in self._user_activity:
                self._user_activity[user_id] = _default_activity()
            self._user_activity[user_id]["running"] = enabled
            self._user_activity[user_id]["last_action"] = "ON" if enabled else "OFF"
            self._user_activity[user_id]["last_message"] = "자동매매 시작" if enabled else "자동매매 중지"
            self._user_activity[user_id]["last_run_at"] = _utc_now_iso()
            if not enabled:
                self._next_run_at[user_id] = 0.0

    def get_user_activity(self, user_id: int) -> dict[str, object | None]:
        with self._lock:
            if user_id not in self._user_activity:
                self._user_activity[user_id] = _default_activity()
            activity = dict(self._user_activity[user_id])
            activity["running"] = bool(self._enabled_state.get(user_id, False))
            return activity

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception:
                pass
            time.sleep(self.interval_seconds)

    def run_once(self) -> None:
        db: Session = SessionLocal()
        try:
            enabled_settings = (
                db.query(AutoTradeSetting)
                .filter(AutoTradeSetting.enabled.is_(True))
                .all()
            )

            for setting in enabled_settings:
                user_id = setting.user_id
                self.set_user_enabled(user_id, True)

                config = self.get_user_config(user_id)
                strategy = str(config.get("strategy", "rsi_macd"))
                symbols = [str(symbol).upper() for symbol in list(config.get("symbols", SYMBOLS))]
                quantity = max(1, int(config.get("quantity", 1)))
                interval_seconds = max(3, int(config.get("interval_seconds", 10)))

                now_ts = time.time()
                next_run_at = self._next_run_at.get(user_id, 0.0)
                if now_ts < next_run_at:
                    continue
                self._next_run_at[user_id] = now_ts + interval_seconds

                with self._lock:
                    if user_id not in self._user_activity:
                        self._user_activity[user_id] = _default_activity()
                    self._user_activity[user_id]["running"] = True
                    self._user_activity[user_id]["last_run_at"] = _utc_now_iso()
                    self._user_activity[user_id]["last_message"] = "신호 계산 중"

                for symbol in symbols:
                    indicators = _load_indicators(symbol)
                    signal = _signal_from_indicators(strategy, indicators)
                    key = (user_id, symbol)

                    if self._last_signal_by_user_symbol.get(key) == signal:
                        continue

                    self._last_signal_by_user_symbol[key] = signal

                    if signal == "HOLD":
                        with self._lock:
                            self._user_activity[user_id]["last_symbol"] = symbol
                            self._user_activity[user_id]["last_signal"] = signal
                            self._user_activity[user_id]["last_action"] = "HOLD"
                            self._user_activity[user_id]["last_message"] = f"{symbol} HOLD"
                        continue

                    side = OrderSide.BUY if signal == "BUY" else OrderSide.SELL
                    request = OrderRequest(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type=OrderType.MARKET,
                    )

                    try:
                        result = engine.execute_order(request)
                    except Exception as error:
                        with self._lock:
                            self._user_activity[user_id]["last_symbol"] = symbol
                            self._user_activity[user_id]["last_signal"] = signal
                            self._user_activity[user_id]["last_action"] = "REJECTED"
                            self._user_activity[user_id]["last_message"] = f"{symbol} 주문 실패: {error}"
                        continue

                    order = TradeOrder(
                        user_id=user_id,
                        symbol=result.symbol,
                        side=result.side.value,
                        order_type=result.order_type.value,
                        quantity=result.quantity,
                        price=result.executed_price,
                        status=result.status.value,
                        reason="AUTO_TRADE",
                    )
                    db.add(order)

                    with self._lock:
                        self._user_activity[user_id]["last_symbol"] = symbol
                        self._user_activity[user_id]["last_signal"] = signal
                        self._user_activity[user_id]["last_action"] = result.side.value
                        self._user_activity[user_id]["last_message"] = f"{symbol} {result.side.value} {result.quantity}주"

            db.commit()
        finally:
            db.close()


auto_trade_runner = AutoTradeRunner()
