import React, { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Users, ShoppingCart, Package, Building, UserSquare, 
  Briefcase, ClipboardCheck, Settings, ChevronDown, ChevronRight, 
  Menu, X, TrendingUp, Boxes, FileText, Receipt, BookOpen, Database
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import CRM from './pages/CRM';
import Sales from './pages/Sales';
import Purchase from './pages/Purchase';
import Stock from './pages/Stock';
import HR from './pages/HR';
import Projects from './pages/Projects';
import Quality from './pages/Quality';
import PurchaseToPay from './pages/PurchaseToPay';
import Reports from './pages/Reports';
import ChartOfAccounts from './pages/ChartOfAccounts';
import CostCenters from './pages/CostCenters';
import MasterData from './pages/MasterData';
import CSVImport from './pages/CSVImport';
import JournalEntry from './pages/JournalEntry';
import AdminDataTables from './pages/AdminDataTables';
import FinancialStatements from './pages/FinancialStatements';
import SellingModule from './pages/SellingModule';
import BuyingModule from './pages/BuyingModule';
import UniversalAI from './components/UniversalAI';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState(['selling', 'buying', 'stock', 'accounting']);

  const toggleSection = (section) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const isActive = (path) => location.pathname === path;

  const menuSections = [
    {
      id: 'core',
      title: 'Core',
      items: [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard }
      ]
    },
    {
      id: 'selling',
      title: 'Selling',
      items: [
        { path: '/crm', label: 'CRM', icon: Users },
        { path: '/selling', label: 'Sales Module', icon: TrendingUp },
      ]
    },
    {
      id: 'buying',
      title: 'Buying',
      items: [
        { path: '/buying', label: 'Purchase Module', icon: ShoppingCart },
      ]
    },
    {
      id: 'stock',
      title: 'Stock',
      items: [
        { path: '/stock', label: 'Inventory', icon: Boxes },
        { path: '/quality', label: 'Quality', icon: ClipboardCheck },
      ]
    },
    {
      id: 'hr',
      title: 'HR',
      items: [
        { path: '/hr', label: 'HR & Payroll', icon: UserSquare },
        { path: '/projects', label: 'Projects', icon: Briefcase },
      ]
    },
    {
      id: 'accounting',
      title: 'Accounting',
      items: [
        { path: '/journal-entries', label: 'Journal Entries', icon: BookOpen },
        { path: '/financial-statements', label: 'Financial Statements', icon: FileText },
      ]
    },
    {
      id: 'reports',
      title: 'Reports & Settings',
      items: [
        { path: '/reports', label: 'Reports', icon: FileText },
        { path: '/admin/tables', label: 'Data Tables', icon: Database },
        { path: '/settings', label: 'Settings', icon: Settings },
      ]
    }
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden" 
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-screen bg-white border-r border-slate-200 z-50 transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 w-64
      `}>
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200">
            <Link to="/" className="heading-font text-xl font-black tracking-tighter text-slate-900">
              Kairos
            </Link>
            <button 
              className="md:hidden p-2 hover:bg-slate-100 rounded-sm"
              onClick={() => setIsOpen(false)}
            >
              <X size={20} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-3 space-y-1">
            {menuSections.map((section) => (
              <div key={section.id} className="mb-2">
                <button
                  onClick={() => toggleSection(section.id)}
                  className="w-full flex items-center justify-between px-3 py-2 text-xs tracking-widest uppercase font-bold text-slate-500 hover:bg-slate-50 rounded-sm transition-colors"
                >
                  <span>{section.title}</span>
                  {expandedSections.includes(section.id) ? 
                    <ChevronDown size={14} /> : <ChevronRight size={14} />
                  }
                </button>
                {expandedSections.includes(section.id) && (
                  <div className="mt-1 space-y-1">
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          onClick={() => window.innerWidth < 768 && setIsOpen(false)}
                          className={`flex items-center space-x-3 px-3 py-2 text-sm rounded-sm transition-colors ${
                            isActive(item.path)
                              ? 'bg-[#002FA7] text-white'
                              : 'text-slate-700 hover:bg-slate-100'
                          }`}
                        >
                          <Icon size={16} />
                          <span>{item.label}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-3 border-t border-slate-200 text-xs text-slate-500">
            <p>Kairos Accounting v2.0</p>
            <p className="text-[10px] mt-1">AI-Powered ERP</p>
          </div>
        </div>
      </aside>
    </>
  );
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="App">
      <BrowserRouter>
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
        
        <div className="md:ml-64 min-h-screen bg-[#FAFAFA]">
          {/* Top bar */}
          <div className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sticky top-0 z-30">
            <button 
              className="md:hidden p-2 hover:bg-slate-100 rounded-sm"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={24} />
            </button>
            <div className="flex-1" />
            <button className="text-sm text-slate-600 hover:text-slate-900 font-medium">
              Admin
            </button>
          </div>

          {/* Main content */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/purchase" element={<Purchase />} />
            <Route path="/stock" element={<Stock />} />
            <Route path="/hr" element={<HR />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/quality" element={<Quality />} />
            <Route path="/purchase-to-pay" element={<PurchaseToPay />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<SettingsRouter />} />
            <Route path="/settings/coa" element={<ChartOfAccounts />} />
            <Route path="/settings/cost-centers" element={<CostCenters />} />
            <Route path="/settings/master-data" element={<MasterData />} />
            <Route path="/settings/import" element={<CSVImport />} />
            <Route path="/journal-entries" element={<JournalEntry />} />
            <Route path="/admin/tables" element={<AdminDataTables />} />
            <Route path="/financial-statements" element={<FinancialStatements />} />
            <Route path="/selling" element={<SellingModule />} />
            <Route path="/buying" element={<BuyingModule />} />
          </Routes>
          
          <UniversalAI />
        </div>
        
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

function SettingsRouter() {
  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900">Settings</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link to="/settings/coa" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Chart of Accounts</h3>
            <p className="text-sm text-slate-600">Manage ledger accounts</p>
          </Link>
          <Link to="/settings/cost-centers" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Cost Centers</h3>
            <p className="text-sm text-slate-600">Define departments</p>
          </Link>
          <Link to="/settings/master-data" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">Master Data</h3>
            <p className="text-sm text-slate-600">Vendors & Clients</p>
          </Link>
          <Link to="/settings/import" className="bg-white border border-slate-200 p-6 rounded-sm hover:shadow-sm transition-all">
            <h3 className="heading-font text-lg font-bold text-slate-900 mb-2">CSV Import</h3>
            <p className="text-sm text-slate-600">Bulk import data</p>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default App;