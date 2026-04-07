import { useState, useEffect, useMemo, useCallback } from 'react';
import { API } from '../App';
import { FolderKanban, Users, Clock, TrendingUp, CheckCircle, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

const HEALTH_COLORS = { GREEN: '#22c55e', YELLOW: '#eab308', RED: '#ef4444', CLOSED: '#6b7280' };
const TYPE_COLORS = { 'Fixed-Price': '#4ade80', 'T&M': '#38bdf8', 'T&M Export': '#fbbf24', 'Fixed-Price Export': '#f59e0b', 'Fixed-Price Milestone': '#a78bfa', 'Monthly Retainer': '#c084fc', 'Non-billable': '#6b7280' };

export default function ProjectsModule() {
  const [projects, setProjects] = useState([]);
  const [healthData, setHealthData] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectTimesheets, setProjectTimesheets] = useState([]);
  const [projectTxns, setProjectTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAiModal, setShowAiModal] = useState(false);

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

  const handleCreateProject = async (data) => {
    const payload = { ...data };
    if (typeof payload.team_names === 'string') payload.team_names = payload.team_names.split(',').map(s => s.trim()).filter(Boolean);
    const res = await fetch(`${API}/projects`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) throw new Error('Failed to create project');
    loadData();
  };

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
        <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1.5 transition-all" data-testid="new-project-btn"><Sparkles size={16} /> New Project</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Active Projects', value: activeProjects.length - closedCount, icon: FolderKanban, color: '#38bdf8' },
          { label: 'Closed', value: closedCount, icon: CheckCircle, color: '#22c55e' },
          { label: 'Portfolio Value', value: `${(totalValue / 100000).toFixed(1)}L`, icon: TrendingUp, color: '#a78bfa' },
          { label: 'Billable Hours', value: totalHours.toLocaleString(), icon: Clock, color: '#00d4aa' },
        ].map((c) => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2"><c.icon size={16} style={{ color: c.color }} /><span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E]">{c.label}</span></div>
            <p className="text-xl font-black text-[#E8EDF2]">{c.value}</p>
          </div>
        ))}
      </div>

      {/* Health Dashboard */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Project Health Dashboard</h2></div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
              {['Project', 'Client', 'Type', 'Health', 'Progress', 'Billable Hrs', 'Team', 'PM', ''].map(h => (
                <th key={h || 'x'} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
              ))}
            </tr></thead>
            <tbody>
              {healthData.map(h => (
                <tr key={h.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50 cursor-pointer" onClick={() => loadProjectDetail(h.id)} data-testid={`project-row-${h.id}`}>
                  <td className="px-3 py-2.5"><span className="font-bold text-[#E8EDF2]">{h.id}</span><span className="text-[#4A5B6E] ml-1.5">{h.name}</span></td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{h.client}</td>
                  <td className="px-3 py-2.5"><span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${TYPE_COLORS[h.type] || '#6b7280'}18`, color: TYPE_COLORS[h.type] || '#6b7280' }}>{h.type}</span></td>
                  <td className="px-3 py-2.5"><span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${HEALTH_COLORS[h.health] || '#6b7280'}18`, color: HEALTH_COLORS[h.health] || '#6b7280' }}><span className="w-1.5 h-1.5 rounded-full" style={{ background: HEALTH_COLORS[h.health] || '#6b7280' }} />{h.health}</span></td>
                  <td className="px-3 py-2.5">{h.pct_complete != null ? <div className="flex items-center gap-2"><div className="w-16 h-1.5 bg-[#1B2D42] rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width: `${h.pct_complete}%`, background: HEALTH_COLORS[h.health] || '#38bdf8' }} /></div><span className="text-[#E8EDF2] font-bold">{h.pct_complete}%</span></div> : <span className="text-[#4A5B6E]">{h.status}</span>}</td>
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

      {/* Expanded Detail */}
      {selectedProject && (() => {
        const proj = projects.find(p => p.id === selectedProject);
        return (
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4 space-y-4" data-testid="project-detail">
            <h3 className="text-sm font-bold text-[#00d4aa]">{selectedProject} — Detail View</h3>
            {proj?.milestones?.length > 0 && (<div><h4 className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E] mb-2">Milestones</h4><div className="grid grid-cols-2 lg:grid-cols-4 gap-3">{proj.milestones.map(m => (<div key={m.id} className={`p-3 rounded-lg border ${m.status === 'Completed' ? 'border-[#22c55e]/30 bg-[#22c55e]/5' : 'border-[#1B2D42] bg-[#152236]'}`}><div className="flex items-center gap-2 mb-1"><span className="text-[10px] font-bold text-[#E8EDF2]">{m.id}</span><span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${m.status === 'Completed' ? 'bg-[#22c55e]/10 text-[#22c55e]' : 'bg-[#1B2D42] text-[#4A5B6E]'}`}>{m.status}</span></div><p className="text-[10px] text-[#4A5B6E]">{m.name}</p><p className="text-xs font-bold text-[#E8EDF2] mt-1">{m.currency === 'USD' ? `$${m.value?.toLocaleString()}` : `${m.value?.toLocaleString()}`}</p></div>))}</div></div>)}
            {projectTimesheets.length > 0 && (<div><h4 className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E] mb-2">Timesheet Hours</h4><div className="grid grid-cols-2 lg:grid-cols-4 gap-2">{projectTimesheets.slice(0,8).map(ts => (<div key={ts.employee_id+ts.week} className="bg-[#152236] rounded p-2 text-[10px]"><span className="font-bold text-[#E8EDF2]">{ts.employee_name}</span> <span className="text-[#4A5B6E]">{ts.week}</span><div className="mt-1 text-[#00d4aa] font-bold">{ts.billable_hours}h</div></div>))}</div></div>)}
          </div>
        );
      })()}

      {/* Project Cards */}
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
                <p className="text-[10px] text-[#4A5B6E]">Client: <span className="text-[#E8EDF2]">{p.client}</span> | PM: <span className="text-[#E8EDF2]">{p.pm}</span></p>
                {p.team_names?.length > 0 && <p className="text-[10px] text-[#4A5B6E] mt-0.5">Team: {p.team_names.join(', ')}</p>}
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-[#E8EDF2]">{p.value_inr ? `${(p.value_inr / 100000).toFixed(1)}L` : p.value_usd ? `$${p.value_usd?.toLocaleString()}` : '--'}</p>
                <p className="text-[10px] text-[#4A5B6E]">{p.billing} | {p.duration || 'Ongoing'}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <AiEntryModal
        open={showAiModal}
        onClose={() => setShowAiModal(false)}
        module="project"
        title="New Project"
        placeholder='e.g. "Create T&M project for Acme Corp, $120K, 6 months, PM is Priya, team: Raj, Ankit"'
        onSubmit={handleCreateProject}
      />
    </div>
  );
}
