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