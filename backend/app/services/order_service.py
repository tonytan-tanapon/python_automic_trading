from ib_insync import Stock, MarketOrder
from app.services.ib_client import connect_ib

def buy_stock(symbol: str, quantity: int):

    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")

    ib.qualifyContracts(contract)

    order = MarketOrder("BUY", quantity)

    trade = ib.placeOrder(contract, order)

    return {
        "symbol": symbol,
        "action": "BUY",
        "quantity": quantity,
        "status": trade.orderStatus.status
    }


def sell_stock(symbol: str, quantity: int):

    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")

    ib.qualifyContracts(contract)

    order = MarketOrder("SELL", quantity)

    trade = ib.placeOrder(contract, order)

    return {
        "symbol": symbol,
        "action": "SELL",
        "quantity": quantity,
        "status": trade.orderStatus.status
    }