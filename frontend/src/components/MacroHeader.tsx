export default function MacroHeader({ macro, portfolio, weeklySummary, onRecompute, onGenerate }: any) {
  return (
    <div className="card">
      <h2>宏观状态: {macro?.regime} / score={macro?.macro_score}</h2>
      <div className="muted">trend_ok={macro?.trend_ok} vol_ok={macro?.vol_ok} breadth_ok={macro?.breadth_ok}</div>
      <div>{macro?.reason_text}</div>
      <div className="row"><b>持仓摘要</b><span>现金 {Math.round((portfolio?.cash_pct || 0) * 100)}%</span><span>总资产 {portfolio?.total_asset}</span><span>P/L {portfolio?.pnl}</span></div>
      <div className="row"><b>本周建议:</b><span>{weeklySummary}</span></div>
      <div className="row"><button className="btn" onClick={onRecompute}>重算宏观</button><button className="btn" onClick={onGenerate}>生成本周建议单</button></div>
    </div>
  )
}
