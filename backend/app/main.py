from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import account, auto_trading, market, market_stream, orders, positions, trades
from app.services.auto_trading_service import auto_trading_engine

app = FastAPI(title="Auto Trading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(auto_trading.router)
app.include_router(positions.router)
app.include_router(market.router)
app.include_router(orders.router)
app.include_router(market_stream.router)
app.include_router(trades.router)


@app.on_event("startup")
async def startup_event():
    init_db()
    await auto_trading_engine.startup()


@app.on_event("shutdown")
async def shutdown_event():
    await auto_trading_engine.shutdown()

@app.get("/")
def root():
    return {"status": "running"}
