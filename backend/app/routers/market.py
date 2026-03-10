from fastapi import APIRouter
from app.services.market_data_service import get_price

router = APIRouter(prefix="/price", tags=["Market"])

@router.get("/{symbol}")
def price(symbol: str):
    return get_price(symbol)