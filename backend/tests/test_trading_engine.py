from __future__ import annotations

from app.services.trading_engine import (
    MockBrokerClient,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
    PortfolioManager,
    RiskManager,
    RiskPolicy,
    TradingEngine,
)


def _create_engine() -> TradingEngine:
    broker = MockBrokerClient({"AAPL": 180.0, "MSFT": 420.0})
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk_manager = RiskManager(policy=RiskPolicy(max_trade_value=50000.0, max_daily_loss=5000.0, stop_loss_pct=0.05))
    return TradingEngine(broker=broker, portfolio=portfolio, risk_manager=risk_manager)


def test_market_order_buy_and_portfolio_update() -> None:
    engine = _create_engine()

    executed = engine.execute_order(
        OrderRequest(symbol="AAPL", side=OrderSide.BUY, quantity=20, order_type=OrderType.MARKET)
    )

    snapshot = engine.get_portfolio_snapshot()

    assert executed.status == OrderStatus.FILLED
    assert snapshot.cash == 96400.0
    assert snapshot.positions[0]["symbol"] == "AAPL"
    assert snapshot.positions[0]["quantity"] == 20


def test_limit_order_rejected_when_price_not_reached() -> None:
    engine = _create_engine()

    executed = engine.execute_order(
        OrderRequest(symbol="AAPL", side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT, limit_price=170.0)
    )

    assert executed.status == OrderStatus.REJECTED


def test_risk_manager_blocks_too_large_order() -> None:
    engine = _create_engine()

    try:
        engine.execute_order(OrderRequest(symbol="MSFT", side=OrderSide.BUY, quantity=200, order_type=OrderType.MARKET))
        raised = False
    except ValueError:
        raised = True

    assert raised is True


def test_stop_loss_forces_sell() -> None:
    engine = _create_engine()

    engine.execute_order(OrderRequest(symbol="AAPL", side=OrderSide.BUY, quantity=30, order_type=OrderType.MARKET))
    engine.broker.set_quote("AAPL", 165.0)

    forced_orders = engine.enforce_stop_losses()

    assert len(forced_orders) == 1
    assert forced_orders[0].side == OrderSide.SELL
    assert forced_orders[0].status == OrderStatus.FILLED

    snapshot = engine.get_portfolio_snapshot()
    assert len(snapshot.positions) == 0
