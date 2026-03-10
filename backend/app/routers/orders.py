from fastapi import APIRouter
from app.services.order_service import buy_stock, sell_stock

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/buy")
def buy(symbol: str, qty: int):
    return buy_stock(symbol, qty)


@router.post("/sell")
def sell(symbol: str, qty: int):
    return sell_stock(symbol, qty)