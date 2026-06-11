import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Shield, LayoutDashboard, Search, Upload, Activity } from 'lucide-react'

// Import Pages
import Dashboard from './pages/Dashboard'
import UploadVideo from './pages/UploadVideo'
import SearchPortal from './pages/SearchPortal'
import EntityDetail from './pages/EntityDetail'

// Create React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Upload Footage', path: '/upload', icon: Upload },
    { name: 'Search Logs', path: '/search', icon: Search },
  ]

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col justify-between select-none">
      <div className="p-6">
        <Link to="/" className="flex items-center gap-3 text-indigo-400 font-extrabold text-xl tracking-tight">
          <Shield className="h-8 w-8 text-indigo-500 fill-indigo-500/10" />
          <span>ShieldCV</span>
        </Link>
        
        <nav className="mt-10 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/15'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      <div className="p-6 border-t border-slate-800 bg-slate-950/30 flex items-center gap-3">
        <div className="flex h-3 w-3 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </div>
        <span className="text-xs text-slate-400 font-medium">Node Security Live</span>
      </div>
    </aside>
  )
}

function MainLayout() {
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden text-slate-100">
      <Navigation />
      <main className="flex-1 overflow-y-auto bg-slate-950">
        <div className="max-w-7xl mx-auto p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadVideo />} />
            <Route path="/search" element={<SearchPortal />} />
            <Route path="/entity/:id" element={<EntityDetail />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <MainLayout />
      </Router>
    </QueryClientProvider>
  )
}
