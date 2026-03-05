import { useEffect, useState } from 'react'
import { client } from '../api/client'

export default function Admin() {
  const [modules, setModules] = useState<any[]>([])
  const [holdingsJson, setHoldingsJson] = useState('[{"ticker":"TQQQ","qty":100,"value":20000,"avg_cost":170,"notes":"demo"}]')
  const [keys, setKeys] = useState('{"FRED_KEY":""}')
  const [params, setParams] = useState('{"max_delta_weight":0.2,"exit_ma":10}')
  const [currentVersion, setCurrentVersion] = useState<any>({})

  const load = async () => {
    setModules(await client.getModules())
    setCurrentVersion(await client.currentConfigVersion())
  }
  useEffect(() => { load() }, [])

  return <div className='container'>
    <div className='card'><h3>Holdings 输入</h3><textarea rows={6} style={{ width: '100%' }} value={holdingsJson} onChange={e => setHoldingsJson(e.target.value)} />
      <button className='btn' onClick={async () => {
        const holdings = JSON.parse(holdingsJson)
        await client.saveSnapshot({ asof_date: new Date().toISOString(), total_asset: holdings.reduce((a: number, h: any) => a + (h.value || 0), 0), cash_pct: 0.2, pnl: 0, notes: 'manual', holdings })
      }}>保存快照</button>
    </div>
    <div className='card'><h3>Modules 管理</h3>{modules.map(m => <div className='row' key={m.id}><span>{m.name} {m.index_symbol}/{m.leveraged_symbol}</span><button className='btn' onClick={async () => { await client.patchModule(m.id, { enabled: !m.enabled }); await load() }}>{m.enabled ? '禁用' : '启用'}</button></div>)}</div>
    <div className='card'><h3>Keys</h3><textarea rows={4} style={{ width: '100%' }} value={keys} onChange={e => setKeys(e.target.value)} /><button className='btn' onClick={() => client.saveKeys(JSON.parse(keys))}>保存本地Key</button></div>
    <div className='card'><h3>策略参数版本</h3><div className='muted'>当前版本: {currentVersion.version_name}</div><textarea rows={4} style={{ width: '100%' }} value={params} onChange={e => setParams(e.target.value)} /><button className='btn' onClick={async () => { await client.saveConfigVersion({ version_name: `v-${Date.now()}`, config: JSON.parse(params) }); await load() }}>保存新版本</button></div>
  </div>
}
