from ib_insync import Stock, MarketOrder
from app.services.ib_client import connect_ib


def place_market_order(symbol: str, action: str, quantity: int):
    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")
    ib.qualifyContracts(contract)

    order = MarketOrder(action.upper(), quantity)
    trade = ib.placeOrder(contract, order)

    return {
        "symbol": symbol,
        "action": action.upper(),
        "quantity": quantity,
        "status": trade.orderStatus.status
    }


def buy_stock(symbol: str, quantity: int):
    return place_market_order(symbol, "BUY", quantity)


def sell_stock(symbol: str, quantity: int):
    return place_market_order(symbol, "SELL", quantity)
