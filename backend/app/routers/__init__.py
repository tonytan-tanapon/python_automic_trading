from fastapi import APIRouter

from app.routers import account, auto_trade, auto_trading, market, market_stream, orders, positions, trades, tws

api_router = APIRouter()

api_router.include_router(account.router)
api_router.include_router(auto_trade.router)
api_router.include_router(auto_trading.router)
api_router.include_router(positions.router)
api_router.include_router(market.router)
api_router.include_router(orders.router)
api_router.include_router(market_stream.router)
api_router.include_router(trades.router)
api_router.include_router(tws.router)
