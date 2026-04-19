from ib_insync import MarketOrder
from app.services.ib_client import ib_call
from app.services.contracts import build_contract, format_symbol


def get_orders():
    def _get_orders(ib):
        result = []

        for trade in ib.openTrades():
            contract = trade.contract
            order = trade.order
            status = trade.orderStatus
            result.append({
                "symbol": format_symbol(contract.localSymbol or contract.symbol),
                "action": order.action,
                "orderType": order.orderType,
                "quantity": order.totalQuantity,
                "status": status.status,
                "filled": status.filled,
                "remaining": status.remaining,
            })

        return result

    return ib_call(_get_orders)


def place_market_order(symbol: str, action: str, quantity: int):
    def _place_market_order(ib):
        contract = build_contract(symbol)
        ib.qualifyContracts(contract)
        order = MarketOrder(action.upper(), quantity)
        trade = ib.placeOrder(contract, order)
        return {
            "symbol": format_symbol(symbol),
            "action": action.upper(),
            "quantity": quantity,
            "status": trade.orderStatus.status,
        }

    return ib_call(_place_market_order)


def buy_stock(symbol: str, quantity: int):
    return place_market_order(symbol, "BUY", quantity)


def sell_stock(symbol: str, quantity: int):
    return place_market_order(symbol, "SELL", quantity)
