from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.trade import AutoTradeSetting, TradeOrder
from app.models.user import User
from app.schemas.trading import AutoTradeToggleRequest, AutoTradeToggleResponse, OrderCreateRequest, OrderResponse
from app.services.trading_engine import OrderRequest, OrderSide, OrderType
from app.services.trading_runtime import engine

router = APIRouter(prefix="/trading", tags=["trading"])


@router.post("/orders", response_model=OrderResponse)
def create_order(
    payload: OrderCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    try:
        request = OrderRequest(
            symbol=payload.symbol.upper(),
            side=OrderSide(payload.side.upper()),
            quantity=payload.quantity,
            order_type=OrderType(payload.order_type.upper()),
            limit_price=payload.limit_price,
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail="주문 파라미터가 유효하지 않습니다.") from error

    try:
        result = engine.execute_order(request)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    order = TradeOrder(
        user_id=user.id,
        symbol=result.symbol,
        side=result.side.value,
        order_type=result.order_type.value,
        quantity=result.quantity,
        price=result.executed_price,
        status=result.status.value,
        reason=result.reason,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        order_id=result.order_id,
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        status=order.status,
        reason=order.reason,
    )


@router.post("/auto-trade", response_model=AutoTradeToggleResponse)
def toggle_auto_trade(
    payload: AutoTradeToggleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AutoTradeToggleResponse:
    setting = db.query(AutoTradeSetting).filter(AutoTradeSetting.user_id == user.id).first()
    if setting is None:
        setting = AutoTradeSetting(user_id=user.id, enabled=payload.enabled)
        db.add(setting)
    else:
        setting.enabled = payload.enabled

    db.commit()
    return AutoTradeToggleResponse(enabled=payload.enabled)
