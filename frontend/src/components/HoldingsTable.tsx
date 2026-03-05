export default function HoldingsTable({ holdings }: any) {
  return <table><thead><tr><th>Ticker</th><th>Qty</th><th>Value</th><th>AvgCost</th><th>Notes</th></tr></thead><tbody>{holdings?.map((h: any, i: number) => <tr key={i}><td>{h.ticker}</td><td>{h.qty}</td><td>{h.value}</td><td>{h.avg_cost}</td><td>{h.notes}</td></tr>)}</tbody></table>
}
