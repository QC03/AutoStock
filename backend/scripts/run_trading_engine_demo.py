from __future__ import annotations

import json

from app.services.trading_engine import (
    MockBrokerClient,
    OrderRequest,
    OrderSide,
    OrderType,
    PortfolioManager,
    RiskManager,
    RiskPolicy,
    TradingEngine,
)


def main() -> None:
    broker = MockBrokerClient({"AAPL": 180.0, "MSFT": 420.0})
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk_manager = RiskManager(policy=RiskPolicy(max_trade_value=50000.0, max_daily_loss=5000.0, stop_loss_pct=0.05))
    engine = TradingEngine(broker=broker, portfolio=portfolio, risk_manager=risk_manager)

    first = engine.execute_order(OrderRequest(symbol="AAPL", side=OrderSide.BUY, quantity=50, order_type=OrderType.MARKET))
    second = engine.execute_order(OrderRequest(symbol="AAPL", side=OrderSide.SELL, quantity=10, order_type=OrderType.LIMIT, limit_price=181.0))

    broker.set_quote("AAPL", 165.0)
    forced = engine.enforce_stop_losses()

    snapshot = engine.get_portfolio_snapshot()

    print(
        json.dumps(
            {
                "orders": [first.__dict__, second.__dict__],
                "forced_stop_loss_orders": [item.__dict__ for item in forced],
                "portfolio": {
                    "cash": snapshot.cash,
                    "positions": snapshot.positions,
                    "total_value": snapshot.total_value,
                    "total_unrealized_pnl": snapshot.total_unrealized_pnl,
                },
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
