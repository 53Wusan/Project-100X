from datetime import datetime

from app.models import Holding, PortfolioSnapshot, SectorModule
from app.storage.db import SessionLocal, init_db


def run():
    init_db()
    db = SessionLocal()
    if not db.query(SectorModule).count():
        db.add_all(
            [
                SectorModule(name="科技大盘", index_symbol="QQQ", leveraged_symbol="TQQQ", leader_symbol="NVDA"),
                SectorModule(name="半导体", index_symbol="SOXX", leveraged_symbol="SOXL", leader_symbol="AVGO"),
                SectorModule(name="加密货币", index_symbol="IBIT", leveraged_symbol="BITX", leader_symbol="COIN"),
            ]
        )
    if not db.query(PortfolioSnapshot).count():
        snap = PortfolioSnapshot(asof_date=datetime.utcnow(), total_asset=100000, cash_pct=0.5, pnl=12000)
        db.add(snap)
        db.flush()
        db.add_all(
            [
                Holding(snapshot_id=snap.id, ticker="TQQQ", qty=100, value=20000, avg_cost=170),
                Holding(snapshot_id=snap.id, ticker="SOXL", qty=120, value=30000, avg_cost=200),
            ]
        )
    db.commit()
    print("seed done")


if __name__ == "__main__":
    run()
