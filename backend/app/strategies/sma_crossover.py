from app.config import (
    AUTO_TRADING_BAR_SIZE,
    AUTO_TRADING_LONG_WINDOW,
    AUTO_TRADING_LOOKBACK_BARS,
    AUTO_TRADING_SHORT_WINDOW,
)
from app.services.market_data_service import get_recent_closes
from app.strategies.base import StrategyProtocol


class MovingAverageCrossoverStrategy(StrategyProtocol):
    name = "sma_crossover"

    def __init__(
        self,
        short_window: int = AUTO_TRADING_SHORT_WINDOW,
        long_window: int = AUTO_TRADING_LONG_WINDOW,
        lookback_bars: int = AUTO_TRADING_LOOKBACK_BARS,
        bar_size: str = AUTO_TRADING_BAR_SIZE,
    ):
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window")

        self.short_window = short_window
        self.long_window = long_window
        self.lookback_bars = lookback_bars
        self.bar_size = bar_size

    def evaluate(self, symbol: str) -> dict:
        closes = get_recent_closes(
            symbol=symbol,
            bar_size=self.bar_size,
            lookback_bars=self.lookback_bars,
        )

        if len(closes) < self.long_window:
            return {
                "symbol": symbol,
                "signal": "HOLD",
                "reason": "not_enough_history",
                "bars": len(closes),
            }

        short_ma = sum(closes[-self.short_window :]) / self.short_window
        long_ma = sum(closes[-self.long_window :]) / self.long_window
        previous_short_ma = sum(closes[-self.short_window - 1 : -1]) / self.short_window
        previous_long_ma = sum(closes[-self.long_window - 1 : -1]) / self.long_window

        signal = "HOLD"
        reason = "trend_unchanged"

        if previous_short_ma <= previous_long_ma and short_ma > long_ma:
            signal = "BUY"
            reason = "bullish_crossover"
        elif previous_short_ma >= previous_long_ma and short_ma < long_ma:
            signal = "SELL"
            reason = "bearish_crossover"

        return {
            "symbol": symbol,
            "signal": signal,
            "reason": reason,
            "short_ma": round(short_ma, 4),
            "long_ma": round(long_ma, 4),
            "previous_short_ma": round(previous_short_ma, 4),
            "previous_long_ma": round(previous_long_ma, 4),
            "last_close": round(closes[-1], 4),
            "bars": len(closes),
            "bar_size": self.bar_size,
        }
