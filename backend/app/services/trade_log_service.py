from datetime import datetime, timezone

from sqlalchemy import desc

from app.database import SessionLocal
from app.models.trade_log import TradeLog


def log_trade(
    *,
    symbol: str,
    strategy_name: str,
    signal: str,
    action: str,
    quantity: int,
    status: str,
    risk_reason: str,
    position_before: float,
    position_after: float,
    market_price: float | None,
    avg_cost: float | None,
    order_status: str | None = None,
    note: str | None = None,
):
    db = SessionLocal()
    try:
        entry = TradeLog(
            created_at=datetime.now(timezone.utc),
            symbol=symbol,
            strategy_name=strategy_name,
            signal=signal,
            action=action,
            quantity=quantity,
            status=status,
            risk_reason=risk_reason,
            position_before=position_before,
            position_after=position_after,
            market_price=market_price,
            avg_cost=avg_cost,
            order_status=order_status,
            note=note,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    finally:
        db.close()


def get_recent_trades(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.query(TradeLog).order_by(desc(TradeLog.created_at)).limit(limit).all()
        return [serialize_trade(row) for row in rows]
    finally:
        db.close()


def serialize_trade(row: TradeLog):
    return {
        "id": row.id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "symbol": row.symbol,
        "strategy_name": row.strategy_name,
        "signal": row.signal,
        "action": row.action,
        "quantity": row.quantity,
        "status": row.status,
        "risk_reason": row.risk_reason,
        "position_before": row.position_before,
        "position_after": row.position_after,
        "market_price": row.market_price,
        "avg_cost": row.avg_cost,
        "order_status": row.order_status,
        "note": row.note,
    }
