import { useState } from 'react'
import { client } from '../api/client'
import BacktestPanel from '../components/BacktestPanel'

export default function ExecutionBacktest() {
  const [plan, setPlan] = useState<any>(null)
  const [execution, setExecution] = useState({ ticker: 'TQQQ', side: 'buy', qty: 10, price: 100, notes: '' })
  const [reason, setReason] = useState('')
  const [backtestResult, setBacktestResult] = useState<any>(null)

  return <div className='container'>
    <div className='card'><h3>建议单草稿/最终建议单</h3><div className='row'><input placeholder='突破20%理由' value={reason} onChange={e => setReason(e.target.value)} /><button className='btn' onClick={async () => setPlan(await client.generatePlan({ asof: new Date().toISOString().slice(0, 10), max_delta_weight: 0.2, override: { reason } }))}>生成建议单</button></div>{plan && <pre>{JSON.stringify(plan, null, 2)}</pre>}</div>
    <div className='card'><h3>执行确认</h3><div className='row'><input value={execution.ticker} onChange={e => setExecution({ ...execution, ticker: e.target.value })} /><select value={execution.side} onChange={e => setExecution({ ...execution, side: e.target.value })}><option>buy</option><option>sell</option></select><input type='number' value={execution.qty} onChange={e => setExecution({ ...execution, qty: +e.target.value })} /><input type='number' value={execution.price} onChange={e => setExecution({ ...execution, price: +e.target.value })} /><button className='btn' onClick={() => client.recordExecution(execution)}>记录成交</button></div></div>
    <BacktestPanel onRun={async (p: any) => setBacktestResult(await client.runBacktest(p))} result={backtestResult} />
  </div>
}
