import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { API } from '../App';
import { Users, TrendingUp, Package, UserSquare, Sparkles, ShoppingCart, Warehouse, FolderKanban, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function Dashboard() {
  const [moduleStats, setModuleStats] = useState({
    crm: { leads: 0, customers: 0 },
    selling: { salesOrders: 0, invoices: 0 },
    buying: { purchaseOrders: 0, invoices: 0 },
    stock: { items: 0, lowStock: 0 },
    hr: { employees: 0, attendance: 0 },
    projects: { active: 0, total: 0 },
    timesheets: { total: 0, utilization: 0 }
  });
  const [company, setCompany] = useState({});

  useEffect(() => {
    fetchModuleStats();
    fetch(`${API}/company/settings`).then(r => r.ok ? r.json() : {}).then(setCompany).catch(() => {});
  }, []);

  const fetchModuleStats = async () => {
    try {
      const [leadsRes, customersRes, sosRes, siRes, posRes, piRes, itemsRes, empsRes, projectsRes, utilRes] = await Promise.all([
        axios.get(`${API}/crm/leads`).catch(() => ({ data: [] })),
        axios.get(`${API}/crm/customers`).catch(() => ({ data: [] })),
        axios.get(`${API}/selling/sales-orders`).catch(() => ({ data: [] })),
        axios.get(`${API}/selling/invoices`).catch(() => ({ data: [] })),
        axios.get(`${API}/purchase/orders`).catch(() => ({ data: [] })),
        axios.get(`${API}/purchase/invoices`).catch(() => ({ data: [] })),
        axios.get(`${API}/stock/items`).catch(() => ({ data: [] })),
        axios.get(`${API}/hr/employees`).catch(() => ({ data: [] })),
        axios.get(`${API}/projects/health/dashboard`).catch(() => ({ data: [] })),
        axios.get(`${API}/timesheets/utilization`).catch(() => ({ data: { summary: {} } })),
      ]);

      const projData = Array.isArray(projectsRes.data) ? projectsRes.data : [];
      const utilSummary = utilRes.data?.summary || {};

      setModuleStats({
        crm: { leads: leadsRes.data.length, customers: customersRes.data.length },
        selling: { salesOrders: sosRes.data.length, invoices: siRes.data.length },
        buying: { purchaseOrders: posRes.data.length, invoices: piRes.data.length },
        stock: { items: itemsRes.data.length, lowStock: itemsRes.data.filter(i => (i.current_stock || 0) <= (i.reorder_level || 0)).length },
        hr: { employees: empsRes.data.length, attendance: 0 },
        projects: { active: projData.filter(p => p.status !== 'CLOSED').length, total: projData.length },
        timesheets: { total: utilSummary.total_billable || 0, utilization: utilSummary.avg_utilization || 0 }
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const modules = [
    {
      title: 'CRM',
      icon: Users,
      color: 'bg-[#00C9A7]/100',
      link: '/crm',
      stats: [
        { label: 'Leads', value: moduleStats.crm.leads },
        { label: 'Customers', value: moduleStats.crm.customers }
      ]
    },
    {
      title: 'Selling',
      icon: TrendingUp,
      color: 'bg-[#00C9A7]/100',
      link: '/selling',
      stats: [
        { label: 'Sales Orders', value: moduleStats.selling.salesOrders },
        { label: 'Invoices', value: moduleStats.selling.invoices }
      ]
    },
    {
      title: 'Buying',
      icon: ShoppingCart,
      color: 'bg-[#00C9A7]/100',
      link: '/buying',
      stats: [
        { label: 'Purchase Orders', value: moduleStats.buying.purchaseOrders },
        { label: 'Invoices', value: moduleStats.buying.invoices }
      ]
    },
    {
      title: 'Stock',
      icon: Warehouse,
      color: 'bg-[#00C9A7]/100',
      link: '/stock',
      stats: [
        { label: 'Items', value: moduleStats.stock.items },
        { label: 'Low Stock', value: moduleStats.stock.lowStock }
      ]
    },
    {
      title: 'HR',
      icon: UserSquare,
      color: 'bg-orange-500',
      link: '/hr',
      stats: [
        { label: 'Employees', value: moduleStats.hr.employees },
        { label: 'Today Attendance', value: moduleStats.hr.attendance }
      ]
    },
    {
      title: 'Projects',
      icon: FolderKanban,
      color: 'bg-[#38bdf8]',
      link: '/projects-module',
      stats: [
        { label: 'Active', value: moduleStats.projects.active },
        { label: 'Total', value: moduleStats.projects.total }
      ]
    },
    {
      title: 'Timesheets',
      icon: Clock,
      color: 'bg-[#00d4aa]',
      link: '/timesheets',
      stats: [
        { label: 'Billable Hrs', value: moduleStats.timesheets.total },
        { label: 'Utilization', value: `${moduleStats.timesheets.utilization}%` }
      ]
    }
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center gap-4">
          {company.logo_url && (
            <img src={`${BACKEND_URL}${company.logo_url}`} alt="Company Logo" className="w-12 h-12 rounded-lg object-cover border border-[#1B2D42]" data-testid="dashboard-company-logo" />
          )}
          <div>
            <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="dashboard-title">
              {company.legal_name || company.short_name || 'Dashboard'}
            </h1>
            <p className="text-[#4A5B6E] mt-1">Welcome to Kairos AI ERP — AI-Powered Enterprise Resource Planning</p>
          </div>
        </div>

        {/* AI Assistant Banner */}
        <div className="bg-gradient-to-r from-[#002FA7] to-[#0039CC] p-8 rounded-sm text-white relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex items-center space-x-3 mb-3">
              <Sparkles size={32} className="text-white" />
              <h2 className="heading-font text-2xl font-bold">Universal AI Assistant</h2>
            </div>
            <p className="text-white/90 mb-4 max-w-2xl">
              Simply describe what you need in natural language. AI will understand and create the right document in the right module.
            </p>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-3 py-1 bg-[#152236]/20 rounded-full backdrop-blur-sm">"Raise PO for Azure cloud infra to Microsoft India - Rs.2,36,600"</span>
              <span className="px-3 py-1 bg-[#152236]/20 rounded-full backdrop-blur-sm">"Invoice HDFC AMC for PRJ-003 M2 milestone Rs.7,00,000"</span>
              <span className="px-3 py-1 bg-[#152236]/20 rounded-full backdrop-blur-sm">"Process March payroll for 21 employees"</span>
            </div>
          </div>
          <div className="absolute right-0 top-0 w-64 h-64 bg-[#152236]/10 rounded-full blur-3xl" />
        </div>

        {/* Module Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.title}
                to={module.link}
                className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm hover:shadow-lg transition-all group"
              >
                <div className={`${module.color} w-12 h-12 rounded-sm flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon size={24} className="text-white" />
                </div>
                <h3 className="heading-font text-xl font-bold text-[#E8EDF2] mb-3">{module.title}</h3>
                <div className="space-y-2">
                  {module.stats.map((stat) => (
                    <div key={stat.label} className="flex justify-between text-sm">
                      <span className="text-[#4A5B6E]">{stat.label}</span>
                      <span className="mono font-bold text-[#E8EDF2]">{stat.value}</span>
                    </div>
                  ))}
                </div>
              </Link>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-sm p-6">
          <h2 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <button className="border-2 border-[#1B2D42] hover:border-[#002FA7] hover:bg-[#00C9A7]/5 p-4 rounded-sm text-left transition-all">
              <p className="font-medium text-[#E8EDF2] text-sm">New Lead</p>
              <p className="text-xs text-[#4A5B6E] mt-1">Capture inquiry</p>
            </button>
            <button className="border-2 border-[#1B2D42] hover:border-[#002FA7] hover:bg-[#00C9A7]/5 p-4 rounded-sm text-left transition-all">
              <p className="font-medium text-[#E8EDF2] text-sm">Create Quotation</p>
              <p className="text-xs text-[#4A5B6E] mt-1">Sales document</p>
            </button>
            <button className="border-2 border-[#1B2D42] hover:border-[#002FA7] hover:bg-[#00C9A7]/5 p-4 rounded-sm text-left transition-all">
              <p className="font-medium text-[#E8EDF2] text-sm">Add Stock</p>
              <p className="text-xs text-[#4A5B6E] mt-1">Material receipt</p>
            </button>
            <button className="border-2 border-[#1B2D42] hover:border-[#002FA7] hover:bg-[#00C9A7]/5 p-4 rounded-sm text-left transition-all">
              <p className="font-medium text-[#E8EDF2] text-sm">Mark Attendance</p>
              <p className="text-xs text-[#4A5B6E] mt-1">HR operation</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;