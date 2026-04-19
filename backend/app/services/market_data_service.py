from app.config import (
    AUTO_TRADING_BAR_SIZE,
    AUTO_TRADING_LOOKBACK_BARS,
    AUTO_TRADING_SHORT_WINDOW,
    AUTO_TRADING_SYMBOLS,
)
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


def get_historical_table(
    symbols: list[str] | None = None,
    bar_size: str = AUTO_TRADING_BAR_SIZE,
    lookback_bars: int = AUTO_TRADING_LOOKBACK_BARS,
    sma_window: int = AUTO_TRADING_SHORT_WINDOW,
):
    target_symbols = symbols or AUTO_TRADING_SYMBOLS

    def _get_historical_table(ib):
        history_by_symbol = {}
        all_times = set()

        for symbol in target_symbols:
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

            formatted_symbol = format_symbol(symbol)
            symbol_history = {}
            recent_closes = []

            for bar in bars[-lookback_bars:]:
                time_key = str(bar.date)
                recent_closes.append(bar.close)
                sma_value = None
                signal = "HOLD"

                if len(recent_closes) >= sma_window:
                    sma_value = sum(recent_closes[-sma_window:]) / sma_window
                    if bar.close > sma_value:
                        signal = "BUY"
                    elif bar.close < sma_value:
                        signal = "SELL"

                symbol_history[time_key] = {
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "sma": sma_value,
                    "signal": signal,
                    "volume": getattr(bar, "volume", None),
                }
                all_times.add(time_key)

            history_by_symbol[formatted_symbol] = symbol_history

        rows = []
        for time_key in sorted(all_times, reverse=True):
            row = {"time": time_key}
            for symbol in history_by_symbol:
                row[symbol] = history_by_symbol[symbol].get(time_key)
            rows.append(row)

        return {
            "symbols": [format_symbol(symbol) for symbol in target_symbols],
            "bar_size": bar_size,
            "lookback_bars": lookback_bars,
            "sma_window": sma_window,
            "rows": rows,
        }

    return ib_call(_get_historical_table)
