import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import ExecutionBacktest from './pages/ExecutionBacktest'
import './styles.css'

function App() {
  return (
    <BrowserRouter>
      <nav className="nav"><Link to="/">Dashboard</Link><Link to="/admin">Admin</Link><Link to="/execution">Execution & Backtest</Link></nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/execution" element={<ExecutionBacktest />} />
      </Routes>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
