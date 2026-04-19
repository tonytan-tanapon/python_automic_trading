from app.services.ib_client import ib_call
from app.services.contracts import contract_symbol, format_symbol, is_forex_symbol, normalize_symbol


def get_positions():
    def _get_positions(ib):
        positions = ib.positions()
        result = []

        for p in positions:
            result.append({
                "symbol": contract_symbol(p.contract),
                "secType": p.contract.secType,
                "exchange": p.contract.exchange,
                "position": p.position,
                "avgCost": p.avgCost,
            })

        return result

    return ib_call(_get_positions)


def get_symbol_position(symbol: str) -> float:
    positions = get_positions()
    target_symbol = normalize_symbol(symbol)

    for position in positions:
        if normalize_symbol(position["symbol"]) == target_symbol:
            return float(position["position"])

    return 0.0


def get_symbol_position_details(symbol: str) -> dict:
    positions = get_positions()
    target_symbol = normalize_symbol(symbol)

    for position in positions:
        if normalize_symbol(position["symbol"]) == target_symbol:
            return {
                "symbol": position["symbol"],
                "position": float(position["position"]),
                "avgCost": float(position["avgCost"]),
                "exchange": position["exchange"],
                "secType": position["secType"],
            }

    return {
        "symbol": format_symbol(symbol),
        "position": 0.0,
        "avgCost": 0.0,
        "exchange": "IDEALPRO" if is_forex_symbol(target_symbol) else "SMART",
        "secType": "CASH" if is_forex_symbol(target_symbol) else "STK",
    }
