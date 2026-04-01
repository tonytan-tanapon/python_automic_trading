from app.services.ib_client import connect_ib


def get_positions():

    ib = connect_ib()

    positions = ib.positions()

    result = []

    for p in positions:

        result.append({
            "symbol": p.contract.symbol,
            "secType": p.contract.secType,
            "exchange": p.contract.exchange,
            "position": p.position,
            "avgCost": p.avgCost
        })

    return result


def get_symbol_position(symbol: str) -> float:
    positions = get_positions()

    for position in positions:
        if position["symbol"].upper() == symbol.upper():
            return float(position["position"])

    return 0.0


def get_symbol_position_details(symbol: str) -> dict:
    positions = get_positions()

    for position in positions:
        if position["symbol"].upper() == symbol.upper():
            return {
                "symbol": position["symbol"],
                "position": float(position["position"]),
                "avgCost": float(position["avgCost"]),
                "exchange": position["exchange"],
                "secType": position["secType"],
            }

    return {
        "symbol": symbol.upper(),
        "position": 0.0,
        "avgCost": 0.0,
        "exchange": "SMART",
        "secType": "STK",
    }
