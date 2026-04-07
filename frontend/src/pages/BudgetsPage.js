import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Wallet, Plus, TrendingDown, TrendingUp, AlertTriangle, Loader2, BarChart3 } from 'lucide-react';

const ALERT_COLORS = { on_track: '#22c55e', warning: '#f59e0b', over_budget: '#ef4444' };

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [variance, setVariance] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: '', type: 'department', department: '', fiscal_year: '2025-26', line_items: [{ category: '', amount: 0 }] });

  const load = useCallback(async () => {
    try {
      const [b, v, a] = await Promise.all([
        fetch(`${API}/budgets`).then(r => r.json()),
        fetch(`${API}/budgets/variance`).then(r => r.json()),
        fetch(`${API}/budgets/alerts`).then(r => r.json()),
      ]);
      setBudgets(Array.isArray(b) ? b : []);
      setVariance(Array.isArray(v) ? v : []);
      setAlerts(Array.isArray(a) ? a : []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createBudget = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await fetch(`${API}/budgets`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      setShowForm(false);
      setForm({ name: '', type: 'department', department: '', fiscal_year: '2025-26', line_items: [{ category: '', amount: 0 }] });
      load();
    } catch {}
    setSubmitting(false);
  };

  const addLineItem = () => setForm(p => ({ ...p, line_items: [...p.line_items, { category: '', amount: 0 }] }));
  const updateLineItem = (i, field, value) => {
    const items = [...form.line_items];
    items[i][field] = field === 'amount' ? Number(value) : value;
    setForm(p => ({ ...p, line_items: items }));
  };

  const totalBudget = variance.reduce((s, v) => s + v.total_budget, 0);
  const totalActual = variance.reduce((s, v) => s + v.total_actual, 0);

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading budgets...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="budgets-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="budgets-title">Budget Management</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Department & project budgets with variance tracking</p>
        </div>
        <button onClick={() => setShowForm(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-budget-btn"><Plus size={16} /> New Budget</button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Budget', value: `${(totalBudget / 100000).toFixed(1)}L`, icon: Wallet, color: '#38bdf8' },
          { label: 'Total Spent', value: `${(totalActual / 100000).toFixed(1)}L`, icon: TrendingDown, color: '#f59e0b' },
          { label: 'Remaining', value: `${((totalBudget - totalActual) / 100000).toFixed(1)}L`, icon: TrendingUp, color: '#22c55e' },
          { label: 'Alerts', value: alerts.length, icon: AlertTriangle, color: '#ef4444' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`budget-stat-${c.label.toLowerCase().replace(' ', '-')}`}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-bold text-[#E8EDF2] flex items-center gap-2"><AlertTriangle size={14} className="text-[#ef4444]" /> Budget Alerts</h2>
          {alerts.map((a, i) => (
            <div key={i} className="bg-[#0A1628] border rounded-lg p-3 flex items-center justify-between" style={{ borderColor: a.severity === 'critical' ? '#ef444440' : '#f59e0b40' }}>
              <div>
                <p className="text-sm font-semibold text-[#E8EDF2]">{a.name}</p>
                <p className="text-xs text-[#4A5B6E]">{a.message}</p>
              </div>
              <span className="text-sm font-bold" style={{ color: a.severity === 'critical' ? '#ef4444' : '#f59e0b' }}>{a.usage_pct}%</span>
            </div>
          ))}
        </div>
      )}

      {/* Variance Table */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="p-4 border-b border-[#1B2D42] flex items-center gap-2"><BarChart3 size={16} className="text-[#00C9A7]" /><h2 className="text-sm font-bold text-[#E8EDF2]">Budget Variance</h2></div>
        {variance.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No budgets configured</p> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
                <th className="text-left p-3">Budget</th><th className="text-left p-3">Type</th><th className="text-right p-3">Budget</th><th className="text-right p-3">Actual</th><th className="text-right p-3">Variance</th><th className="text-center p-3">Status</th>
              </tr></thead>
              <tbody>
                {variance.map(v => (
                  <tr key={v.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`variance-${v.id}`}>
                    <td className="p-3 text-[#E8EDF2] font-medium">{v.name}</td>
                    <td className="p-3 text-[#7A8BA0] capitalize">{v.type}</td>
                    <td className="p-3 text-right text-[#E8EDF2]">{v.total_budget.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })}</td>
                    <td className="p-3 text-right text-[#E8EDF2]">{v.total_actual.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })}</td>
                    <td className="p-3 text-right font-bold" style={{ color: ALERT_COLORS[v.alert] }}>{v.variance >= 0 ? '+' : ''}{v.variance.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })} ({v.variance_pct}%)</td>
                    <td className="p-3 text-center"><span className="px-2 py-0.5 rounded-full text-xs font-bold capitalize" style={{ color: ALERT_COLORS[v.alert], background: ALERT_COLORS[v.alert] + '15' }}>{v.alert?.replace('_', ' ')}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Budget Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={createBudget} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-lg space-y-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-[#E8EDF2]">New Budget</h2>
            <input placeholder="Budget Name" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="budget-name" />
            <div className="grid grid-cols-3 gap-3">
              <select value={form.type} onChange={e => setForm(p => ({ ...p, type: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none">
                <option value="department">Department</option><option value="project">Project</option>
              </select>
              <input placeholder="Department" value={form.department} onChange={e => setForm(p => ({ ...p, department: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" />
              <input placeholder="FY 2025-26" value={form.fiscal_year} onChange={e => setForm(p => ({ ...p, fiscal_year: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2"><span className="text-xs text-[#4A5B6E] uppercase tracking-wider">Line Items</span><button type="button" onClick={addLineItem} className="text-xs text-[#00C9A7] hover:underline">+ Add</button></div>
              {form.line_items.map((li, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input placeholder="Category" value={li.category} onChange={e => updateLineItem(i, 'category', e.target.value)} className="flex-1 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                  <input type="number" placeholder="Amount" value={li.amount || ''} onChange={e => updateLineItem(i, 'amount', e.target.value)} className="w-32 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                </div>
              ))}
              <p className="text-xs text-[#4A5B6E] text-right">Total: {form.line_items.reduce((s, li) => s + (li.amount || 0), 0).toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</p>
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="create-budget-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Create</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
