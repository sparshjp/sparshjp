import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Users, BarChart3, UserCheck, UserMinus, Briefcase, Sparkles } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

export default function ResourcesPage() {
  const [tab, setTab] = useState('allocations');
  const [allocations, setAllocations] = useState([]);
  const [bench, setBench] = useState([]);
  const [utilization, setUtilization] = useState({});
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAiModal, setShowAiModal] = useState(false);

  const load = useCallback(async () => {
    try {
      const [al, bn, ut, fc] = await Promise.all([
        fetch(`${API}/resources/allocations`).then(r => r.json()),
        fetch(`${API}/resources/bench`).then(r => r.json()),
        fetch(`${API}/resources/utilization`).then(r => r.json()),
        fetch(`${API}/resources/forecast`).then(r => r.json()),
      ]);
      setAllocations(Array.isArray(al) ? al : []);
      setBench(Array.isArray(bn) ? bn : []);
      setUtilization(ut || {});
      setForecast(Array.isArray(fc) ? fc : []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createAllocation = async (data) => {
    const res = await fetch(`${API}/resources/allocations`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to create allocation');
    load();
  };

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading resources...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="resources-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="resources-title">Resource Planning</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Allocations, bench management & utilization</p>
        </div>
        <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-allocation-btn"><Sparkles size={16} /> Allocate</button>
      </div>

      {/* Utilization Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: 'Total Employees', value: utilization.total_employees || 0, icon: Users, color: '#38bdf8' },
          { label: 'Allocated', value: utilization.allocated || 0, icon: UserCheck, color: '#22c55e' },
          { label: 'On Bench', value: utilization.on_bench || 0, icon: UserMinus, color: '#f59e0b' },
          { label: 'Avg Utilization', value: `${utilization.avg_utilization || 0}%`, icon: BarChart3, color: '#a78bfa' },
          { label: 'Billable Ratio', value: `${utilization.billable_ratio || 0}%`, icon: Briefcase, color: '#00d4aa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`resource-stat-${c.label.toLowerCase().replace(' ', '-')}`}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-lg font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit">
        {['allocations', 'bench', 'forecast'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`tab-${t}`}>{t}</button>
        ))}
      </div>

      {tab === 'allocations' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          {allocations.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No allocations yet</p> : (
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
                <th className="text-left p-3">Employee</th><th className="text-left p-3">Project</th><th className="text-left p-3">Role</th><th className="text-center p-3">Allocation</th><th className="text-center p-3">Billable</th><th className="text-right p-3">Rate</th>
              </tr></thead>
              <tbody>
                {allocations.map(a => (
                  <tr key={a.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`alloc-${a.id}`}>
                    <td className="p-3 text-[#E8EDF2] font-medium">{a.employee_name}</td>
                    <td className="p-3 text-[#7A8BA0]">{a.project_name}</td>
                    <td className="p-3 text-[#7A8BA0]">{a.role}</td>
                    <td className="p-3 text-center"><span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#00C9A7]/15 text-[#00C9A7]">{a.allocation_pct}%</span></td>
                    <td className="p-3 text-center">{a.billable ? <span className="text-[#22c55e] text-xs">Yes</span> : <span className="text-[#4A5B6E] text-xs">No</span>}</td>
                    <td className="p-3 text-right text-[#E8EDF2]">{a.bill_rate ? `${a.bill_rate}/hr` : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'bench' && (
        <div className="space-y-3">
          {bench.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No bench resources</p> : bench.map(b => (
            <div key={b.employee_id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`bench-${b.employee_id}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-bold text-[#E8EDF2]">{b.name}</p>
                  <p className="text-xs text-[#4A5B6E]">{b.department} | {b.designation}</p>
                  {b.skills?.length > 0 && <div className="flex gap-1 mt-1 flex-wrap">{b.skills.map((s, i) => <span key={i} className="px-1.5 py-0.5 rounded bg-[#152236] text-[#7A8BA0] text-xs">{s}</span>)}</div>}
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-[#00C9A7]">{b.available_pct}%</p>
                  <p className="text-xs text-[#4A5B6E]">available</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'forecast' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          {forecast.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No staffing forecast data</p> : (
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
                <th className="text-left p-3">Project</th><th className="text-center p-3">Status</th><th className="text-center p-3">Team Size</th><th className="text-center p-3">Total FTE</th><th className="text-center p-3">Billable FTE</th><th className="text-left p-3">End Date</th>
              </tr></thead>
              <tbody>
                {forecast.map(f => (
                  <tr key={f.project_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50">
                    <td className="p-3 text-[#E8EDF2] font-medium">{f.project_name}</td>
                    <td className="p-3 text-center"><span className="px-2 py-0.5 rounded-full text-xs capitalize bg-[#152236] text-[#7A8BA0]">{f.status}</span></td>
                    <td className="p-3 text-center text-[#E8EDF2]">{f.team_size}</td>
                    <td className="p-3 text-center text-[#E8EDF2]">{f.total_fte}</td>
                    <td className="p-3 text-center text-[#00C9A7]">{f.billable_fte}</td>
                    <td className="p-3 text-[#4A5B6E]">{f.end_date || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <AiEntryModal open={showAiModal} onClose={() => setShowAiModal(false)} module="resource_allocation" title="New Resource Allocation" placeholder='e.g. "Allocate Priya 100% to CloudMigrate as Tech Lead, billable at 3000/hr, Apr-Sep 2026"' onSubmit={createAllocation} />
    </div>
  );
}
