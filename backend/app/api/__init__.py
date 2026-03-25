from fastapi import APIRouter

from app.api import auth, dashboard, data, trading, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(data.router)
api_router.include_router(trading.router)
api_router.include_router(dashboard.router)
api_router.include_router(ws.router)

__all__ = ["api_router"]
