import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import {
  CreditCard, Plus, CheckCircle2, XCircle, Clock, DollarSign,
  User, Filter, ChevronDown, ChevronUp, X, Loader2, Receipt
} from 'lucide-react';

const CATEGORIES = ['travel', 'meals', 'software', 'hardware', 'office', 'other'];
const STATUSES = ['pending', 'approved', 'rejected', 'reimbursed'];
const CATEGORY_COLORS = {
  travel: '#60a5fa', meals: '#f59e0b', software: '#a78bfa',
  hardware: '#22c55e', office: '#06b6d4', other: '#4A5B6E',
};
const STATUS_COLORS = {
  pending: '#f59e0b', approved: '#22c55e', rejected: '#ef4444', reimbursed: '#06b6d4',
};

export default function ExpenseManagement() {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState({ status: '', category: '' });
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    employee_id: '', employee_name: '', category: 'travel',
    description: '', amount: '', currency: 'INR', receipt_url: '',
  });

  const loadData = useCallback(async () => {
    try {
      const [expRes, sumRes] = await Promise.all([
        fetch(`${API}/expenses`).then(r => r.json()),
        fetch(`${API}/expenses/summary`).then(r => r.json()),
      ]);
      setExpenses(Array.isArray(expRes) ? expRes : []);
      setSummary(sumRes);
    } catch { }
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const createExpense = async (e) => {
    e.preventDefault();
    if (!form.employee_name || !form.description || !form.amount) return;
    setSubmitting(true);
    try {
      await fetch(`${API}/expenses`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, amount: parseFloat(form.amount) }),
      });
      setForm({ employee_id: '', employee_name: '', category: 'travel', description: '', amount: '', currency: 'INR', receipt_url: '' });
      setShowForm(false);
      loadData();
    } catch { }
    setSubmitting(false);
  };

  const updateStatus = async (id, action) => {
    try {
      await fetch(`${API}/expenses/${id}/${action}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved_by: 'Admin', rejection_reason: 'Policy violation' }),
      });
      loadData();
    } catch { }
  };

  const filtered = expenses.filter(exp => {
    if (filter.status && exp.status !== filter.status) return false;
    if (filter.category && exp.category !== filter.category) return false;
    return true;
  });

  const fmt = (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n || 0);

  if (loading) return (
    <div className="flex items-center justify-center h-64" data-testid="expense-loading">
      <Loader2 className="animate-spin text-[#00d4aa]" size={24} />
    </div>
  );

  return (
    <div className="p-6 space-y-6" data-testid="expense-management-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00d4aa]/15 to-[#00d4aa]/5 border border-[#00d4aa]/20 flex items-center justify-center">
            <CreditCard size={20} className="text-[#00d4aa]" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#E8EDF2]" data-testid="expense-title">Expense Management</h1>
            <p className="text-xs text-[#4A5B6E]">{expenses.length} expense{expenses.length !== 1 ? 's' : ''} tracked</p>
          </div>
        </div>
        <button onClick={() => setShowForm(!showForm)} data-testid="new-expense-btn"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#00d4aa]/15 text-[#00d4aa] border border-[#00d4aa]/30 text-xs font-bold hover:bg-[#00d4aa]/25 transition-colors">
          <Plus size={14} /> New Expense
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="expense-summary">
          <SummaryCard label="Total Expenses" value={summary.total_expenses || 0} icon={Receipt} color="#E8EDF2" />
          <SummaryCard label="Pending Amount" value={fmt(summary.total_pending_amount)} icon={Clock} color="#f59e0b" />
          <SummaryCard label="Approved Amount" value={fmt(summary.total_approved_amount)} icon={CheckCircle2} color="#22c55e" />
          <SummaryCard label="Categories" value={summary.total_by_category?.length || 0} icon={Filter} color="#a78bfa" />
        </div>
      )}

      {/* Category breakdown */}
      {summary?.total_by_category?.length > 0 && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-xl p-4" data-testid="category-breakdown">
          <h3 className="text-xs font-bold text-[#4A5B6E] uppercase tracking-wider mb-3">By Category</h3>
          <div className="flex flex-wrap gap-2">
            {summary.total_by_category.map((cat, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#1B2D42] bg-[#152236]">
                <div className="w-2 h-2 rounded-full" style={{ background: CATEGORY_COLORS[cat.category] || '#4A5B6E' }} />
                <span className="text-[10px] font-bold text-[#E8EDF2] capitalize">{cat.category || 'Unknown'}</span>
                <span className="text-[10px] text-[#4A5B6E]">{fmt(cat.total)} ({cat.count})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Expense Form */}
      {showForm && (
        <form onSubmit={createExpense} className="bg-[#0A1628] border border-[#00d4aa]/20 rounded-xl p-5 space-y-4" data-testid="expense-form">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#E8EDF2]">New Expense</h3>
            <button type="button" onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={16} /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input value={form.employee_name} onChange={e => setForm({ ...form, employee_name: e.target.value })}
              placeholder="Employee Name" required data-testid="expense-employee-name"
              className="px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/40" />
            <input value={form.employee_id} onChange={e => setForm({ ...form, employee_id: e.target.value })}
              placeholder="Employee ID (e.g. EMP-001)" data-testid="expense-employee-id"
              className="px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/40" />
            <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} data-testid="expense-category"
              className="px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs text-[#E8EDF2] focus:outline-none focus:border-[#00d4aa]/40">
              {CATEGORIES.map(c => <option key={c} value={c} className="capitalize">{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
              placeholder="Description" required data-testid="expense-description"
              className="md:col-span-2 px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/40" />
            <input value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })}
              placeholder="Amount (INR)" type="number" step="0.01" required data-testid="expense-amount"
              className="px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/40" />
          </div>
          <div className="flex justify-end">
            <button type="submit" disabled={submitting} data-testid="submit-expense-btn"
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[#00d4aa] text-[#0D1B2A] text-xs font-bold hover:bg-[#00d4aa]/90 transition-colors disabled:opacity-50">
              {submitting ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />} Submit Expense
            </button>
          </div>
        </form>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap" data-testid="expense-filters">
        <div className="flex items-center gap-1.5">
          <Filter size={12} className="text-[#4A5B6E]" />
          <span className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Filter:</span>
        </div>
        <select value={filter.status} onChange={e => setFilter({ ...filter, status: e.target.value })} data-testid="filter-status"
          className="px-2.5 py-1.5 rounded-lg bg-[#152236] border border-[#1B2D42] text-[10px] text-[#E8EDF2] focus:outline-none">
          <option value="">All Statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
        <select value={filter.category} onChange={e => setFilter({ ...filter, category: e.target.value })} data-testid="filter-category"
          className="px-2.5 py-1.5 rounded-lg bg-[#152236] border border-[#1B2D42] text-[10px] text-[#E8EDF2] focus:outline-none">
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
        </select>
        {(filter.status || filter.category) && (
          <button onClick={() => setFilter({ status: '', category: '' })}
            className="text-[10px] text-[#ef4444] hover:text-[#ef4444]/80 flex items-center gap-1">
            <X size={10} /> Clear
          </button>
        )}
        <span className="text-[10px] text-[#4A5B6E] ml-auto">{filtered.length} result{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Expense Table */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-xl overflow-hidden" data-testid="expense-table">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1B2D42]">
                {['Employee', 'Category', 'Description', 'Amount', 'Status', 'Date', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left text-[9px] font-bold uppercase tracking-wider text-[#4A5B6E]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-xs text-[#4A5B6E]">No expenses found</td></tr>
              ) : (
                filtered.map((exp, i) => (
                  <tr key={exp.id || i} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/30 transition-colors" data-testid={`expense-row-${i}`}>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <User size={12} className="text-[#4A5B6E]" />
                        <div>
                          <p className="text-[11px] font-medium text-[#E8EDF2]">{exp.employee_name || '-'}</p>
                          <p className="text-[9px] text-[#4A5B6E]">{exp.employee_id || ''}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold capitalize border"
                        style={{ color: CATEGORY_COLORS[exp.category] || '#4A5B6E', borderColor: `${CATEGORY_COLORS[exp.category] || '#4A5B6E'}40`, background: `${CATEGORY_COLORS[exp.category] || '#4A5B6E'}10` }}>
                        {exp.category || 'other'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-[11px] text-[#c8d4e0] max-w-[200px] truncate">{exp.description || '-'}</td>
                    <td className="px-4 py-2.5">
                      <span className="text-[11px] font-bold text-[#E8EDF2]">{fmt(exp.amount)}</span>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold capitalize"
                        style={{ color: STATUS_COLORS[exp.status] || '#4A5B6E', background: `${STATUS_COLORS[exp.status] || '#4A5B6E'}15` }}>
                        {exp.status === 'approved' && <CheckCircle2 size={9} />}
                        {exp.status === 'rejected' && <XCircle size={9} />}
                        {exp.status === 'pending' && <Clock size={9} />}
                        {exp.status || 'pending'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-[10px] text-[#4A5B6E]">
                      {exp.submitted_date ? new Date(exp.submitted_date).toLocaleDateString() : exp.created_at ? new Date(exp.created_at).toLocaleDateString() : '-'}
                    </td>
                    <td className="px-4 py-2.5">
                      {exp.status === 'pending' && (
                        <div className="flex items-center gap-1">
                          <button onClick={() => updateStatus(exp.id, 'approve')} data-testid={`approve-${exp.id}`}
                            className="p-1 rounded text-[#22c55e] hover:bg-[#22c55e]/10 transition-colors" title="Approve">
                            <CheckCircle2 size={14} />
                          </button>
                          <button onClick={() => updateStatus(exp.id, 'reject')} data-testid={`reject-${exp.id}`}
                            className="p-1 rounded text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors" title="Reject">
                            <XCircle size={14} />
                          </button>
                        </div>
                      )}
                      {exp.status === 'approved' && exp.approved_by && (
                        <span className="text-[9px] text-[#4A5B6E]">by {exp.approved_by}</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, icon: Icon, color }) {
  return (
    <div className="bg-[#0A1628] border border-[#1B2D42] rounded-xl p-4 flex items-center gap-3" data-testid={`summary-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${color}10`, border: `1px solid ${color}20` }}>
        <Icon size={16} style={{ color }} />
      </div>
      <div>
        <p className="text-[9px] font-bold uppercase tracking-wider text-[#4A5B6E]">{label}</p>
        <p className="text-sm font-bold" style={{ color }}>{value}</p>
      </div>
    </div>
  );
}
