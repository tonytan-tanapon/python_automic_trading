from fastapi import APIRouter

from app.services.trade_log_service import get_recent_trades

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("/")
def list_trades(limit: int = 50):
    return get_recent_trades(limit=limit)
