import { useState, useEffect, useMemo, useCallback } from 'react';
import { API } from '../App';
import { FolderKanban, Users, Clock, TrendingUp, AlertCircle, CheckCircle, ChevronDown, ChevronUp, Plus, Loader2, X } from 'lucide-react';

const HEALTH_COLORS = { GREEN: '#22c55e', YELLOW: '#eab308', RED: '#ef4444', CLOSED: '#6b7280' };
const TYPE_COLORS = { 'Fixed-Price': '#4ade80', 'T&M': '#38bdf8', 'T&M Export': '#fbbf24', 'Fixed-Price Export': '#f59e0b', 'Fixed-Price Milestone': '#a78bfa', 'Monthly Retainer': '#c084fc', 'Non-billable': '#6b7280' };
const PROJECT_TYPES = ['Fixed-Price', 'T&M', 'T&M Export', 'Fixed-Price Export', 'Fixed-Price Milestone', 'Monthly Retainer', 'Non-billable'];

export default function ProjectsModule() {
  const [projects, setProjects] = useState([]);
  const [healthData, setHealthData] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectTimesheets, setProjectTimesheets] = useState([]);
  const [projectTxns, setProjectTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: '', client: '', type: 'T&M', pm: '', value_inr: 0, value_usd: 0, currency: 'INR', billing: 'Monthly', duration: '', team_names_str: '', milestones: [] });

  const loadData = useCallback(() => {
    Promise.all([
      fetch(`${API}/projects`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/projects/health/dashboard`).then(r => r.ok ? r.json() : []),
    ]).then(([p, h]) => {
      setProjects(p);
      setHealthData(h);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const loadProjectDetail = async (pid) => {
    if (selectedProject === pid) { setSelectedProject(null); return; }
    setSelectedProject(pid);
    const [ts, txns] = await Promise.all([
      fetch(`${API}/projects/${pid}/timesheets`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/projects/${pid}/transactions`).then(r => r.ok ? r.json() : []),
    ]);
    setProjectTimesheets(ts);
    setProjectTxns(txns);
  };

  const createProject = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        team_names: form.team_names_str.split(',').map(s => s.trim()).filter(Boolean),
      };
      delete payload.team_names_str;
      await fetch(`${API}/projects`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      setShowForm(false);
      setForm({ name: '', client: '', type: 'T&M', pm: '', value_inr: 0, value_usd: 0, currency: 'INR', billing: 'Monthly', duration: '', team_names_str: '', milestones: [] });
      loadData();
    } catch {}
    setSubmitting(false);
  };

  const addMilestone = () => setForm(p => ({ ...p, milestones: [...p.milestones, { name: '', value: 0, currency: p.currency, date: '' }] }));
  const updateMilestone = (i, field, value) => {
    const ms = [...form.milestones];
    ms[i][field] = field === 'value' ? Number(value) : value;
    setForm(p => ({ ...p, milestones: ms }));
  };
  const removeMilestone = (i) => setForm(p => ({ ...p, milestones: p.milestones.filter((_, idx) => idx !== i) }));

  const activeProjects = projects.filter(p => p.id !== 'PRJ-INT');
  const closedCount = activeProjects.filter(p => p.status === 'CLOSED').length;
  const totalValue = activeProjects.reduce((s, p) => s + (p.value_inr || (p.value_usd || 0) * 84.5 || 0), 0);
  const totalHours = healthData.reduce((s, h) => s + h.billable_hours, 0);

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading projects...</div>;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6" data-testid="projects-module">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="projects-title">Project Management</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Active delivery portfolio</p>
        </div>
        <button onClick={() => setShowForm(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-project-btn"><Plus size={16} /> New Project</button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Active Projects', value: activeProjects.length - closedCount, icon: FolderKanban, color: '#38bdf8' },
          { label: 'Closed', value: closedCount, icon: CheckCircle, color: '#22c55e' },
          { label: 'Portfolio Value', value: `${(totalValue / 100000).toFixed(1)}L`, icon: TrendingUp, color: '#a78bfa' },
          { label: 'Billable Hours', value: totalHours.toLocaleString(), icon: Clock, color: '#00d4aa' },
        ].map((c) => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`project-summary-${c.label}`}>
            <div className="flex items-center gap-2 mb-2">
              <c.icon size={16} style={{ color: c.color }} />
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E]">{c.label}</span>
            </div>
            <p className="text-xl font-black text-[#E8EDF2]">{c.value}</p>
          </div>
        ))}
      </div>

      {/* Health Dashboard */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Project Health Dashboard</h2></div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
                {['Project', 'Client', 'Type', 'Health', 'Progress', 'Billable Hrs', 'Team', 'PM', ''].map(h => (
                  <th key={h || 'actions'} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {healthData.map(h => (
                <tr key={h.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50 cursor-pointer transition-colors"
                    onClick={() => loadProjectDetail(h.id)} data-testid={`project-row-${h.id}`}>
                  <td className="px-3 py-2.5"><span className="font-bold text-[#E8EDF2]">{h.id}</span><span className="text-[#4A5B6E] ml-1.5">{h.name}</span></td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{h.client}</td>
                  <td className="px-3 py-2.5"><span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${TYPE_COLORS[h.type] || '#6b7280'}18`, color: TYPE_COLORS[h.type] || '#6b7280' }}>{h.type}</span></td>
                  <td className="px-3 py-2.5"><span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${HEALTH_COLORS[h.health] || '#6b7280'}18`, color: HEALTH_COLORS[h.health] || '#6b7280' }}><span className="w-1.5 h-1.5 rounded-full" style={{ background: HEALTH_COLORS[h.health] || '#6b7280' }} />{h.health}</span></td>
                  <td className="px-3 py-2.5">{h.pct_complete != null ? (<div className="flex items-center gap-2"><div className="w-16 h-1.5 bg-[#1B2D42] rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width: `${h.pct_complete}%`, background: HEALTH_COLORS[h.health] || '#38bdf8' }} /></div><span className="text-[#E8EDF2] font-bold">{h.pct_complete}%</span></div>) : <span className="text-[#4A5B6E]">{h.status}</span>}</td>
                  <td className="px-3 py-2.5 text-[#E8EDF2] font-mono">{h.billable_hours}</td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{h.team_count}</td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{h.pm}</td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{selectedProject === h.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Project Detail Expanded */}
      {selectedProject && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4 space-y-4" data-testid="project-detail">
          <h3 className="text-sm font-bold text-[#00d4aa]">{selectedProject} — Detail View</h3>
          {(() => {
            const proj = projects.find(p => p.id === selectedProject);
            if (!proj?.milestones?.length) return null;
            return (
              <div>
                <h4 className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E] mb-2">Milestones</h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  {proj.milestones.map(m => (
                    <div key={m.id} className={`p-3 rounded-lg border ${m.status === 'Completed' ? 'border-[#22c55e]/30 bg-[#22c55e]/5' : 'border-[#1B2D42] bg-[#152236]'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold text-[#E8EDF2]">{m.id}</span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${m.status === 'Completed' ? 'bg-[#22c55e]/10 text-[#22c55e]' : m.status === 'In Progress' ? 'bg-[#eab308]/10 text-[#eab308]' : 'bg-[#1B2D42] text-[#4A5B6E]'}`}>{m.status}</span>
                      </div>
                      <p className="text-[10px] text-[#4A5B6E]">{m.name}</p>
                      <p className="text-xs font-bold text-[#E8EDF2] mt-1">{m.currency === 'USD' ? `USD ${m.value?.toLocaleString()}` : `${m.value?.toLocaleString()}`}</p>
                      {m.date && <p className="text-[9px] text-[#4A5B6E] mt-0.5">{m.date}</p>}
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}
          {projectTimesheets.length > 0 && (
            <div>
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E] mb-2">Timesheet Hours ({projectTimesheets.length} entries)</h4>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
                {projectTimesheets.slice(0, 8).map(ts => (
                  <div key={ts.employee_id + ts.week} className="bg-[#152236] rounded p-2 text-[10px]">
                    <span className="font-bold text-[#E8EDF2]">{ts.employee_name}</span>
                    <span className="text-[#4A5B6E] ml-1">{ts.week}</span>
                    <div className="mt-1 text-[#00d4aa] font-bold">{ts.billable_hours}h billable</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {projectTxns.length > 0 && (
            <div>
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E] mb-2">Related Transactions ({projectTxns.length})</h4>
              <div className="space-y-1 max-h-60 overflow-y-auto">
                {projectTxns.slice(0, 10).map(t => (
                  <div key={t.id} className="bg-[#152236] rounded p-2 text-[10px]">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[#38bdf8]">{t.id}</span>
                      <span className="text-[#4A5B6E]">{t.date}</span>
                      <span className="font-bold text-[#E8EDF2]">{t.type}</span>
                    </div>
                    <p className="text-[#4A5B6E] mt-1 line-clamp-2">{t.prompt?.slice(0, 150)}...</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* All Projects Detail Cards */}
      <div className="space-y-3">
        {activeProjects.map(p => (
          <div key={p.id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`project-card-${p.id}`}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-[#38bdf8]">{p.id}</span>
                  <span className="text-sm font-bold text-[#E8EDF2]">{p.name}</span>
                  <span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${TYPE_COLORS[p.type] || '#6b7280'}18`, color: TYPE_COLORS[p.type] || '#6b7280' }}>{p.type}</span>
                </div>
                <p className="text-[10px] text-[#4A5B6E]">
                  Client: <span className="text-[#E8EDF2]">{p.client}</span> | PM: <span className="text-[#E8EDF2]">{p.pm}</span> | {p.currency}
                </p>
                {p.team_names?.length > 0 && <p className="text-[10px] text-[#4A5B6E] mt-0.5">Team: {p.team_names.join(', ')}</p>}
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-[#E8EDF2]">
                  {p.value_inr ? `${(p.value_inr / 100000).toFixed(1)}L` : p.value_usd ? `USD ${p.value_usd?.toLocaleString()}` : p.rate || '--'}
                </p>
                <p className="text-[10px] text-[#4A5B6E]">{p.billing}</p>
                <p className="text-[10px] text-[#4A5B6E]">{p.duration || 'Ongoing'}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Project Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={createProject} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-lg space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-[#E8EDF2]">New Project</h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={18} /></button>
            </div>
            <input placeholder="Project Name" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7]" required data-testid="project-name-input" />
            <input placeholder="Client Name" value={form.client} onChange={e => setForm(p => ({ ...p, client: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="project-client-input" />
            <div className="grid grid-cols-2 gap-3">
              <select value={form.type} onChange={e => setForm(p => ({ ...p, type: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="project-type-select">
                {PROJECT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <input placeholder="Project Manager" value={form.pm} onChange={e => setForm(p => ({ ...p, pm: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="project-pm-input" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <select value={form.currency} onChange={e => setForm(p => ({ ...p, currency: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none">
                <option value="INR">INR</option><option value="USD">USD</option><option value="GBP">GBP</option><option value="EUR">EUR</option>
              </select>
              {form.currency === 'INR' ? (
                <input type="number" placeholder="Value (INR)" value={form.value_inr || ''} onChange={e => setForm(p => ({ ...p, value_inr: Number(e.target.value) }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="project-value-input" />
              ) : (
                <input type="number" placeholder={`Value (${form.currency})`} value={form.value_usd || ''} onChange={e => setForm(p => ({ ...p, value_usd: Number(e.target.value) }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="project-value-input" />
              )}
              <select value={form.billing} onChange={e => setForm(p => ({ ...p, billing: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none">
                <option value="Monthly">Monthly</option><option value="Milestone">Milestone</option><option value="Quarterly">Quarterly</option>
              </select>
            </div>
            <input placeholder="Duration (e.g. Mar-Sep 2026)" value={form.duration} onChange={e => setForm(p => ({ ...p, duration: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" />
            <input placeholder="Team Members (comma-separated)" value={form.team_names_str} onChange={e => setForm(p => ({ ...p, team_names_str: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="project-team-input" />

            {/* Milestones */}
            <div>
              <div className="flex items-center justify-between mb-2"><span className="text-xs text-[#4A5B6E] uppercase tracking-wider">Milestones</span><button type="button" onClick={addMilestone} className="text-xs text-[#00C9A7] hover:underline">+ Add</button></div>
              {form.milestones.map((ms, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input placeholder="Milestone Name" value={ms.name} onChange={e => updateMilestone(i, 'name', e.target.value)} className="flex-1 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                  <input type="number" placeholder="Value" value={ms.value || ''} onChange={e => updateMilestone(i, 'value', e.target.value)} className="w-24 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                  <input type="date" value={ms.date} onChange={e => updateMilestone(i, 'date', e.target.value)} className="px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                  <button type="button" onClick={() => removeMilestone(i)} className="text-[#ef4444] text-xs px-2">X</button>
                </div>
              ))}
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="create-project-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Create Project</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
