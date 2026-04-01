from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(64), nullable=False)
    signal: Mapped[str] = mapped_column(String(16), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    position_before: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    position_after: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    market_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    order_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
