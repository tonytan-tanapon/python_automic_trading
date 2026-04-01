from app.config import (
    AUTO_TRADING_BAR_SIZE,
    AUTO_TRADING_LOOKBACK_BARS,
    AUTO_TRADING_LONG_WINDOW,
    AUTO_TRADING_MEAN_REVERSION_THRESHOLD,
)
from app.services.market_data_service import get_recent_closes
from app.strategies.base import StrategyProtocol


class MeanReversionStrategy(StrategyProtocol):
    name = "mean_reversion"

    def __init__(
        self,
        moving_average_window: int = AUTO_TRADING_LONG_WINDOW,
        threshold: float = AUTO_TRADING_MEAN_REVERSION_THRESHOLD,
        lookback_bars: int = AUTO_TRADING_LOOKBACK_BARS,
        bar_size: str = AUTO_TRADING_BAR_SIZE,
    ):
        self.moving_average_window = moving_average_window
        self.threshold = threshold
        self.lookback_bars = lookback_bars
        self.bar_size = bar_size

    def evaluate(self, symbol: str) -> dict:
        closes = get_recent_closes(symbol, self.bar_size, self.lookback_bars)

        if len(closes) < self.moving_average_window:
            return {
                "symbol": symbol,
                "signal": "HOLD",
                "reason": "not_enough_history",
                "bars": len(closes),
            }

        latest = closes[-1]
        mean_price = sum(closes[-self.moving_average_window :]) / self.moving_average_window
        deviation = 0 if mean_price == 0 else (latest - mean_price) / mean_price

        signal = "HOLD"
        reason = "within_band"
        if deviation <= -self.threshold:
            signal = "BUY"
            reason = "below_mean"
        elif deviation >= self.threshold:
            signal = "SELL"
            reason = "above_mean"

        return {
            "symbol": symbol,
            "signal": signal,
            "reason": reason,
            "bars": len(closes),
            "bar_size": self.bar_size,
            "latest_close": round(latest, 4),
            "mean_price": round(mean_price, 4),
            "deviation_pct": round(deviation, 6),
        }
