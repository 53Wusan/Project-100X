import csv
import io
import json
from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.backtest.engine_backtestingpy import BacktestParams, run_pure_rules
from app.backtest.replay import run_replay_logs
from app.data_adapters.gdelt_provider import GDELTProvider
from app.data_adapters.yfinance_provider import YFinanceProvider
from app.models import (
    BacktestRun,
    ConfigVersion,
    ExecutionLog,
    Holding,
    ModuleStateSnapshot,
    NewsItem,
    PortfolioSnapshot,
    SectorModule,
    TradePlan,
)
from app.schemas import (
    BacktestRunIn,
    ExecutionRecordIn,
    PortfolioSnapshotIn,
    SectorModuleIn,
    SectorModulePatch,
    TradePlanGenerateIn,
)
from app.storage.db import get_db, init_db
from app.strategy.indicators import classify_stage, momentum_13_26w, sma
from app.strategy.layer1_macro import compute_macro_state
from app.strategy.layer2_selection import select_candidates
from app.strategy.layer3_execution import generate_trade_plan

app = FastAPI(title="Project100X MVP")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
KEYS_PATH = Path(".local_keys.json")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/state/macro")
def get_macro_state(asof: date | None = Query(default=None)):
    m = compute_macro_state()
    return {**m.__dict__, "updated_at": datetime.utcnow(), "asof": asof or date.today()}


@app.post("/api/state/macro/recompute")
def recompute_macro_state():
    return get_macro_state()


@app.get("/api/portfolio/current")
def get_portfolio_current(db: Session = Depends(get_db)):
    snap = db.query(PortfolioSnapshot).order_by(PortfolioSnapshot.created_at.desc()).first()
    if not snap:
        return {"cash_pct": 1, "holdings": [], "total_asset": 0, "pnl": 0}
    return {
        "id": snap.id,
        "cash_pct": snap.cash_pct,
        "total_asset": snap.total_asset,
        "pnl": snap.pnl,
        "holdings": [{"ticker": h.ticker, "qty": h.qty, "value": h.value, "avg_cost": h.avg_cost, "notes": h.notes} for h in snap.holdings],
    }


@app.post("/api/portfolio/snapshot")
def create_snapshot(payload: PortfolioSnapshotIn, db: Session = Depends(get_db)):
    snap = PortfolioSnapshot(
        asof_date=payload.asof_date,
        total_asset=payload.total_asset,
        cash_pct=payload.cash_pct,
        pnl=payload.pnl,
        notes=payload.notes,
    )
    db.add(snap)
    db.flush()
    for h in payload.holdings:
        db.add(Holding(snapshot_id=snap.id, **h.model_dump()))
    db.commit()
    return {"ok": True, "snapshot_id": snap.id}


@app.get("/api/modules")
def list_modules(db: Session = Depends(get_db)):
    return db.query(SectorModule).order_by(SectorModule.id.asc()).all()


@app.post("/api/modules")
def create_module(payload: SectorModuleIn, db: Session = Depends(get_db)):
    m = SectorModule(**payload.model_dump())
    db.add(m)
    db.commit()
    return m


