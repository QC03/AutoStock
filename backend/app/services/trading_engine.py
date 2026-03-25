from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None


@dataclass
class ExecutedOrder:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    executed_price: float
    status: OrderStatus
    executed_at: str
    reason: str = ""


@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
    market_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.market_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.market_price - self.avg_price) * self.quantity


@dataclass
class PortfolioSnapshot:
    cash: float
    positions: list[dict[str, float | int | str]]
    total_value: float
    total_unrealized_pnl: float


class BrokerClient(Protocol):
    def get_quote(self, symbol: str) -> float:
        ...

    def place_order(self, request: OrderRequest) -> ExecutedOrder:
        ...


class MockBrokerClient:
    def __init__(self, quotes: dict[str, float] | None = None) -> None:
        self.quotes = quotes or {}
        self._counter = 0

    def set_quote(self, symbol: str, price: float) -> None:
        self.quotes[symbol] = price

    def get_quote(self, symbol: str) -> float:
        if symbol not in self.quotes:
            raise ValueError(f"시세가 없습니다: {symbol}")
        return self.quotes[symbol]

    def place_order(self, request: OrderRequest) -> ExecutedOrder:
        self._counter += 1
        now = dt.datetime.now().isoformat()
        order_id = f"MOCK-{self._counter:06d}"

        quote = self.get_quote(request.symbol)

        if request.order_type == OrderType.LIMIT:
            if request.limit_price is None or request.limit_price <= 0:
                return ExecutedOrder(
                    order_id=order_id,
                    symbol=request.symbol,
                    side=request.side,
                    quantity=request.quantity,
                    order_type=request.order_type,
                    executed_price=0.0,
                    status=OrderStatus.REJECTED,
                    executed_at=now,
                    reason="유효한 지정가(limit_price)가 필요합니다.",
                )

            if request.side == OrderSide.BUY and quote > request.limit_price:
                return ExecutedOrder(
                    order_id=order_id,
                    symbol=request.symbol,
                    side=request.side,
                    quantity=request.quantity,
                    order_type=request.order_type,
                    executed_price=0.0,
                    status=OrderStatus.REJECTED,
                    executed_at=now,
                    reason="지정가보다 현재가가 높아 체결되지 않았습니다.",
                )

            if request.side == OrderSide.SELL and quote < request.limit_price:
                return ExecutedOrder(
                    order_id=order_id,
                    symbol=request.symbol,
                    side=request.side,
                    quantity=request.quantity,
                    order_type=request.order_type,
                    executed_price=0.0,
                    status=OrderStatus.REJECTED,
                    executed_at=now,
                    reason="지정가보다 현재가가 낮아 체결되지 않았습니다.",
                )

            executed_price = request.limit_price
        else:
            executed_price = quote

        return ExecutedOrder(
            order_id=order_id,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            executed_price=executed_price,
            status=OrderStatus.FILLED,
            executed_at=now,
        )


@dataclass
class RiskPolicy:
    max_trade_value: float = 20000.0
    max_daily_loss: float = 5000.0
    stop_loss_pct: float = 0.05


@dataclass
class RiskManager:
    policy: RiskPolicy
    realized_pnl_today: float = 0.0

    def validate_order(self, request: OrderRequest, current_price: float) -> None:
        trade_value = request.quantity * current_price
        if trade_value > self.policy.max_trade_value:
            raise ValueError("주문 금액이 최대 한도를 초과했습니다.")

        if abs(self.realized_pnl_today) >= self.policy.max_daily_loss and self.realized_pnl_today < 0:
            raise ValueError("일일 최대 손실 한도에 도달하여 주문이 차단되었습니다.")

    def should_force_stop_loss(self, position: Position) -> bool:
        if position.quantity <= 0 or position.avg_price <= 0:
            return False
        loss_pct = (position.market_price - position.avg_price) / position.avg_price
        return loss_pct <= -self.policy.stop_loss_pct


@dataclass
class PortfolioManager:
    initial_cash: float = 100000.0
    cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.cash = self.initial_cash

    def update_market_price(self, symbol: str, price: float) -> None:
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        self.positions[symbol].market_price = price

    def apply_fill(self, fill: ExecutedOrder) -> None:
        if fill.status != OrderStatus.FILLED:
            return

        if fill.symbol not in self.positions:
            self.positions[fill.symbol] = Position(symbol=fill.symbol)

        position = self.positions[fill.symbol]
        position.market_price = fill.executed_price

        if fill.side == OrderSide.BUY:
            cost = fill.executed_price * fill.quantity
            if cost > self.cash:
                raise ValueError("현금 잔고가 부족합니다.")

            new_qty = position.quantity + fill.quantity
            if new_qty <= 0:
                raise ValueError("잘못된 수량 계산입니다.")

            total_cost = position.avg_price * position.quantity + cost
            position.quantity = new_qty
            position.avg_price = total_cost / new_qty
            self.cash -= cost

        elif fill.side == OrderSide.SELL:
            if fill.quantity > position.quantity:
                raise ValueError("보유 수량보다 많은 매도 주문입니다.")

            revenue = fill.executed_price * fill.quantity
            position.quantity -= fill.quantity
            self.cash += revenue
            if position.quantity == 0:
                position.avg_price = 0.0

    def snapshot(self) -> PortfolioSnapshot:
        positions_view: list[dict[str, float | int | str]] = []
        total_value = self.cash
        total_unrealized_pnl = 0.0

        for position in self.positions.values():
            if position.quantity <= 0:
                continue
            market_value = position.market_value
            pnl = position.unrealized_pnl
            total_value += market_value
            total_unrealized_pnl += pnl
            positions_view.append(
                {
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "avg_price": round(position.avg_price, 6),
                    "market_price": round(position.market_price, 6),
                    "market_value": round(market_value, 6),
                    "unrealized_pnl": round(pnl, 6),
                }
            )

        return PortfolioSnapshot(
            cash=round(self.cash, 6),
            positions=positions_view,
            total_value=round(total_value, 6),
            total_unrealized_pnl=round(total_unrealized_pnl, 6),
        )


class TradingEngine:
    def __init__(
        self,
        broker: BrokerClient,
        portfolio: PortfolioManager,
        risk_manager: RiskManager,
    ) -> None:
        self.broker = broker
        self.portfolio = portfolio
        self.risk_manager = risk_manager

    def execute_order(self, request: OrderRequest) -> ExecutedOrder:
        current_price = self.broker.get_quote(request.symbol)
        self.risk_manager.validate_order(request, current_price)

        executed = self.broker.place_order(request)
        if executed.status == OrderStatus.FILLED:
            self.portfolio.apply_fill(executed)
        return executed

    def refresh_prices(self, symbols: list[str]) -> None:
        for symbol in symbols:
            price = self.broker.get_quote(symbol)
            self.portfolio.update_market_price(symbol, price)

    def enforce_stop_losses(self) -> list[ExecutedOrder]:
        forced_orders: list[ExecutedOrder] = []
        for position in list(self.portfolio.positions.values()):
            if position.quantity <= 0:
                continue

            latest = self.broker.get_quote(position.symbol)
            self.portfolio.update_market_price(position.symbol, latest)

            if self.risk_manager.should_force_stop_loss(position):
                sell_request = OrderRequest(
                    symbol=position.symbol,
                    side=OrderSide.SELL,
                    quantity=position.quantity,
                    order_type=OrderType.MARKET,
                )
                forced_orders.append(self.execute_order(sell_request))

        return forced_orders

    def get_portfolio_snapshot(self) -> PortfolioSnapshot:
        return self.portfolio.snapshot()
