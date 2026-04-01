import os
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_symbols(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [symbol.strip().upper() for symbol in raw_value.split(",") if symbol.strip()]

TWS_HOST = os.getenv("TWS_HOST", "127.0.0.1")
TWS_PORT = int(os.getenv("TWS_PORT", 7497))
CLIENT_ID = int(os.getenv("CLIENT_ID", 1))
TRADING_MODE = os.getenv("TRADING_MODE", "paper")

AUTO_TRADING_SYMBOLS = _get_symbols("AUTO_TRADING_SYMBOLS", "AAPL")
AUTO_TRADING_STRATEGY = os.getenv("AUTO_TRADING_STRATEGY", "sma_crossover")
AUTO_TRADING_INTERVAL_SECONDS = int(os.getenv("AUTO_TRADING_INTERVAL_SECONDS", 60))
AUTO_TRADING_BAR_SIZE = os.getenv("AUTO_TRADING_BAR_SIZE", "5 mins")
AUTO_TRADING_LOOKBACK_BARS = int(os.getenv("AUTO_TRADING_LOOKBACK_BARS", 20))
AUTO_TRADING_SHORT_WINDOW = int(os.getenv("AUTO_TRADING_SHORT_WINDOW", 5))
AUTO_TRADING_LONG_WINDOW = int(os.getenv("AUTO_TRADING_LONG_WINDOW", 10))
AUTO_TRADING_MOMENTUM_WINDOW = int(os.getenv("AUTO_TRADING_MOMENTUM_WINDOW", 6))
AUTO_TRADING_MEAN_REVERSION_THRESHOLD = float(
    os.getenv("AUTO_TRADING_MEAN_REVERSION_THRESHOLD", 0.02)
)
AUTO_TRADING_ORDER_SIZE = int(os.getenv("AUTO_TRADING_ORDER_SIZE", 1))
AUTO_TRADING_MAX_POSITION_PER_SYMBOL = int(
    os.getenv("AUTO_TRADING_MAX_POSITION_PER_SYMBOL", 10)
)
AUTO_TRADING_MAX_DAILY_TRADES = int(os.getenv("AUTO_TRADING_MAX_DAILY_TRADES", 10))
AUTO_TRADING_COOLDOWN_SECONDS = int(os.getenv("AUTO_TRADING_COOLDOWN_SECONDS", 300))
AUTO_TRADING_STOP_LOSS_PCT = float(os.getenv("AUTO_TRADING_STOP_LOSS_PCT", 0.03))
AUTO_TRADING_TAKE_PROFIT_PCT = float(os.getenv("AUTO_TRADING_TAKE_PROFIT_PCT", 0.05))
AUTO_TRADING_AUTOSTART = _get_bool("AUTO_TRADING_AUTOSTART", False)
AUTO_TRADING_ALLOW_LIVE = _get_bool("AUTO_TRADING_ALLOW_LIVE", False)
