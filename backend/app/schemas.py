from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class HoldingIn(BaseModel):
    ticker: str
    qty: float = 0
    value: float = 0
    avg_cost: float = 0
    notes: str = ""


class PortfolioSnapshotIn(BaseModel):
    asof_date: datetime
    total_asset: float
    cash_pct: float
    pnl: float = 0
    notes: str = ""
    holdings: List[HoldingIn]


class SectorModuleIn(BaseModel):
    name: str
    index_symbol: str
    leveraged_symbol: str
    leader_symbol: str = ""
    enabled: bool = True


class SectorModulePatch(BaseModel):
    name: Optional[str] = None
    index_symbol: Optional[str] = None
    leveraged_symbol: Optional[str] = None
    leader_symbol: Optional[str] = None
    enabled: Optional[bool] = None


class TradePlanGenerateIn(BaseModel):
    asof: date
    max_delta_weight: float = 0.2
    override: dict = Field(default_factory=dict)


class ExecutionRecordIn(BaseModel):
    trade_plan_id: Optional[int] = None
    ticker: str
    side: str
    qty: float
    price: float
    notes: str = ""


class BacktestRunIn(BaseModel):
    mode: str
    start_date: date
    end_date: date
    commission_bps: float = 5
    slippage_bps: float = 10
    rebalance_freq: str = "W"
    allow_simulated_proxy: bool = False
