import React, { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { FileText, TrendingUp, Package, Building, Users, Landmark, MessageSquare, BarChart3, Menu, X, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import PurchaseToPay from './pages/PurchaseToPay';
import OrderToCash from './pages/OrderToCash';
import Inventory from './pages/Inventory';
import FixedAssets from './pages/FixedAssets';
import Payroll from './pages/Payroll';
import Banking from './pages/Banking';
import Reports from './pages/Reports';
import ChartOfAccounts from './pages/ChartOfAccounts';
import CostCenters from './pages/CostCenters';
import MasterData from './pages/MasterData';
import CSVImport from './pages/CSVImport';
import AIPromptInterface from './components/AIPromptInterface';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/purchase-to-pay', label: 'P2P', icon: FileText },
    { path: '/order-to-cash', label: 'O2C', icon: TrendingUp },
    { path: '/inventory', label: 'Inventory', icon: Package },
    { path: '/fixed-assets', label: 'Assets', icon: Building },
    { path: '/payroll', label: 'Payroll', icon: Users },
    { path: '/banking', label: 'Banking', icon: Landmark },
    { path: '/reports', label: 'Reports', icon: MessageSquare },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="heading-font text-xl font-black tracking-tighter text-slate-900" data-testid="app-logo">
              Kairos Accounting
            </Link>
            <div className="hidden md:flex space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                    className={`px-3 py-2 text-sm font-medium transition-colors flex items-center space-x-2 rounded-sm ${
                      isActive
                        ? 'bg-[#002FA7] text-white'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
          <button
            className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-sm"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-toggle"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white" data-testid="mobile-menu">
          <div className="px-4 py-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-3 py-2 text-sm font-medium transition-colors rounded-sm ${
                    isActive
                      ? 'bg-[#002FA7] text-white'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <Icon size={16} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}

function SettingsRouter() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900">Settings</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link to="/settings/coa" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Chart of Accounts</h3>
            <p className="text-sm text-slate-600">Manage your ledger accounts and categories</p>
          </Link>
          <Link to="/settings/cost-centers" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Cost Centers</h3>
            <p className="text-sm text-slate-600">Define departments and project centers</p>
          </Link>
          <Link to="/settings/master-data" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Master Data</h3>
            <p className="text-sm text-slate-600">Vendors, Clients, and GSTIN lookup</p>
          </Link>
          <Link to="/settings/import" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">CSV Import</h3>
            <p className="text-sm text-slate-600">Bulk import transactions from Excel/CSV</p>
          </Link>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/purchase-to-pay" element={<PurchaseToPay />} />
          <Route path="/order-to-cash" element={<OrderToCash />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/fixed-assets" element={<FixedAssets />} />
          <Route path="/payroll" element={<Payroll />} />
          <Route path="/banking" element={<Banking />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<SettingsRouter />} />
          <Route path="/settings/coa" element={<ChartOfAccounts />} />
          <Route path="/settings/cost-centers" element={<CostCenters />} />
          <Route path="/settings/master-data" element={<MasterData />} />
          <Route path="/settings/import" element={<CSVImport />} />
        </Routes>
        <AIPromptInterface />
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;