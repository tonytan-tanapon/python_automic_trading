from app.config import (
    AUTO_TRADING_BAR_SIZE,
    AUTO_TRADING_LOOKBACK_BARS,
    AUTO_TRADING_MOMENTUM_WINDOW,
)
from app.services.market_data_service import get_recent_closes
from app.strategies.base import StrategyProtocol


class MomentumStrategy(StrategyProtocol):
    name = "momentum"

    def __init__(
        self,
        momentum_window: int = AUTO_TRADING_MOMENTUM_WINDOW,
        lookback_bars: int = AUTO_TRADING_LOOKBACK_BARS,
        bar_size: str = AUTO_TRADING_BAR_SIZE,
    ):
        self.momentum_window = momentum_window
        self.lookback_bars = lookback_bars
        self.bar_size = bar_size

    def evaluate(self, symbol: str) -> dict:
        closes = get_recent_closes(symbol, self.bar_size, self.lookback_bars)

        if len(closes) <= self.momentum_window:
            return {
                "symbol": symbol,
                "signal": "HOLD",
                "reason": "not_enough_history",
                "bars": len(closes),
            }

        baseline = closes[-self.momentum_window - 1]
        latest = closes[-1]
        change_pct = 0 if baseline == 0 else (latest - baseline) / baseline

        signal = "HOLD"
        reason = "momentum_flat"
        if change_pct > 0:
            signal = "BUY"
            reason = "positive_momentum"
        elif change_pct < 0:
            signal = "SELL"
            reason = "negative_momentum"

        return {
            "symbol": symbol,
            "signal": signal,
            "reason": reason,
            "bars": len(closes),
            "bar_size": self.bar_size,
            "latest_close": round(latest, 4),
            "baseline_close": round(baseline, 4),
            "change_pct": round(change_pct, 6),
        }
