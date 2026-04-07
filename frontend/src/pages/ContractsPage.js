import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { FileText, AlertTriangle, CheckCircle2, Clock, DollarSign, Sparkles } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

const STATUS_COLORS = { active: '#22c55e', expired: '#ef4444', terminated: '#6b7280', draft: '#f59e0b' };

export default function ContractsPage() {
  const [contracts, setContracts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAiModal, setShowAiModal] = useState(false);
  const [expanded, setExpanded] = useState(null);

  const load = useCallback(async () => {
    try {
      const [c, a, s] = await Promise.all([
        fetch(`${API}/contracts`).then(r => r.json()),
        fetch(`${API}/contracts/alerts/renewals`).then(r => r.json()),
        fetch(`${API}/contracts/stats/summary`).then(r => r.json()),
      ]);
      setContracts(Array.isArray(c) ? c : []);
      setAlerts(Array.isArray(a) ? a : []);
      setStats(s || {});
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createContract = async (data) => {
    const res = await fetch(`${API}/contracts`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to create contract');
    load();
  };

  const completeMilestone = async (contractId, msId) => {
    await fetch(`${API}/contracts/${contractId}/milestones/${msId}/complete`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ completed_by: 'admin' }) });
    load();
  };

  const totalValue = Object.values(stats).reduce((s, v) => s + (v.total_value || 0), 0);
  const activeCount = stats.active?.count || 0;

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading contracts...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="contracts-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="contracts-title">Contract Management</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">SOW/MSA tracking, milestones & renewal alerts</p>
        </div>
        <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-contract-btn"><Sparkles size={16} /> New Contract</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Active', value: activeCount, icon: CheckCircle2, color: '#22c55e' },
          { label: 'Total Value', value: `${(totalValue / 100000).toFixed(1)}L`, icon: DollarSign, color: '#38bdf8' },
          { label: 'Expiring Soon', value: alerts.length, icon: AlertTriangle, color: '#f59e0b' },
          { label: 'Total Contracts', value: contracts.length, icon: FileText, color: '#a78bfa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`contract-stat-${c.label.toLowerCase().replace(' ', '-')}`}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Renewal Alerts */}
      {alerts.length > 0 && (
        <div className="bg-[#0A1628] border border-[#f59e0b]/30 rounded-lg p-4">
          <h2 className="text-sm font-bold text-[#f59e0b] flex items-center gap-2 mb-3"><AlertTriangle size={14} /> Renewal Alerts</h2>
          <div className="space-y-2">
            {alerts.slice(0, 5).map(a => (
              <div key={a.contract_id} className="flex items-center justify-between text-sm">
                <span className="text-[#E8EDF2]">{a.title} <span className="text-[#4A5B6E]">({a.client_name})</span></span>
                <span className={`font-bold ${a.severity === 'critical' ? 'text-[#ef4444]' : 'text-[#f59e0b]'}`}>{a.days_remaining}d left</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Contracts List */}
      <div className="space-y-3">
        {contracts.length === 0 && <p className="text-[#4A5B6E] text-center py-8">No contracts yet</p>}
        {contracts.map(c => (
          <div key={c.id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg" data-testid={`contract-${c.id}`}>
            <div className="p-4 cursor-pointer" onClick={() => setExpanded(expanded === c.id ? null : c.id)}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-[#E8EDF2]">{c.title}</span>
                    <span className="px-2 py-0.5 rounded-full text-xs font-bold uppercase" style={{ color: STATUS_COLORS[c.status] || '#7A8BA0', background: (STATUS_COLORS[c.status] || '#7A8BA0') + '15' }}>{c.status}</span>
                    <span className="px-2 py-0.5 rounded-full text-xs bg-[#152236] text-[#7A8BA0] uppercase">{c.type}</span>
                  </div>
                  <p className="text-xs text-[#4A5B6E] mt-1">{c.client_name} | {c.contract_number} | {c.billing_type}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-[#E8EDF2]">{c.value?.toLocaleString('en-IN', { style: 'currency', currency: c.currency || 'INR' })}</p>
                  <p className="text-xs text-[#4A5B6E]">{c.start_date} to {c.end_date}</p>
                </div>
              </div>
            </div>
            {expanded === c.id && c.milestones?.length > 0 && (
              <div className="px-4 pb-4 border-t border-[#1B2D42] pt-3">
                <p className="text-xs text-[#4A5B6E] uppercase tracking-wider mb-2">Milestones</p>
                <div className="space-y-2">
                  {c.milestones.map(m => (
                    <div key={m.id} className="flex items-center justify-between bg-[#152236] rounded p-2">
                      <div className="flex items-center gap-2">
                        {m.status === 'completed' ? <CheckCircle2 size={14} className="text-[#22c55e]" /> : <Clock size={14} className="text-[#f59e0b]" />}
                        <span className="text-sm text-[#E8EDF2]">{m.name}</span>
                        <span className="text-xs text-[#4A5B6E]">{m.amount?.toLocaleString('en-IN', { style: 'currency', currency: c.currency || 'INR' })}</span>
                      </div>
                      {m.status === 'pending' && <button onClick={(e) => { e.stopPropagation(); completeMilestone(c.id, m.id); }} className="text-xs text-[#00C9A7] hover:underline" data-testid={`complete-ms-${m.id}`}>Complete</button>}
                      {m.invoiced && <span className="text-xs text-[#22c55e]">Invoiced</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <AiEntryModal open={showAiModal} onClose={() => setShowAiModal(false)} module="contract" title="New Contract" placeholder='e.g. "SOW for CloudMigrate with TechCorp, $200K fixed-price, Apr-Dec 2026, 3 milestones"' onSubmit={createContract} />
    </div>
  );
}
