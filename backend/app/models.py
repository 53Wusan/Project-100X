from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.storage.db import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    asof_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_asset: Mapped[float] = mapped_column(Float, default=0)
    cash_pct: Mapped[float] = mapped_column(Float, default=1.0)
    pnl: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    holdings = relationship("Holding", back_populates="snapshot", cascade="all,delete")


class Holding(Base):
    __tablename__ = "holdings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("portfolio_snapshots.id"))
    ticker: Mapped[str] = mapped_column(String(20))
    qty: Mapped[float] = mapped_column(Float, default=0)
    value: Mapped[float] = mapped_column(Float, default=0)
    avg_cost: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    snapshot = relationship("PortfolioSnapshot", back_populates="holdings")


class SectorModule(Base):
    __tablename__ = "sector_modules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    index_symbol: Mapped[str] = mapped_column(String(20))
    leveraged_symbol: Mapped[str] = mapped_column(String(20))
    leader_symbol: Mapped[str] = mapped_column(String(20), default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SignalRun(Base):
    __tablename__ = "signal_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="ok")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModuleStateSnapshot(Base):
    __tablename__ = "module_state_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("sector_modules.id"))
    asof_date: Mapped[Date] = mapped_column(Date)
    stage: Mapped[str] = mapped_column(String(30), default="unknown")
    momentum: Mapped[float] = mapped_column(Float, default=0)
    trend_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    news_risk_score: Mapped[float] = mapped_column(Float, default=0)
    reason_text: Mapped[str] = mapped_column(Text, default="")


class TradePlan(Base):
    __tablename__ = "trade_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    asof_date: Mapped[Date] = mapped_column(Date)
    draft_json: Mapped[str] = mapped_column(Text, default="[]")
    final_json: Mapped[str] = mapped_column(Text, default="[]")
    override_reason: Mapped[str] = mapped_column(Text, default="")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trade_plan_id: Mapped[int] = mapped_column(ForeignKey("trade_plans.id"), nullable=True)
    ticker: Mapped[str] = mapped_column(String(20))
    side: Mapped[str] = mapped_column(String(10))
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notes: Mapped[str] = mapped_column(Text, default="")


class NewsItem(Base):
    __tablename__ = "news_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("sector_modules.id"))
    title: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100), default="gdelt")
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sentiment: Mapped[float] = mapped_column(Float, default=0)
    risk_label: Mapped[str] = mapped_column(String(20), default="neutral")
    url: Mapped[str] = mapped_column(Text, default="")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mode: Mapped[str] = mapped_column(String(20))
    params_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ConfigVersion(Base):
    __tablename__ = "config_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_name: Mapped[str] = mapped_column(String(50), default="v1")
    config_json: Mapped[str] = mapped_column(Text, default="{}")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
