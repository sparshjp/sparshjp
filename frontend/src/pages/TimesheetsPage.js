import React, { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Clock, Users, TrendingUp, CheckCircle, ChevronDown, ChevronUp, Sparkles, Check, XCircle } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

const STATUS_COLORS = { 'On Track': '#22c55e', 'At Risk': '#eab308', 'Below Target': '#ef4444' };

export default function TimesheetsPage() {
  const [timesheets, setTimesheets] = useState([]);
  const [utilization, setUtilization] = useState(null);
  const [consolidation, setConsolidation] = useState([]);
  const [tab, setTab] = useState('utilization');
  const [loading, setLoading] = useState(true);
  const [expandedEmployee, setExpandedEmployee] = useState(null);
  const [showAiModal, setShowAiModal] = useState(false);

  const loadData = useCallback(() => {
    Promise.all([
      fetch(`${API}/timesheets`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/timesheets/utilization`).then(r => r.ok ? r.json() : null),
      fetch(`${API}/timesheets/consolidation`).then(r => r.ok ? r.json() : []),
    ]).then(([ts, util, cons]) => {
      setTimesheets(ts);
      setUtilization(util);
      setConsolidation(cons);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreateTimesheet = async (data) => {
    const totalHours = (data.entries || []).reduce((s, en) => s + (en.hours || 0), 0) + (data.leave_hours || 0);
    const res = await fetch(`${API}/timesheets`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, total_hours: totalHours }),
    });
    if (!res.ok) throw new Error('Failed to create timesheet');
    loadData();
  };

  const approveTs = async (id) => { await fetch(`${API}/timesheets/${id}/approve`, { method: 'PUT' }); loadData(); };
  const rejectTs = async (id) => { await fetch(`${API}/timesheets/${id}/reject`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) }); loadData(); };

  const summary = utilization?.summary || {};

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading timesheets...</div>;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6" data-testid="timesheets-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="timesheets-title">Timesheets & Utilization</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Resource tracking & billing</p>
        </div>
        <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1.5" data-testid="new-timesheet-btn"><Sparkles size={16} /> New Timesheet</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Avg Utilization', value: `${summary.avg_utilization || 0}%`, icon: TrendingUp, color: summary.avg_utilization >= 75 ? '#22c55e' : '#eab308' },
          { label: 'Total Billable', value: `${summary.total_billable || 0}h`, icon: Clock, color: '#38bdf8' },
          { label: 'Headcount', value: summary.headcount || 0, icon: Users, color: '#a78bfa' },
          { label: 'Timesheets', value: timesheets.length, icon: CheckCircle, color: '#00d4aa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2"><c.icon size={16} style={{ color: c.color }} /><span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E]">{c.label}</span></div>
            <p className="text-xl font-black text-[#E8EDF2]">{c.value}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-1 border-b border-[#1B2D42]">
        {[{ id: 'utilization', label: 'Utilization Report' }, { id: 'consolidation', label: 'Project Hours' }, { id: 'entries', label: 'Timesheet Entries' }].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} data-testid={`tab-${t.id}`} className={`px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${tab === t.id ? 'border-[#00d4aa] text-[#00d4aa]' : 'border-transparent text-[#4A5B6E] hover:text-[#E8EDF2]'}`}>{t.label}</button>
        ))}
      </div>

      {tab === 'utilization' && utilization && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Employee Utilization — Target: {summary.target}%</h2></div>
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">{['Employee', 'Role', 'Location', 'Billable', 'Non-Bill', 'Total', 'Utilization', 'Status'].map(h => (<th key={h} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>))}</tr></thead><tbody>{utilization.employees.map(emp => (<tr key={emp.employee_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50"><td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] text-[10px]">{emp.employee_id}</span><span className="font-bold text-[#E8EDF2] ml-1.5">{emp.name}</span></td><td className="px-3 py-2.5 text-[#4A5B6E]">{emp.role}</td><td className="px-3 py-2.5 text-[#4A5B6E]">{emp.location}</td><td className="px-3 py-2.5 font-mono text-[#00d4aa] font-bold">{emp.billable_hours}h</td><td className="px-3 py-2.5 font-mono text-[#4A5B6E]">{emp.non_billable_hours}h</td><td className="px-3 py-2.5 font-mono text-[#E8EDF2]">{emp.total_hours}h</td><td className="px-3 py-2.5"><div className="flex items-center gap-2"><div className="w-16 h-1.5 bg-[#1B2D42] rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width: `${Math.min(emp.utilization_pct,100)}%`, background: emp.utilization_pct >= 80 ? '#22c55e' : emp.utilization_pct >= 50 ? '#eab308' : '#ef4444' }} /></div><span className="font-bold text-[#E8EDF2]">{emp.utilization_pct}%</span></div></td><td className="px-3 py-2.5"><span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${STATUS_COLORS[emp.status] || '#6b7280'}18`, color: STATUS_COLORS[emp.status] || '#6b7280' }}>{emp.status}</span></td></tr>))}</tbody></table></div>
        </div>
      )}

      {tab === 'consolidation' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Monthly Hours by Project</h2></div>
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">{['Project', 'Client', 'Type', 'Billable', 'Non-Bill', 'Total', 'Team'].map(h => (<th key={h} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>))}</tr></thead><tbody>{consolidation.map(c => (<tr key={c.project_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50"><td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] font-bold">{c.project_id}</span> <span className="text-[#E8EDF2]">{c.project_name}</span></td><td className="px-3 py-2.5 text-[#4A5B6E]">{c.client}</td><td className="px-3 py-2.5 text-[#4A5B6E]">{c.type}</td><td className="px-3 py-2.5 font-mono text-[#00d4aa] font-bold">{c.billable_hours}h</td><td className="px-3 py-2.5 font-mono text-[#4A5B6E]">{c.non_billable_hours}h</td><td className="px-3 py-2.5 font-mono text-[#E8EDF2] font-bold">{c.total_hours}h</td><td className="px-3 py-2.5 text-[#4A5B6E] text-[10px]">{c.employees?.join(', ')}</td></tr>))}</tbody></table></div>
        </div>
      )}

      {tab === 'entries' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">{['Employee', 'Week', 'Period', 'Hours', 'Status', 'Actions', ''].map(h => (<th key={h||'e'} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>))}</tr></thead><tbody>
            {timesheets.map(ts => (
              <React.Fragment key={ts.id || ts.employee_id+ts.week}>
                <tr className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50 cursor-pointer" onClick={() => setExpandedEmployee(expandedEmployee === ts.id ? null : ts.id)}>
                  <td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] text-[10px]">{ts.employee_id}</span><span className="font-bold text-[#E8EDF2] ml-1.5">{ts.employee_name}</span></td>
                  <td className="px-3 py-2.5 text-[#E8EDF2] font-bold">{ts.week}</td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{ts.week_start} - {ts.week_end}</td>
                  <td className="px-3 py-2.5 font-mono text-[#E8EDF2] font-bold">{ts.total_hours}h</td>
                  <td className="px-3 py-2.5"><span className={`px-2 py-0.5 rounded text-[9px] font-bold ${ts.status === 'Approved' ? 'bg-[#22c55e]/10 text-[#22c55e]' : ts.status === 'Rejected' ? 'bg-[#ef4444]/10 text-[#ef4444]' : 'bg-[#eab308]/10 text-[#eab308]'}`}>{ts.status}</span></td>
                  <td className="px-3 py-2.5" onClick={e => e.stopPropagation()}>
                    {ts.status === 'Submitted' && (
                      <div className="flex gap-1">
                        <button onClick={() => approveTs(ts.id)} className="px-2 py-1 bg-[#22c55e]/15 text-[#22c55e] rounded text-[10px] font-bold hover:bg-[#22c55e]/25 flex items-center gap-0.5" data-testid={`approve-ts-${ts.id}`}><Check size={10} /> Approve</button>
                        <button onClick={() => rejectTs(ts.id)} className="px-2 py-1 bg-[#ef4444]/15 text-[#ef4444] rounded text-[10px] font-bold hover:bg-[#ef4444]/25 flex items-center gap-0.5" data-testid={`reject-ts-${ts.id}`}><XCircle size={10} /> Reject</button>
                      </div>
                    )}
                  </td>
                  <td className="px-3 py-2.5 text-[#4A5B6E]">{expandedEmployee === ts.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                </tr>
                {expandedEmployee === ts.id && (
                  <tr><td colSpan={7} className="p-3 bg-[#152236]/50">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">{ts.entries?.map((entry, i) => (
                      <div key={`${entry.project_id}-${i}`} className={`p-2 rounded border text-[10px] ${entry.billable ? 'border-[#00d4aa]/30 bg-[#00d4aa]/5' : 'border-[#1B2D42] bg-[#0A1628]'}`}>
                        <div className="flex items-center gap-1 mb-0.5"><span className="font-mono font-bold text-[#38bdf8]">{entry.project_id}</span><span className={`text-[8px] font-bold px-1 rounded ${entry.billable ? 'bg-[#00d4aa]/20 text-[#00d4aa]' : 'bg-[#4A5B6E]/20 text-[#4A5B6E]'}`}>{entry.billable ? 'BILL' : 'NON'}</span></div>
                        <p className="font-bold text-[#E8EDF2]">{entry.hours}h</p>
                        {entry.note && <p className="text-[#4A5B6E]">{entry.note}</p>}
                      </div>
                    ))}</div>
                  </td></tr>
                )}
              </React.Fragment>
            ))}
          </tbody></table></div>
        </div>
      )}

      <AiEntryModal
        open={showAiModal}
        onClose={() => setShowAiModal(false)}
        module="timesheet"
        title="New Timesheet"
        placeholder='e.g. "Log 40h for Raj (EMP-005) on PRJ-001, all billable at 2500/hr, week W1-Apr"'
        onSubmit={handleCreateTimesheet}
      />
    </div>
  );
}
