from app.services.ib_client import ib_call
from app.services.contracts import build_contract, format_symbol, is_forex_symbol


def get_price(symbol: str):
    def _get_price(ib):
        contract = build_contract(symbol)
        ib.qualifyContracts(contract)
        ticker = ib.reqMktData(contract)
        ib.sleep(1)
        return {
            "symbol": format_symbol(symbol),
            "bid": ticker.bid,
            "ask": ticker.ask,
            "last": ticker.last,
            "close": ticker.close,
        }

    return ib_call(_get_price)


def get_last_price(symbol: str) -> float | None:
    price_data = get_price(symbol)
    for field in ("last", "close", "bid", "ask"):
        value = price_data.get(field)
        if value is not None and value > 0:
            return float(value)
    return None


def get_recent_closes(symbol: str, bar_size: str = "5 mins", lookback_bars: int = 20):
    def _get_recent_closes(ib):
        contract = build_contract(symbol)
        ib.qualifyContracts(contract)
        what_to_show = "MIDPOINT" if is_forex_symbol(symbol) else "TRADES"
        use_rth = False if is_forex_symbol(symbol) else True

        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=f"{max(lookback_bars * 2, 30)} D",
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=use_rth,
            formatDate=1,
        )

        closes = [bar.close for bar in bars if bar.close is not None]
        return closes[-lookback_bars:]

    return ib_call(_get_recent_closes)
