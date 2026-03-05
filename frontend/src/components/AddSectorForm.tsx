import { useState } from 'react'

export default function AddSectorForm({ onAdd }: any) {
  const [form, setForm] = useState({ name: '', index_symbol: '', leveraged_symbol: '', leader_symbol: '' })
  return <div className='card'><h3>添加新板块</h3><div className='row'>{Object.keys(form).map((k) => <input key={k} placeholder={k} value={(form as any)[k]} onChange={e => setForm({ ...form, [k]: e.target.value })} />)}<button className='btn' onClick={() => onAdd(form)}>保存</button></div></div>
}
