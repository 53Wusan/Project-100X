from datetime import date
from typing import Dict

from sqlalchemy.orm import Session

from app.models import ExecutionLog


def run_replay_logs(db: Session, start_date: date, end_date: date) -> Dict:
    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.executed_at >= start_date)
        .filter(ExecutionLog.executed_at <= end_date)
        .order_by(ExecutionLog.executed_at.asc())
        .all()
    )
    pnl = 0.0
    wins = 0
    for l in logs:
        signed = l.qty * l.price if l.side.lower() == "sell" else -l.qty * l.price
        pnl += signed
        if signed > 0:
            wins += 1
    n = len(logs) or 1
    return {
        "mode": "replay_logs",
        "total_return": pnl,
        "annualized_return": 0,
        "max_drawdown": 0,
        "win_rate": wins / n,
        "turnover": abs(pnl),
        "equity_curve": [{"t": str(l.executed_at.date()), "v": pnl} for l in logs],
        "positions": sorted({l.ticker for l in logs}),
    }
