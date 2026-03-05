import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { client } from '../api/client'
import AddSectorForm from '../components/AddSectorForm'
import HoldingsTable from '../components/HoldingsTable'
import MacroHeader from '../components/MacroHeader'
import SectorCard from '../components/SectorCard'

export default function Dashboard() {
  const [macro, setMacro] = useState<any>({})
  const [portfolio, setPortfolio] = useState<any>({ holdings: [] })
  const [modules, setModules] = useState<any[]>([])
  const [moduleState, setModuleState] = useState<any>({})
  const [newsByModule, setNewsByModule] = useState<any>({})
  const [weeklySummary, setWeeklySummary] = useState('尚未生成建议单')
  const nav = useNavigate()

  const load = async () => {
    setMacro(await client.getMacro())
    setPortfolio(await client.getPortfolio())
    const ms = await client.getModules()
    setModules(ms)
    for (const m of ms) {
      const state = await client.getModuleState(m.id)
      setModuleState((s: any) => ({ ...s, [m.id]: state }))
      const news = await client.fetchNews(m.id)
      setNewsByModule((n: any) => ({ ...n, [m.id]: news.items || [] }))
    }
  }

  useEffect(() => { load() }, [])

  return <div className='container'>
    <MacroHeader macro={macro} portfolio={portfolio} weeklySummary={weeklySummary} onRecompute={async () => setMacro(await client.recomputeMacro())} onGenerate={async () => {
      const r = await client.generatePlan({ asof: new Date().toISOString().slice(0, 10), max_delta_weight: 0.2, override: {} })
      setWeeklySummary((r.final || []).map((x: any) => `${x.action}${x.ticker} ${Math.round(x.delta_weight * 100)}%`).join(', '))
      nav('/execution')
    }} />
    <div className='card'><h3>当前持仓(最多6)</h3><HoldingsTable holdings={(portfolio.holdings || []).slice(0, 6)} /></div>
    {modules.map((m) => <SectorCard key={m.id} module={m} state={moduleState[m.id]} news={newsByModule[m.id]} onAdopt={() => nav('/execution')} />)}
    <AddSectorForm onAdd={async (f: any) => { await client.addModule(f); await load() }} />
  </div>
}
