# 周频杠杆ETF/龙头股交易看板与策略回测系统（MVP）

本仓库提供一个可本地一键运行的全栈MVP：
- **前端**：React + TypeScript + Vite + ECharts
- **后端**：FastAPI + SQLAlchemy + SQLite
- **数据**：yfinance（默认）、FRED（宏观可选）、GDELT（新闻）
- **回测**：pure-rules + replay-logs

## 目录结构
- `backend/` FastAPI服务、策略、回测、数据适配器、seed脚本
- `frontend/` Dashboard/Admin/ExecutionBacktest页面
- `.github/workflows/weekly.yml` 周频自动化模板
- `docker-compose.yml` 一键启动前后端

## 0到运行成功（本地最简）

### 1) 后端启动
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_demo_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) 前端启动
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
浏览器打开 `http://localhost:5173`

## 一键启动（Docker Compose）
```bash
docker compose up --build
```
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000/docs`

## 核心实现说明

### Dashboard（顶部+板块卡片+新增模块）
- 顶部宏观状态：`macro_score/regime/trend_ok/vol_ok/breadth_ok/reason_text`
- 持仓摘要：现金、持仓列表、总资产、P/L
- 本周建议摘要与按钮：重算宏观、生成建议单
- 板块卡片：指数/杠杆ETF/龙头股、阶段、新闻、建议动作
- 底部：AddSectorForm 添加新板块

### Admin
- Holdings 手工录入并保存 `PortfolioSnapshot`
- Modules 管理（编辑/禁用）
- Keys 本地存储（仅后端读取）
- Params 参数版本化，保存生成 `ConfigVersion`

### ExecutionBacktest
- 建议单草稿+最终单（TradePlan）
- 20%调整约束（可填突破理由）
- 手工执行确认写入 `ExecutionLog`
- 回测（pure_rules/replay_logs）参数输入与结果展示

## 策略规则（与需求对齐）

### Layer1: 宏观打分
`macro_score = trend_ok + vol_ok + breadth_ok`
- trend_ok：SPY周线收盘 > SMA40W
- vol_ok：VIX < VIX3M；缺失时降级为 VIX<25
- breadth_ok：默认A方案（NYAD 10周回归斜率>0）
- regime：3=Risk-On，2=Caution，0/1=Risk-Off
- 仓位：3=>100%，2=>50%，<=1=>0%

### Layer2: 选择
- 动量：`0.5*ROC(13W)+0.5*ROC(26W)`
- 趋势过滤：价格>MA20W 且 MA20W斜率>0
- 模块内按动量排序，前K（默认<=5）
- 龙头股最多2只（同过滤逻辑）

### Layer3: 执行
- 默认等权
- 单周单标的权重变化限制 `|delta|<=20%`
- 例外：宏观=3且动量第一、强势可放宽到最大仓位（默认40%）
- 退出：跌破MA10W（参数化）或宏观<=1清仓
- 新闻只做提示，触发红旗进入人工复核，不自动下单

## API 列表与示例
- `GET /api/state/macro?asof=YYYY-MM-DD`
- `POST /api/state/macro/recompute`
- `GET /api/portfolio/current`
- `POST /api/portfolio/snapshot`
```json
{
  "asof_date":"2026-01-01T00:00:00",
  "total_asset":100000,
  "cash_pct":0.2,
  "pnl":5000,
  "notes":"manual",
  "holdings":[{"ticker":"TQQQ","qty":100,"value":20000,"avg_cost":170,"notes":""}]
}
```
- `GET /api/modules`
- `POST /api/modules`
- `PATCH /api/modules/{id}`
- `GET /api/modules/{id}/state?asof=`
- `POST /api/news/fetch?module_id=1`
- `POST /api/tradeplan/generate`
- `POST /api/execution/record`
- `POST /api/backtest/run`
```json
{"mode":"pure_rules","start_date":"2022-01-01","end_date":"2024-12-31","commission_bps":5,"slippage_bps":10,"rebalance_freq":"W"}
```
- `GET /api/backtest/{run_id}`

## CSV 支持
- 导出：`GET /api/portfolio/export`
- 导入：`POST /api/portfolio/import`（multipart file）

## 可替换项
- 行情：`backend/app/data_adapters/yfinance_provider.py` 可替换为 OpenBB ODP 适配器
- 新闻：GDELT 可替换 NewsAPI/RSS
- 回测：当前为轻量引擎，可替换 backtrader

## 人工审核点（务必阅读）
1. **风控阈值**：MA窗口、动量窗口、最大仓位、20%规则例外。
2. **杠杆产品范围**：是否允许反向杠杆ETF/单股杠杆ETF（默认不自动放行）。
3. **实盘下单权限**：MVP **禁止自动下单**，如接券商API必须显式开关且默认关闭。
4. **数据源可靠性**：yfinance/抓取类接口可能变更，需监控与fallback。

## 自动化任务（可选）
- `.github/workflows/weekly.yml` 每周触发示例（重算宏观、产出数据库artifact）

