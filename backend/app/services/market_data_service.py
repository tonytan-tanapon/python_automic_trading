from ib_insync import Stock
from app.services.ib_client import connect_ib


def get_price(symbol: str):

    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")

    ib.qualifyContracts(contract)

    ticker = ib.reqMktData(contract)

    ib.sleep(1)

    return {
        "symbol": symbol,
        "bid": ticker.bid,
        "ask": ticker.ask,
        "last": ticker.last,
        "close": ticker.close
    }


def get_last_price(symbol: str) -> float | None:
    price_data = get_price(symbol)
    for field in ("last", "close", "bid", "ask"):
        value = price_data.get(field)
        if value is not None and value > 0:
            return float(value)
    return None


def get_recent_closes(symbol: str, bar_size: str = "5 mins", lookback_bars: int = 20):
    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")
    ib.qualifyContracts(contract)

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr=f"{max(lookback_bars * 2, 30)} D",
        barSizeSetting=bar_size,
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1,
    )

    closes = [bar.close for bar in bars if bar.close is not None]
    return closes[-lookback_bars:]
