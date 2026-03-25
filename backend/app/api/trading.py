from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.trade import AutoTradeSetting, TradeOrder
from app.models.user import User
from app.schemas.trading import (
    AutoTradeActivityResponse,
    AutoTradeConfigRequest,
    AutoTradeConfigResponse,
    AutoTradeToggleRequest,
    AutoTradeToggleResponse,
    OrderCreateRequest,
    OrderResponse,
)
from app.services.auto_trade_runner import auto_trade_runner
from app.services.trading_engine import OrderRequest, OrderSide, OrderType
from app.services.trading_runtime import engine

router = APIRouter(prefix="/trading", tags=["trading"])


@router.get("/auto-trade", response_model=AutoTradeToggleResponse)
def get_auto_trade_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AutoTradeToggleResponse:
    setting = db.query(AutoTradeSetting).filter(AutoTradeSetting.user_id == user.id).first()
    enabled = setting.enabled if setting is not None else False
    auto_trade_runner.set_user_enabled(user.id, enabled)
    return AutoTradeToggleResponse(enabled=enabled)


@router.get("/auto-trade/config", response_model=AutoTradeConfigResponse)
def get_auto_trade_config(
    user: User = Depends(get_current_user),
) -> AutoTradeConfigResponse:
    config = auto_trade_runner.get_user_config(user.id)
    return AutoTradeConfigResponse(**config)


@router.post("/auto-trade/config", response_model=AutoTradeConfigResponse)
def set_auto_trade_config(
    payload: AutoTradeConfigRequest,
    user: User = Depends(get_current_user),
) -> AutoTradeConfigResponse:
    config = auto_trade_runner.set_user_config(
        user.id,
        {
            "strategy": payload.strategy,
            "symbols": [symbol.upper() for symbol in payload.symbols],
            "quantity": payload.quantity,
            "interval_seconds": payload.interval_seconds,
            "max_loss_pct": payload.max_loss_pct,
        },
    )
    return AutoTradeConfigResponse(**config)


@router.get("/auto-trade/activity", response_model=AutoTradeActivityResponse)
def get_auto_trade_activity(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AutoTradeActivityResponse:
    setting = db.query(AutoTradeSetting).filter(AutoTradeSetting.user_id == user.id).first()
    enabled = setting.enabled if setting is not None else False
    auto_trade_runner.set_user_enabled(user.id, enabled)
    activity = auto_trade_runner.get_user_activity(user.id)
    config = auto_trade_runner.get_user_config(user.id)
    return AutoTradeActivityResponse(
        enabled=enabled,
        running=activity["running"],
        strategy=config["strategy"],
        symbols=config["symbols"],
        quantity=config["quantity"],
        interval_seconds=config["interval_seconds"],
        next_run_in_seconds=activity.get("next_run_in_seconds"),
        last_run_at=activity["last_run_at"],
        last_action=activity["last_action"],
        last_symbol=activity["last_symbol"],
        last_signal=activity["last_signal"],
        last_message=activity["last_message"],
        recent_logs=activity.get("recent_logs", []),
    )


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
    auto_trade_runner.set_user_enabled(user.id, payload.enabled)
    return AutoTradeToggleResponse(enabled=payload.enabled)
