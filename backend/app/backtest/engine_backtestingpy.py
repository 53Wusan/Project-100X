from dataclasses import dataclass
from datetime import date
from typing import Dict, List

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.data_adapters.yfinance_provider import YFinanceProvider
from app.strategy.layer1_macro import compute_macro_state
from app.strategy.layer2_selection import select_candidates
from app.strategy.layer3_execution import target_exposure
from app.models import SectorModule


@dataclass
class BacktestParams:
    start_date: date
    end_date: date
    commission_bps: float = 5
    slippage_bps: float = 10


def run_pure_rules(db: Session, params: BacktestParams) -> Dict:
    modules = db.query(SectorModule).filter_by(enabled=True).all()
    if not modules:
        return {"error": "No modules configured"}

    picks = select_candidates(modules, top_k=5)
    provider = YFinanceProvider()
    rets = []
    tickers = [p["ticker"] for p in picks]
    for t in tickers:
        w = provider.history(t, period="3y", interval="1wk")
        w = w[(w.index.date >= params.start_date) & (w.index.date <= params.end_date)]
        if len(w) > 1:
            rets.append(w["Close"].pct_change().fillna(0))
    if not rets:
        return {"error": "No price history"}

    aligned = pd.concat(rets, axis=1).fillna(0)
    macro = compute_macro_state()
    exp = target_exposure(macro.macro_score)
    port_ret = aligned.mean(axis=1) * exp
    cost = (params.commission_bps + params.slippage_bps) / 10000 / 52
    net = port_ret - cost
    equity = (1 + net).cumprod()
    dd = equity / equity.cummax() - 1
    years = max((params.end_date - params.start_date).days / 365, 1 / 52)
    cagr = float(equity.iloc[-1] ** (1 / years) - 1)
    win_rate = float((net > 0).mean())
    return {
        "mode": "pure_rules",
        "total_return": float(equity.iloc[-1] - 1),
        "annualized_return": cagr,
        "max_drawdown": float(dd.min()),
        "win_rate": win_rate,
        "turnover": float(np.abs(net).sum()),
        "equity_curve": [{"t": str(i.date()), "v": float(v)} for i, v in equity.items()],
        "positions": tickers,
    }
