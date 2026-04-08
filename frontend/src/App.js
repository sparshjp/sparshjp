import React, { useState, useRef, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { 
  LayoutDashboard, Users, ShoppingCart, Package, Building, UserSquare, 
  Briefcase, ClipboardCheck, Settings, ChevronDown, ChevronRight, 
  Menu, X, TrendingUp, Boxes, FileText, Receipt, BookOpen, Database,
  Scale, IndianRupee, Factory, Building2, Sparkles, Shield, QrCode, Clock,
  FolderKanban, ArrowLeftRight, CreditCard, User, Lock, Unlock, LogOut,
  CheckSquare, Wallet, ScrollText, UserCog, DollarSign, Bell, FolderOpen, Globe
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
// MasterData replaced by VendorsPage, CustomersPage, ItemsPage
import CSVImport from './pages/CSVImport';
import JournalEntry from './pages/JournalEntry';
import AdminDataTables from './pages/AdminDataTables';
import FinancialStatements from './pages/FinancialStatements';
import SellingModule from './pages/SellingModule';
import BuyingModule from './pages/BuyingModule';
import GSTModule from './pages/GSTModule';
import GSTR1Page from './pages/GSTR1Page';
import GSTR3BPage from './pages/GSTR3BPage';
import EInvoicePage from './pages/EInvoicePage';
import TDSPage from './pages/TDSPage';
import VendorsPage from './pages/VendorsPage';
import CustomersPage from './pages/CustomersPage';
import ItemsPage from './pages/ItemsPage';
import AgingReport from './pages/AgingReport';
import ProjectsModule from './pages/ProjectsModule';
import TimesheetsPage from './pages/TimesheetsPage';
import RevenueRecognition from './pages/RevenueRecognition';
import TransactionExplorer from './pages/TransactionExplorer';
import BankReconciliation from './pages/BankReconciliation';
import AIAgentsPage from './pages/AIAgentsPage';
import ManufacturingModule from './pages/ManufacturingModule';
import CompanySetup from './pages/CompanySetup';
import ReportingAI from './pages/ReportingAI';
import AuditTrail from './pages/AuditTrail';
import UniversalAI from './components/UniversalAI';
import { KairosIcon } from './components/KairosIcon';
import { Toaster } from './components/ui/sonner';
import ExpenseManagement from './pages/ExpenseManagement';
import FeedbackPage from './pages/FeedbackPage';
import LeadEnrichment from './pages/LeadEnrichment';
import ProformaARLink from './pages/ProformaARLink';
import ItemSampleTracking from './pages/ItemSampleTracking';
import LeadProbabilityScore from './pages/LeadProbabilityScore';
import AnnouncementsPage from './pages/AnnouncementsPage';
import UserManagement from './pages/UserManagement';
import ApprovalsPage from './pages/ApprovalsPage';
import BudgetsPage from './pages/BudgetsPage';
import ContractsPage from './pages/ContractsPage';
import ResourcesPage from './pages/ResourcesPage';
import ForexPage from './pages/ForexPage';
import BillingPage from './pages/BillingPage';
import DocumentsPage from './pages/DocumentsPage';
import NotificationsPage from './pages/NotificationsPage';
import CompliancePage from './pages/CompliancePage';
import PortalPage from './pages/PortalPage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation();
  const { creatorMode } = useAuth();
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
      id: 'master-data',
      title: 'Master Data',
      items: [
        { path: '/vendors', label: 'Vendors', icon: Building },
        { path: '/customers', label: 'Customers', icon: Users },
        { path: '/items', label: 'Items', icon: Package },
        { path: '/settings', label: 'CoA & Settings', icon: Settings },
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
      ]
    },
    {
      id: 'delivery',
      title: 'Delivery',
      items: [
        { path: '/projects-module', label: 'Project Management', icon: FolderKanban },
        { path: '/timesheets', label: 'Timesheets', icon: Clock },
      ]
    },
    {
      id: 'accounting',
      title: 'Accounting',
      items: [
        { path: '/journal-entries', label: 'Journal Entries', icon: BookOpen },
        { path: '/revenue-recognition', label: 'Revenue (Ind AS 115)', icon: TrendingUp },
        { path: '/financial-statements', label: 'Financial Statements', icon: FileText },
        { path: '/aging-report', label: 'AP / AR Aging', icon: Clock },
        { path: '/bank-reconciliation', label: 'Bank Reconciliation', icon: ArrowLeftRight },
        { path: '/expense-management', label: 'Expense Management', icon: CreditCard },
        { path: '/audit-trail', label: 'Audit Trail', icon: Shield },
      ]
    },
    {
      id: 'approvals',
      title: 'Approvals',
      items: [
        { path: '/approvals', label: 'Approval Workflows', icon: CheckSquare },
      ]
    },
    {
      id: 'budgets',
      title: 'Budgets',
      items: [
        { path: '/budgets', label: 'Budget Management', icon: Wallet },
      ]
    },
    {
      id: 'contracts',
      title: 'Contracts',
      items: [
        { path: '/contracts', label: 'Contract Management', icon: ScrollText },
      ]
    },
    {
      id: 'resources',
      title: 'Resources',
      items: [
        { path: '/resources', label: 'Resource Planning', icon: UserCog },
      ]
    },
    {
      id: 'forex',
      title: 'Forex',
      items: [
        { path: '/forex', label: 'Multi-Currency', icon: DollarSign },
      ]
    },
    {
      id: 'billing',
      title: 'Billing',
      items: [
        { path: '/billing', label: 'Billing Automation', icon: Receipt },
      ]
    },
    {
      id: 'doc-mgmt',
      title: 'Documents',
      items: [
        { path: '/doc-management', label: 'Document Manager', icon: FolderOpen },
      ]
    },
    {
      id: 'notifications',
      title: 'Notifications',
      items: [
        { path: '/notifications', label: 'Notification Center', icon: Bell },
      ]
    },
    {
      id: 'compliance',
      title: 'Compliance',
      items: [
        { path: '/compliance', label: 'Audit & Compliance', icon: Shield },
      ]
    },
    {
      id: 'portal',
      title: 'Client Portal',
      items: [
        { path: '/client-portal', label: 'Portal Setup', icon: Globe },
      ]
    },
    {
      id: 'gst',
      title: 'GST',
      items: [
        { path: '/gst-dashboard', label: 'GST Dashboard', icon: IndianRupee },
        { path: '/gstr-1', label: 'GSTR-1 (Outward)', icon: FileText },
        { path: '/gstr-3b', label: 'GSTR-3B (Summary)', icon: Receipt },
        { path: '/e-invoicing', label: 'E-Invoicing', icon: QrCode },
      ]
    },
    {
      id: 'tds',
      title: 'TDS',
      items: [
        { path: '/tds-returns', label: 'TDS Returns (26Q)', icon: Scale },
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
        { path: '/transaction-explorer', label: 'Transaction Explorer', icon: FileText },
        { path: '/reports', label: 'Reports', icon: FileText },
        { path: '/admin/tables', label: 'Data Tables', icon: Database },
      ]
    },
    {
      id: 'user-management',
      title: 'Administration',
      items: [
        { path: '/user-management', label: 'User Management', icon: Users },
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
              <KairosIcon size={28} />
              <div className="border-l border-[#1B2D42] pl-3 h-8 flex flex-col justify-center">
                <span className="text-sm font-bold tracking-[3px] text-white leading-none">KAIROS</span>
                <span className="text-[8px] tracking-[4px] text-[#00C9A7] uppercase leading-none mt-1">AI ERP</span>
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

          {/* Footer — Kairos Engine link when in creator mode */}
          {creatorMode && (
            <div className="p-3 border-t border-[#1B2D42]">
              <Link
                to="/ai-agents"
                onClick={() => window.innerWidth < 768 && setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  isActive('/ai-agents')
                    ? 'bg-[#00C9A7]/15 text-[#00C9A7] border border-[#00C9A7]/30'
                    : 'text-[#00C9A7] hover:bg-[#00C9A7]/10 border border-[#00C9A7]/20'
                }`}
                data-testid="kairos-engine-link"
              >
                <Sparkles size={16} />
                <span className="font-semibold">Kairos AI Engine</span>
              </Link>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}


function CreatorLoginPage() {
  const navigate = useNavigate();
  const { enterCreatorMode } = useAuth();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      await enterCreatorMode(password);
      navigate('/ai-agents');
    } catch (e) {
      setError(e.message || 'Invalid password');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#060e1a] flex items-center justify-center p-4">
      <div className="w-full max-w-sm" data-testid="creator-login-page">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#a78bfa]/10 border border-[#a78bfa]/20 mb-4">
            <Sparkles size={28} className="text-[#a78bfa]" />
          </div>
          <h1 className="text-xl font-bold text-[#E8EDF2] mb-1">Creator Mode</h1>
          <p className="text-sm text-[#4A5B6E]">Authenticate to access Kairos AI Engine</p>
        </div>

        <div className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 space-y-4">
          <div>
            <label className="text-xs text-[#7A8BA0] mb-1.5 block">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && password) handleLogin(); }}
              placeholder="Enter creator password"
              className="w-full px-4 py-3 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#a78bfa] placeholder:text-[#4A5B6E]/60 transition-colors"
              autoFocus
              data-testid="creator-password-input"
            />
          </div>

          {error && (
            <p className="text-xs text-[#ef4444] bg-[#ef4444]/10 rounded-lg px-3 py-2" data-testid="creator-login-error">{error}</p>
          )}

          <button
            onClick={handleLogin}
            disabled={loading || !password}
            className="w-full px-4 py-3 bg-[#a78bfa] text-white rounded-lg text-sm font-bold hover:bg-[#9572f5] disabled:opacity-50 transition-all"
            data-testid="creator-login-btn"
          >
            {loading ? 'Verifying...' : 'Unlock Creator Mode'}
          </button>

          <button
            onClick={() => navigate('/')}
            className="w-full px-4 py-2 text-sm text-[#4A5B6E] hover:text-[#7A8BA0] transition-colors"
            data-testid="creator-login-back"
          >
            Back to ERP
          </button>
        </div>
      </div>
    </div>
  );
}

function AppShell({ sidebarOpen, setSidebarOpen }) {
  const loc = useLocation();
  const navigate = useNavigate();
  const isAIEngine = loc.pathname === '/ai-agents';
  const isCreatorLogin = loc.pathname === '/creator-login';
  const { user, creatorMode, exitCreatorMode } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClick = (e) => { if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowDropdown(false); };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Creator login page — show without sidebar/header
  if (isCreatorLogin && !creatorMode) {
    return (
      <>
        <Routes>
          <Route path="/creator-login" element={<CreatorLoginPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-right" richColors theme="dark" />
      </>
    );
  }

  return (
    <>
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="md:ml-64 min-h-screen bg-[#0D1B2A]">
        <div className="h-14 bg-[#152236] border-b border-[#1B2D42] flex items-center justify-between px-4 sticky top-0 z-30">
          <button className="md:hidden p-2 hover:bg-[#1B2D42] rounded text-[#7A8BA0]" onClick={() => setSidebarOpen(true)}>
            <Menu size={24} />
          </button>
          <div className="flex-1" />
          {/* Role Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-[#1B2D42] transition-colors"
              data-testid="role-dropdown-trigger"
            >
              <div className="w-7 h-7 rounded-full bg-[#00C9A7]/20 flex items-center justify-center">
                <User size={13} className="text-[#00C9A7]" />
              </div>
              <span className="text-xs text-[#E8EDF2] font-medium">{user.name}</span>
              {creatorMode && (
                <span className="px-1.5 py-0.5 rounded-full text-[9px] font-bold bg-[#a78bfa]/15 text-[#a78bfa] border border-[#a78bfa]/30">Creator</span>
              )}
              <ChevronDown size={14} className="text-[#4A5B6E]" />
            </button>

            {showDropdown && (
              <div className="absolute right-0 top-full mt-1 w-56 bg-[#0D1B2A] border border-[#1B2D42] rounded-xl shadow-2xl overflow-hidden z-50" data-testid="role-dropdown-menu">
                <div className="p-3 border-b border-[#1B2D42]">
                  <p className="text-[10px] text-[#4A5B6E] uppercase tracking-wider mb-1">Current Role</p>
                  <p className="text-sm text-[#E8EDF2] font-medium">{creatorMode ? 'Creator' : 'User'}</p>
                </div>
                <div className="p-1.5">
                  {!creatorMode ? (
                    <button
                      onClick={() => { setShowDropdown(false); navigate('/creator-login'); }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[#a78bfa] hover:bg-[#a78bfa]/10 transition-colors"
                      data-testid="switch-to-creator"
                    >
                      <Lock size={15} />
                      <span>Switch to Creator</span>
                    </button>
                  ) : (
                    <>
                      <Link
                        to="/ai-agents"
                        onClick={() => setShowDropdown(false)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[#00C9A7] hover:bg-[#00C9A7]/10 transition-colors"
                        data-testid="go-to-kairos"
                      >
                        <Sparkles size={15} />
                        <span>Kairos AI Engine</span>
                      </Link>
                      <button
                        onClick={() => { exitCreatorMode(); setShowDropdown(false); navigate('/'); }}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors"
                        data-testid="exit-creator-mode"
                      >
                        <LogOut size={15} />
                        <span>Exit Creator Mode</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        <div className={isAIEngine ? '' : 'p-4 sm:p-6'}>
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
            <Route path="/settings/import" element={<CSVImport />} />
            <Route path="/journal-entries" element={<JournalEntry />} />
            <Route path="/admin/tables" element={<AdminDataTables />} />
            <Route path="/financial-statements" element={<FinancialStatements />} />
            <Route path="/selling" element={<SellingModule />} />
            <Route path="/buying" element={<BuyingModule />} />
            <Route path="/manufacturing" element={<ManufacturingModule />} />
            <Route path="/gst-tds" element={<GSTModule />} />
            <Route path="/gst-dashboard" element={<GSTModule />} />
            <Route path="/gstr-1" element={<GSTR1Page />} />
            <Route path="/gstr-3b" element={<GSTR3BPage />} />
            <Route path="/e-invoicing" element={<EInvoicePage />} />
            <Route path="/tds-returns" element={<TDSPage />} />
            <Route path="/vendors" element={<VendorsPage />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/items" element={<ItemsPage />} />
            <Route path="/aging-report" element={<AgingReport />} />
            <Route path="/company-setup" element={<CompanySetup />} />
            <Route path="/reporting-ai" element={<ReportingAI />} />
            <Route path="/audit-trail" element={<AuditTrail />} />
            <Route path="/projects-module" element={<ProjectsModule />} />
            <Route path="/timesheets" element={<TimesheetsPage />} />
            <Route path="/revenue-recognition" element={<RevenueRecognition />} />
            <Route path="/transaction-explorer" element={<TransactionExplorer />} />
            <Route path="/bank-reconciliation" element={<BankReconciliation />} />
            <Route path="/ai-agents" element={creatorMode ? <AIAgentsPage /> : <Navigate to="/" replace />} />
            <Route path="/creator-login" element={creatorMode ? <Navigate to="/" replace /> : <CreatorLoginPage />} />
            <Route path="/expense-management" element={<ExpenseManagement />} />
            <Route path="/feedback" element={<FeedbackPage />} />
            <Route path="/leads/enrich" element={<LeadEnrichment />} />
            <Route path="/proformas/ar-link" element={<ProformaARLink />} />
            <Route path="/items/sample-tracking" element={<ItemSampleTracking />} />
            <Route path="/leads/probability" element={<LeadProbabilityScore />} />
            <Route path="/announcements" element={<AnnouncementsPage />} />
            <Route path="/user-management" element={<UserManagement />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/budgets" element={<BudgetsPage />} />
            <Route path="/contracts" element={<ContractsPage />} />
            <Route path="/resources" element={<ResourcesPage />} />
            <Route path="/forex" element={<ForexPage />} />
            <Route path="/billing" element={<BillingPage />} />
            <Route path="/doc-management" element={<DocumentsPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/compliance" element={<CompliancePage />} />
            <Route path="/client-portal" element={<PortalPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        {!isAIEngine && <UniversalAI />}
      </div>
    </>
  );
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppShell sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
          <Toaster position="top-right" richColors theme="dark" />
        </AuthProvider>
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
        <Link to="/settings/import" className="bg-[#152236] border border-[#1B2D42] p-6 rounded-lg hover:border-[#00C9A7]/30 transition-all">
          <h3 className="text-lg font-bold text-[#E8EDF2] mb-2">CSV Import</h3>
          <p className="text-sm text-[#4A5B6E]">Bulk import data</p>
        </Link>
      </div>
    </div>
  );
}

export default App;