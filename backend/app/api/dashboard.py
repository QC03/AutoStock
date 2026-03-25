from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.trade import TradeOrder
from app.models.user import User
from app.schemas.dashboard import PerformanceResponse, PortfolioResponse, TradeHistoryItem
from app.services.trading_runtime import engine

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(user: User = Depends(get_current_user)) -> PortfolioResponse:
    _ = user
    snapshot = engine.get_portfolio_snapshot()
    return PortfolioResponse(
        cash=snapshot.cash,
        total_value=snapshot.total_value,
        total_unrealized_pnl=snapshot.total_unrealized_pnl,
        positions=snapshot.positions,
    )


@router.get("/trades", response_model=list[TradeHistoryItem])
def get_trade_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TradeHistoryItem]:
    orders = (
        db.query(TradeOrder)
        .filter(TradeOrder.user_id == user.id)
        .order_by(TradeOrder.id.desc())
        .limit(100)
        .all()
    )

    return [
        TradeHistoryItem(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            status=order.status,
            created_at=order.created_at.isoformat(),
        )
        for order in orders
    ]


@router.get("/performance", response_model=PerformanceResponse)
def get_performance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PerformanceResponse:
    orders = db.query(TradeOrder).filter(TradeOrder.user_id == user.id).all()
    buy_count = sum(1 for order in orders if order.side == "BUY")
    sell_count = sum(1 for order in orders if order.side == "SELL")
    notional = sum(order.price * order.quantity for order in orders)

    return PerformanceResponse(
        order_count=len(orders),
        buy_count=buy_count,
        sell_count=sell_count,
        notional=round(notional, 6),
    )
