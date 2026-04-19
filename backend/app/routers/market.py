from fastapi import APIRouter, Query
from app.services.market_data_service import get_historical_table, get_price

router = APIRouter(prefix="/price", tags=["Market"])


@router.get("/history")
def price_history(
    symbols: str | None = None,
    bar_size: str | None = None,
    lookback_bars: int | None = Query(default=None, ge=1, le=200),
    sma_window: int | None = Query(default=None, ge=1, le=100),
):
    parsed_symbols = [item.strip().upper() for item in symbols.split(",")] if symbols else None
    return get_historical_table(
        symbols=parsed_symbols,
        bar_size=bar_size or "5 mins",
        lookback_bars=lookback_bars or 20,
        sma_window=sma_window or 5,
    )


@router.get("/{symbol}")
def price(symbol: str):
    return get_price(symbol)