@app.patch("/api/modules/{module_id}")
def patch_module(module_id: int, payload: SectorModulePatch, db: Session = Depends(get_db)):
    m = db.get(SectorModule, module_id)
    if not m:
        raise HTTPException(404, "module not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(m, k, v)
    db.commit()
    return m


@app.get("/api/modules/{module_id}/state")
def module_state(module_id: int, asof: date | None = Query(default=None), db: Session = Depends(get_db)):
    m = db.get(SectorModule, module_id)
    if not m:
        raise HTTPException(404, "module not found")
    p = YFinanceProvider()
    w = p.history(m.leveraged_symbol, period="1y", interval="1wk")
    if w.empty:
        return {"module": m.name, "stage": "unknown"}
    ma20 = sma(w["Close"], 20)
    stg = classify_stage(w["Close"])
    mom = momentum_13_26w(w["Close"])
    state = ModuleStateSnapshot(module_id=m.id, asof_date=asof or date.today(), stage=stg, momentum=mom, trend_ok=w["Close"].iloc[-1] > ma20.iloc[-1], reason_text="auto computed")
    db.add(state)
    db.commit()
    return {"module": m.name, "stage": stg, "momentum": mom, "trend_ok": state.trend_ok, "asof": asof or date.today()}


@app.post("/api/news/fetch")
def fetch_news(module_id: int, db: Session = Depends(get_db)):
    m = db.get(SectorModule, module_id)
    if not m:
        raise HTTPException(404, "module not found")
    provider = GDELTProvider()
    items = provider.fetch(m.name)
    out = []
    for it in items:
        n = NewsItem(module_id=m.id, title=it["title"], source=it["source"], url=it["url"], sentiment=it["sentiment"], risk_label=it["risk_label"])
        db.add(n)
        out.append(it)
    db.commit()
    return {"count": len(out), "items": out}


@app.post("/api/tradeplan/generate")
def generate(payload: TradePlanGenerateIn, db: Session = Depends(get_db)):
    macro = compute_macro_state()
    modules = db.query(SectorModule).filter_by(enabled=True).all()
    picks = select_candidates(modules, top_k=5)
    snap = db.query(PortfolioSnapshot).order_by(PortfolioSnapshot.created_at.desc()).first()
    current_weights = {}
    if snap and snap.total_asset:
        for h in snap.holdings:
            current_weights[h.ticker] = h.value / snap.total_asset
    result = generate_trade_plan(current_weights, picks, macro.macro_score, payload.max_delta_weight)
    tp = TradePlan(asof_date=payload.asof, draft_json=json.dumps(result["draft"], ensure_ascii=False), final_json=json.dumps(result["final"], ensure_ascii=False), override_reason=payload.override.get("reason", ""))
    db.add(tp)
    db.commit()
    return {"trade_plan_id": tp.id, **result}


@app.post("/api/execution/record")
def record_execution(payload: ExecutionRecordIn, db: Session = Depends(get_db)):
    row = ExecutionLog(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"ok": True, "execution_id": row.id}


@app.post("/api/backtest/run")
def run_backtest(payload: BacktestRunIn, db: Session = Depends(get_db)):
    if payload.mode == "pure_rules":
        result = run_pure_rules(db, BacktestParams(payload.start_date, payload.end_date, payload.commission_bps, payload.slippage_bps))
    else:
        result = run_replay_logs(db, payload.start_date, payload.end_date)
    run = BacktestRun(mode=payload.mode, params_json=json.dumps(payload.model_dump(), default=str), result_json=json.dumps(result, default=str))
    db.add(run)
    db.commit()
    return {"run_id": run.id, "result": result}


@app.get("/api/backtest/{run_id}")
def get_backtest(run_id: int, db: Session = Depends(get_db)):
    run = db.get(BacktestRun, run_id)
    if not run:
        raise HTTPException(404, "run not found")
    return {"id": run.id, "mode": run.mode, "params": json.loads(run.params_json), "result": json.loads(run.result_json)}


@app.post("/api/admin/keys")
def save_keys(payload: dict):
    KEYS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return {"ok": True}


@app.post("/api/admin/config/version")
def save_config_version(payload: dict, db: Session = Depends(get_db)):
    db.query(ConfigVersion).update({"active": False})
    cv = ConfigVersion(version_name=payload.get("version_name", f"v{datetime.utcnow().strftime('%Y%m%d%H%M')}"), config_json=json.dumps(payload.get("config", {}), ensure_ascii=False), active=True)
    db.add(cv)
    db.commit()
    return {"id": cv.id, "version_name": cv.version_name}


@app.get("/api/admin/config/version/current")
def current_config_version(db: Session = Depends(get_db)):
    cv = db.query(ConfigVersion).filter_by(active=True).order_by(ConfigVersion.created_at.desc()).first()
    if not cv:
        return {"version_name": "none", "config": {}}
    return {"id": cv.id, "version_name": cv.version_name, "config": json.loads(cv.config_json)}


@app.get("/api/portfolio/export")
def export_portfolio_csv(db: Session = Depends(get_db)):
    snap = db.query(PortfolioSnapshot).order_by(PortfolioSnapshot.created_at.desc()).first()
    if not snap:
        raise HTTPException(404, "no snapshot")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ticker", "qty", "value", "avg_cost", "notes"])
    for h in snap.holdings:
        writer.writerow([h.ticker, h.qty, h.value, h.avg_cost, h.notes])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv")


@app.post("/api/portfolio/import")
async def import_portfolio_csv(file: UploadFile, db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(content)))
    holdings = [
        Holding(
            ticker=r["ticker"],
            qty=float(r.get("qty", 0) or 0),
            value=float(r.get("value", 0) or 0),
            avg_cost=float(r.get("avg_cost", 0) or 0),
            notes=r.get("notes", ""),
            snapshot_id=0,
        )
        for r in rows
    ]
    snap = PortfolioSnapshot(asof_date=datetime.utcnow(), total_asset=sum(h.value for h in holdings), cash_pct=0)
    db.add(snap)
    db.flush()
    for h in holdings:
        h.snapshot_id = snap.id
        db.add(h)
    db.commit()
    return {"ok": True, "snapshot_id": snap.id}
