from datetime import datetime, timezone

from app.services.ib_client import get_ib_connection_status
from app.services.market_data_service import get_price


class AutoTradeService:
    def __init__(self):
        self._last_run_at: datetime | None = None
        self._last_symbol: str | None = None
        self._last_result: dict | None = None

    def run_once(self, symbol: str):
        normalized_symbol = symbol.strip().upper()
        # print(f"Running auto-trade for symbol: {normalized_symbol} at {datetime.now(timezone.utc).isoformat()}")    
        if not normalized_symbol:
            raise ValueError("Symbol is required")

        connection = get_ib_connection_status()
        if not connection["connected"]:
            raise ConnectionError("TWS is not connected")

        price_data = get_price(normalized_symbol)
        self._last_run_at = self._utc_now()
        self._last_symbol = normalized_symbol
        self._last_result = {
            "status": "ok",
            "symbol": normalized_symbol,
            "evaluated_at": self._isoformat(self._last_run_at),
            "price": price_data,
            "message": f"Fetched market data for {normalized_symbol}",
        }
        return self._last_result

    def status(self):
        return {
            "last_run_at": self._isoformat(self._last_run_at),
            "last_symbol": self._last_symbol,
            "last_result": self._last_result,
        }

    @staticmethod
    def _utc_now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _isoformat(value: datetime | None):
        return value.isoformat() if value is not None else None


auto_trade_service = AutoTradeService()
