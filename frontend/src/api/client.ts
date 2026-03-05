import axios from 'axios'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000' })

export const client = {
  getMacro: () => api.get('/api/state/macro').then(r => r.data),
  recomputeMacro: () => api.post('/api/state/macro/recompute').then(r => r.data),
  getPortfolio: () => api.get('/api/portfolio/current').then(r => r.data),
  saveSnapshot: (payload: any) => api.post('/api/portfolio/snapshot', payload).then(r => r.data),
  getModules: () => api.get('/api/modules').then(r => r.data),
  addModule: (payload: any) => api.post('/api/modules', payload).then(r => r.data),
  patchModule: (id: number, payload: any) => api.patch(`/api/modules/${id}`, payload).then(r => r.data),
  getModuleState: (id: number) => api.get(`/api/modules/${id}/state`).then(r => r.data),
  fetchNews: (module_id: number) => api.post('/api/news/fetch', null, { params: { module_id } }).then(r => r.data),
  generatePlan: (payload: any) => api.post('/api/tradeplan/generate', payload).then(r => r.data),
  recordExecution: (payload: any) => api.post('/api/execution/record', payload).then(r => r.data),
  runBacktest: (payload: any) => api.post('/api/backtest/run', payload).then(r => r.data),
  getBacktest: (id: number) => api.get(`/api/backtest/${id}`).then(r => r.data),
  saveKeys: (payload: any) => api.post('/api/admin/keys', payload).then(r => r.data),
  saveConfigVersion: (payload: any) => api.post('/api/admin/config/version', payload).then(r => r.data),
  currentConfigVersion: () => api.get('/api/admin/config/version/current').then(r => r.data),
}
