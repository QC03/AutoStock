from __future__ import annotations

from app.services.trading_engine import MockBrokerClient, PortfolioManager, RiskManager, RiskPolicy, TradingEngine


def create_runtime() -> TradingEngine:
    broker = MockBrokerClient({"AAPL": 180.0, "MSFT": 420.0, "TSLA": 210.0, "NVDA": 960.0})
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk = RiskManager(policy=RiskPolicy(max_trade_value=50000.0, max_daily_loss=5000.0, stop_loss_pct=0.05))
    return TradingEngine(broker=broker, portfolio=portfolio, risk_manager=risk)


engine = create_runtime()


def reset_runtime() -> None:
    global engine
    engine = create_runtime()
