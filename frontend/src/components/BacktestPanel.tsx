import { useState } from 'react'

export default function BacktestPanel({ onRun, result }: any) {
  const [params, setParams] = useState({ mode: 'pure_rules', start_date: '2022-01-01', end_date: '2024-12-31', commission_bps: 5, slippage_bps: 10, rebalance_freq: 'W', allow_simulated_proxy: false })
  return <div className='card'><h3>回测面板</h3><div className='row'>
    <select value={params.mode} onChange={e => setParams({ ...params, mode: e.target.value })}><option value='pure_rules'>pure_rules</option><option value='replay_logs'>replay_logs</option></select>
    <input type='date' value={params.start_date} onChange={e => setParams({ ...params, start_date: e.target.value })} />
    <input type='date' value={params.end_date} onChange={e => setParams({ ...params, end_date: e.target.value })} />
    <input type='number' value={params.commission_bps} onChange={e => setParams({ ...params, commission_bps: +e.target.value })} />
    <input type='number' value={params.slippage_bps} onChange={e => setParams({ ...params, slippage_bps: +e.target.value })} />
    <button className='btn' onClick={() => onRun(params)}>运行</button></div>
    {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
  </div>
}
