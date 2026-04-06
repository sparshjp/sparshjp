import React, { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Users, ShoppingCart, Package, Building, UserSquare, 
  Briefcase, ClipboardCheck, Settings, ChevronDown, ChevronRight, 
  Menu, X, TrendingUp, Boxes, FileText, Receipt, BookOpen, Database,
  Scale, IndianRupee, Factory, Building2, Sparkles
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
import GSTModule from './pages/GSTModule';
import ManufacturingModule from './pages/ManufacturingModule';
import CompanySetup from './pages/CompanySetup';
import ReportingAI from './pages/ReportingAI';
import UniversalAI from './components/UniversalAI';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState(['core', 'selling', 'buying', 'stock', 'accounting', 'reporting-ai']);

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
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/company-setup', label: 'Company Setup', icon: Building2 },
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
      title: 'Stock & Manufacturing',
      items: [
        { path: '/stock', label: 'Inventory', icon: Boxes },
        { path: '/manufacturing', label: 'Manufacturing', icon: Factory },
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
        { path: '/gst-tds', label: 'GST & TDS', icon: Scale },
      ]
    },
    {
      id: 'reporting-ai',
      title: 'Reporting AI',
      items: [
        { path: '/reporting-ai', label: 'Ask Kairos AI', icon: Sparkles },
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
        fixed top-0 left-0 h-screen bg-[#0D1B2A] border-r border-[#1B2D42] z-50 transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 w-64
      `}>
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-[#1B2D42]">
            <Link to="/" className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <div className="w-1 h-6 bg-[#0D1B2A] rounded-sm" />
                <div className="flex flex-col gap-0.5">
                  <div className="w-2.5 h-0.5 bg-[#00C9A7] -rotate-12" />
                  <div className="w-2.5 h-0.5 bg-[#00C9A7] rotate-12" />
                </div>
                <div className="w-1.5 h-1.5 rounded-full bg-[#00C9A7]" />
              </div>
              <div className="border-l border-[#1B2D42] pl-3 h-8 flex flex-col justify-center">
                <span className="text-sm font-bold tracking-[3px] text-white leading-none">KAIROS</span>
                <span className="text-[8px] tracking-[4px] text-[#00C9A7] uppercase leading-none mt-1">Advisory</span>
              </div>
            </Link>
            <button 
              className="md:hidden p-2 hover:bg-[#1B2D42] rounded text-[#7A8BA0]"
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
                  className="w-full flex items-center justify-between px-3 py-2 text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] hover:text-[#7A8BA0] hover:bg-[#152236] rounded transition-colors"
                >
                  <span>{section.title}</span>
                  {expandedSections.includes(section.id) ? 
                    <ChevronDown size={14} /> : <ChevronRight size={14} />
                  }
                </button>
                {expandedSections.includes(section.id) && (
                  <div className="mt-1 space-y-0.5">
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          onClick={() => window.innerWidth < 768 && setIsOpen(false)}
                          className={`flex items-center space-x-3 px-3 py-2 text-sm rounded transition-all ${
                            isActive(item.path)
                              ? 'bg-[#00C9A7]/15 text-[#00C9A7] border-l-2 border-[#00C9A7]'
                              : 'text-[#7A8BA0] hover:bg-[#152236] hover:text-[#E8EDF2]'
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
          <div className="p-3 border-t border-[#1B2D42] text-xs text-[#4A5B6E]">
            <p className="font-semibold tracking-wider">Kairos Advisory</p>
            <p className="text-[10px] mt-1 text-[#00C9A7]">AI-Powered ERP</p>
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
        
        <div className="md:ml-64 min-h-screen bg-[#0D1B2A]">
          {/* Top bar */}
          <div className="h-14 bg-[#152236] border-b border-[#1B2D42] flex items-center justify-between px-4 sticky top-0 z-30">
            <button 
              className="md:hidden p-2 hover:bg-[#1B2D42] rounded text-[#7A8BA0]"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={24} />
            </button>
            <div className="flex-1" />
            <button className="text-sm text-[#7A8BA0] hover:text-[#00C9A7] font-medium transition-colors">
              Admin
            </button>
          </div>

          {/* Main content */}
          <div className="p-4 sm:p-6">
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
            <Route path="/manufacturing" element={<ManufacturingModule />} />
            <Route path="/gst-tds" element={<GSTModule />} />
            <Route path="/company-setup" element={<CompanySetup />} />
            <Route path="/reporting-ai" element={<ReportingAI />} />
          </Routes>
          </div>
          
          <UniversalAI />
        </div>
        
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

function SettingsRouter() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">Settings</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link to="/settings/coa" className="bg-[#152236] border border-[#1B2D42] p-6 rounded-lg hover:border-[#00C9A7]/30 transition-all">
          <h3 className="text-lg font-bold text-[#E8EDF2] mb-2">Chart of Accounts</h3>
          <p className="text-sm text-[#4A5B6E]">Manage ledger accounts</p>
        </Link>
        <Link to="/settings/cost-centers" className="bg-[#152236] border border-[#1B2D42] p-6 rounded-lg hover:border-[#00C9A7]/30 transition-all">
          <h3 className="text-lg font-bold text-[#E8EDF2] mb-2">Cost Centers</h3>
          <p className="text-sm text-[#4A5B6E]">Define departments</p>
        </Link>
        <Link to="/settings/master-data" className="bg-[#152236] border border-[#1B2D42] p-6 rounded-lg hover:border-[#00C9A7]/30 transition-all">
          <h3 className="text-lg font-bold text-[#E8EDF2] mb-2">Master Data</h3>
          <p className="text-sm text-[#4A5B6E]">Vendors & Clients</p>
        </Link>
        <Link to="/settings/import" className="bg-[#152236] border border-[#1B2D42] p-6 rounded-lg hover:border-[#00C9A7]/30 transition-all">
          <h3 className="text-lg font-bold text-[#E8EDF2] mb-2">CSV Import</h3>
          <p className="text-sm text-[#4A5B6E]">Bulk import data</p>
        </Link>
      </div>
    </div>
  );
}

export default App;