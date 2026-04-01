from datetime import datetime, timezone

from app.config import (
    AUTO_TRADING_ALLOW_LIVE,
    AUTO_TRADING_COOLDOWN_SECONDS,
    AUTO_TRADING_MAX_DAILY_TRADES,
    AUTO_TRADING_MAX_POSITION_PER_SYMBOL,
    AUTO_TRADING_STOP_LOSS_PCT,
    AUTO_TRADING_TAKE_PROFIT_PCT,
    TRADING_MODE,
)


class RiskManager:
    def __init__(
        self,
        max_position_per_symbol: int = AUTO_TRADING_MAX_POSITION_PER_SYMBOL,
        max_daily_trades: int = AUTO_TRADING_MAX_DAILY_TRADES,
        cooldown_seconds: int = AUTO_TRADING_COOLDOWN_SECONDS,
        stop_loss_pct: float = AUTO_TRADING_STOP_LOSS_PCT,
        take_profit_pct: float = AUTO_TRADING_TAKE_PROFIT_PCT,
    ):
        self.max_position_per_symbol = max_position_per_symbol
        self.max_daily_trades = max_daily_trades
        self.cooldown_seconds = cooldown_seconds
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def evaluate(
        self,
        *,
        symbol: str,
        signal: str,
        current_position: float,
        avg_cost: float,
        market_price: float | None,
        quantity: int,
        trades_today: int,
        last_trade_at: datetime | None,
    ) -> tuple[bool, str]:
        if signal == "HOLD":
            return False, "hold_signal"

        if TRADING_MODE != "paper" and not AUTO_TRADING_ALLOW_LIVE:
            return False, "live_trading_blocked"

        if trades_today >= self.max_daily_trades:
            return False, "daily_trade_limit_reached"

        if last_trade_at is not None:
            elapsed = (datetime.now(timezone.utc) - last_trade_at).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False, "cooldown_active"

        if signal == "BUY" and current_position + quantity > self.max_position_per_symbol:
            return False, "max_position_exceeded"

        if signal == "BUY" and current_position > 0:
            return False, "position_already_open"

        if signal == "SELL" and current_position <= 0:
            return False, "no_long_position_to_exit"

        return True, "approved"

    def check_exit_rules(
        self,
        *,
        current_position: float,
        avg_cost: float,
        market_price: float | None,
    ) -> tuple[str | None, str | None]:
        if current_position <= 0 or avg_cost <= 0 or market_price is None or market_price <= 0:
            return None, None

        stop_loss_price = avg_cost * (1 - self.stop_loss_pct)
        take_profit_price = avg_cost * (1 + self.take_profit_pct)

        if market_price <= stop_loss_price:
            return "SELL", "stop_loss_triggered"

        if market_price >= take_profit_price:
            return "SELL", "take_profit_triggered"

        return None, None
