import ReactECharts from 'echarts-for-react'

export default function SectorCard({ module, state, news, onAdopt }: any) {
  const data = state?.series || []
  const option = { xAxis: { type: 'category', data: data.map((x: any) => x.date) }, yAxis: { type: 'value' }, series: [{ data: data.map((x: any) => x.close), type: 'line' }] }
  return <div className='card grid'>
    <div><h4>{module.name}</h4><div>指数 {module.index_symbol}</div><div>杠杆ETF {module.leveraged_symbol}</div><div>龙头 {module.leader_symbol || '-'}</div></div>
    <div><div>阶段: {state?.stage || '...'}</div><div>动量: {Number(state?.momentum || 0).toFixed(3)}</div><ReactECharts option={option} style={{ height: 180 }} /></div>
    <div><b>新闻监测</b><ul>{(news || []).map((n: any, i: number) => <li key={i}>{n.title} ({n.risk_label})</li>)}</ul><div>news_risk_score: {news?.filter((x: any) => x.risk_label === 'high').length || 0}</div></div>
    <div><b>建议操作</b><div>{state?.stage === '急跌' ? '减仓/观察' : '加仓/观察'}</div><button className='btn' onClick={() => onAdopt(module)}>采纳到建议单草稿</button></div>
  </div>
}
