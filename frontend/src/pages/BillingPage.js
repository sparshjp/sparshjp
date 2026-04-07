import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Receipt, Plus, Clock, CheckCircle2, Loader2, FileText, Milestone } from 'lucide-react';

export default function BillingPage() {
  const [tab, setTab] = useState('unbilled');
  const [unbilled, setUnbilled] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(null);

  const load = useCallback(async () => {
    try {
      const [ub, ms, st] = await Promise.all([
        fetch(`${API}/billing/unbilled`).then(r => r.json()),
        fetch(`${API}/billing/milestone-invoices`).then(r => r.json()),
        fetch(`${API}/billing/stats`).then(r => r.json()),
      ]);
      setUnbilled(Array.isArray(ub) ? ub : []);
      setMilestones(Array.isArray(ms) ? ms : []);
      setStats(st || {});
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const generateInvoice = async (project) => {
    setGenerating(project.project_id);
    try {
      await fetch(`${API}/billing/generate-invoice`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: project.project_id, entries: project.entries, billing_type: project.billing_type, period: `${new Date().toISOString().slice(0, 7)}` }),
      });
      load();
    } catch {}
    setGenerating(null);
  };

  const generateMilestoneInvoice = async (m) => {
    setGenerating(m.milestone_id);
    try {
      await fetch(`${API}/billing/milestone-invoice`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_id: m.contract_id, milestone_id: m.milestone_id }),
      });
      load();
    } catch {}
    setGenerating(null);
  };

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading billing...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="billing-page">
      <div>
        <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="billing-title">Billing Automation</h1>
        <p className="text-[#4A5B6E] text-sm mt-1">Auto-generate invoices from timesheets & milestones</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Unbilled Timesheets', value: stats.unbilled_timesheets || 0, icon: Clock, color: '#f59e0b' },
          { label: 'Invoiced Timesheets', value: stats.invoiced_timesheets || 0, icon: CheckCircle2, color: '#22c55e' },
          { label: 'Draft Invoices', value: stats.draft_invoices || 0, icon: FileText, color: '#38bdf8' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit">
        {['unbilled', 'milestones'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`tab-${t}`}>{t === 'unbilled' ? 'Unbilled T&M' : 'Milestone Billing'}</button>
        ))}
      </div>

      {tab === 'unbilled' && (
        <div className="space-y-4">
          {unbilled.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No unbilled timesheet entries</p> : unbilled.map(p => (
            <div key={p.project_id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`unbilled-${p.project_id}`}>
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm font-bold text-[#E8EDF2]">{p.project_name}</p>
                  <p className="text-xs text-[#4A5B6E]">{p.client} | {p.billing_type} | {p.total_hours} hrs</p>
                </div>
                <div className="flex items-center gap-3">
                  <p className="text-lg font-bold text-[#00C9A7]">{p.total_amount?.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</p>
                  <button onClick={() => generateInvoice(p)} disabled={generating === p.project_id} className="px-3 py-1.5 bg-[#00C9A7] text-[#0A1628] rounded text-xs font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid={`generate-inv-${p.project_id}`}>
                    {generating === p.project_id ? <Loader2 size={12} className="animate-spin" /> : <Receipt size={12} />} Generate Invoice
                  </button>
                </div>
              </div>
              {p.entries?.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead><tr className="text-[#4A5B6E] border-b border-[#1B2D42]">
                      <th className="text-left p-2">Employee</th><th className="text-left p-2">Task</th><th className="text-right p-2">Hours</th><th className="text-right p-2">Rate</th><th className="text-right p-2">Amount</th>
                    </tr></thead>
                    <tbody>
                      {p.entries.slice(0, 10).map((e, i) => (
                        <tr key={i} className="border-b border-[#1B2D42]/30">
                          <td className="p-2 text-[#E8EDF2]">{e.employee}</td>
                          <td className="p-2 text-[#7A8BA0]">{e.task || e.description || '-'}</td>
                          <td className="p-2 text-right text-[#E8EDF2]">{e.hours}</td>
                          <td className="p-2 text-right text-[#7A8BA0]">{e.rate}</td>
                          <td className="p-2 text-right text-[#00C9A7]">{e.amount?.toLocaleString('en-IN')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === 'milestones' && (
        <div className="space-y-3">
          {milestones.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No invoiceable milestones</p> : milestones.map(m => (
            <div key={m.milestone_id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4 flex items-center justify-between" data-testid={`milestone-${m.milestone_id}`}>
              <div>
                <p className="text-sm font-bold text-[#E8EDF2]">{m.milestone_name}</p>
                <p className="text-xs text-[#4A5B6E]">{m.contract_title} | {m.client_name}</p>
                <p className="text-xs text-[#4A5B6E]">Completed: {m.completed_at?.slice(0, 10)}</p>
              </div>
              <div className="flex items-center gap-3">
                <p className="text-lg font-bold text-[#00C9A7]">{m.amount?.toLocaleString('en-IN', { style: 'currency', currency: m.currency || 'INR' })}</p>
                <button onClick={() => generateMilestoneInvoice(m)} disabled={generating === m.milestone_id} className="px-3 py-1.5 bg-[#00C9A7] text-[#0A1628] rounded text-xs font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid={`gen-ms-inv-${m.milestone_id}`}>
                  {generating === m.milestone_id ? <Loader2 size={12} className="animate-spin" /> : <Receipt size={12} />} Invoice
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
