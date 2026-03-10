from fastapi import FastAPI
from app.routers import account, positions, market, orders, market_stream

app = FastAPI(title="Auto Trading API")

app.include_router(account.router)
app.include_router(positions.router)
app.include_router(market.router)
app.include_router(orders.router)
app.include_router(market_stream.router)

@app.get("/")
def root():
    return {"status": "running"}