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