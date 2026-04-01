import asyncio
from datetime import datetime, timezone

from app.config import (
    AUTO_TRADING_AUTOSTART,
    AUTO_TRADING_INTERVAL_SECONDS,
    AUTO_TRADING_ORDER_SIZE,
    AUTO_TRADING_STRATEGY,
    AUTO_TRADING_SYMBOLS,
)
from app.services.market_data_service import get_last_price
from app.services.order_service import place_market_order
from app.services.position_service import get_symbol_position_details
from app.services.risk_service import RiskManager
from app.services.trade_log_service import get_recent_trades, log_trade
from app.strategies import build_strategy, list_strategies


class AutoTradingEngine:
    def __init__(self):
        self.symbols = AUTO_TRADING_SYMBOLS
        self.interval_seconds = AUTO_TRADING_INTERVAL_SECONDS
        self.order_size = AUTO_TRADING_ORDER_SIZE
        self.strategy_name = AUTO_TRADING_STRATEGY
        self.strategy = build_strategy(self.strategy_name)
        self.risk_manager = RiskManager()
        self._task: asyncio.Task | None = None
        self._stop_event: asyncio.Event | None = None
        self._running = False
        self._started_at: datetime | None = None
        self._last_run_at: datetime | None = None
        self._trades_today = 0
        self._trade_day = self._utc_now().date()
        self._last_trade_at: dict[str, datetime] = {}
        self._latest_results: dict[str, dict] = {}

    async def start(self):
        if self._running:
            return self.status()

        self._stop_event = asyncio.Event()
        self._running = True
        self._started_at = self._utc_now()
        self._task = asyncio.create_task(self._run_loop())
        return self.status()

    async def stop(self):
        if not self._running:
            return self.status()

        self._running = False

        if self._stop_event is not None:
            self._stop_event.set()

        if self._task is not None:
            await self._task

        self._task = None
        self._stop_event = None
        return self.status()

    async def startup(self):
        if AUTO_TRADING_AUTOSTART:
            await self.start()

    async def shutdown(self):
        await self.stop()

    async def run_once(self):
        self._reset_trade_counter_if_needed()
        self._last_run_at = self._utc_now()
        cycle_results = {}

        for symbol in self.symbols:
            cycle_results[symbol] = self._evaluate_symbol(symbol)

        self._latest_results = cycle_results
        return self.status()

    def status(self):
        return {
            "running": self._running,
            "symbols": self.symbols,
            "strategy": self.strategy_name,
            "available_strategies": list_strategies(),
            "interval_seconds": self.interval_seconds,
            "order_size": self.order_size,
            "started_at": self._isoformat(self._started_at),
            "last_run_at": self._isoformat(self._last_run_at),
            "trades_today": self._trades_today,
            "latest_results": self._latest_results,
            "recent_trades": get_recent_trades(limit=10),
        }

    async def _run_loop(self):
        while self._stop_event is not None and not self._stop_event.is_set():
            try:
                await self.run_once()
            except Exception as exc:
                timestamp = self._utc_now()
                for symbol in self.symbols:
                    self._latest_results[symbol] = {
                        "symbol": symbol,
                        "status": "error",
                        "message": str(exc),
                        "evaluated_at": self._isoformat(timestamp),
                    }

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.interval_seconds,
                )
            except asyncio.TimeoutError:
                continue

    def _evaluate_symbol(self, symbol: str):
        evaluated_at = self._utc_now()
        strategy_result = self.strategy.evaluate(symbol)
        position = get_symbol_position_details(symbol)
        current_position = position["position"]
        avg_cost = position["avgCost"]
        market_price = get_last_price(symbol)
        signal = strategy_result["signal"]
        risk_override_signal, risk_override_reason = self.risk_manager.check_exit_rules(
            current_position=current_position,
            avg_cost=avg_cost,
            market_price=market_price,
        )
        if risk_override_signal is not None:
            signal = risk_override_signal
            strategy_result = {
                **strategy_result,
                "signal": signal,
                "reason": risk_override_reason,
                "risk_override": True,
            }
        last_trade_at = self._last_trade_at.get(symbol)

        approved, reason = self.risk_manager.evaluate(
            symbol=symbol,
            signal=signal,
            current_position=current_position,
            avg_cost=avg_cost,
            market_price=market_price,
            quantity=self.order_size,
            trades_today=self._trades_today,
            last_trade_at=last_trade_at,
        )

        result = {
            "symbol": symbol,
            "evaluated_at": self._isoformat(evaluated_at),
            "signal": signal,
            "strategy": strategy_result,
            "current_position": current_position,
            "avg_cost": avg_cost,
            "market_price": market_price,
            "risk_reason": reason,
            "status": "skipped",
        }

        if not approved:
            log_trade(
                symbol=symbol,
                strategy_name=self.strategy_name,
                signal=signal,
                action="SKIP",
                quantity=0,
                status="skipped",
                risk_reason=reason,
                position_before=current_position,
                position_after=current_position,
                market_price=market_price,
                avg_cost=avg_cost,
                note=strategy_result.get("reason"),
            )
            return result

        quantity = self.order_size
        if signal == "SELL":
            quantity = min(self.order_size, max(int(current_position), 0))
            if quantity == 0:
                result["risk_reason"] = "no_long_position_to_exit"
                log_trade(
                    symbol=symbol,
                    strategy_name=self.strategy_name,
                    signal=signal,
                    action="SKIP",
                    quantity=0,
                    status="skipped",
                    risk_reason="no_long_position_to_exit",
                    position_before=current_position,
                    position_after=current_position,
                    market_price=market_price,
                    avg_cost=avg_cost,
                    note="sell signal without long position",
                )
                return result

        order_result = place_market_order(symbol, signal, quantity)
        self._last_trade_at[symbol] = evaluated_at
        self._trades_today += 1
        position_after = current_position + quantity if signal == "BUY" else max(current_position - quantity, 0)
        log_trade(
            symbol=symbol,
            strategy_name=self.strategy_name,
            signal=signal,
            action=signal,
            quantity=quantity,
            status="submitted",
            risk_reason="approved",
            position_before=current_position,
            position_after=position_after,
            market_price=market_price,
            avg_cost=avg_cost,
            order_status=order_result.get("status"),
            note=strategy_result.get("reason"),
        )

        result["status"] = "submitted"
        result["order"] = order_result
        result["risk_reason"] = "approved"
        return result

    def _reset_trade_counter_if_needed(self):
        today = self._utc_now().date()
        if today != self._trade_day:
            self._trade_day = today
            self._trades_today = 0

    @staticmethod
    def _utc_now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _isoformat(value: datetime | None):
        return value.isoformat() if value is not None else None


auto_trading_engine = AutoTradingEngine()
