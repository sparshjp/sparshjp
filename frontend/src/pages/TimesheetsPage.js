import React, { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Clock, Users, TrendingUp, CheckCircle, ChevronDown, ChevronUp, Plus, Loader2, X, Check, XCircle } from 'lucide-react';

const STATUS_COLORS = { 'On Track': '#22c55e', 'At Risk': '#eab308', 'Below Target': '#ef4444' };

export default function TimesheetsPage() {
  const [timesheets, setTimesheets] = useState([]);
  const [utilization, setUtilization] = useState(null);
  const [consolidation, setConsolidation] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [projects, setProjects] = useState([]);
  const [tab, setTab] = useState('utilization');
  const [loading, setLoading] = useState(true);
  const [expandedEmployee, setExpandedEmployee] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    employee_id: '', employee_name: '', week: '', week_start: '', week_end: '',
    entries: [{ project_id: '', hours: 0, billable: true, note: '', rate: 0, currency: 'INR' }],
    leave_hours: 0, leave_type: '',
  });

  const loadData = useCallback(() => {
    Promise.all([
      fetch(`${API}/timesheets`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/timesheets/utilization`).then(r => r.ok ? r.json() : null),
      fetch(`${API}/timesheets/consolidation`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/timesheets/employees`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/projects`).then(r => r.ok ? r.json() : []),
    ]).then(([ts, util, cons, emps, prj]) => {
      setTimesheets(ts);
      setUtilization(util);
      setConsolidation(cons);
      setEmployees(emps);
      setProjects(prj);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const createTimesheet = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const totalHours = form.entries.reduce((s, en) => s + (en.hours || 0), 0) + (form.leave_hours || 0);
      await fetch(`${API}/timesheets`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, total_hours: totalHours }),
      });
      setShowForm(false);
      setForm({ employee_id: '', employee_name: '', week: '', week_start: '', week_end: '', entries: [{ project_id: '', hours: 0, billable: true, note: '', rate: 0, currency: 'INR' }], leave_hours: 0, leave_type: '' });
      loadData();
    } catch {}
    setSubmitting(false);
  };

  const approveTs = async (id) => {
    await fetch(`${API}/timesheets/${id}/approve`, { method: 'PUT' });
    loadData();
  };

  const rejectTs = async (id) => {
    const reason = prompt('Rejection reason (optional):') || '';
    await fetch(`${API}/timesheets/${id}/reject`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ reason }) });
    loadData();
  };

  const addEntry = () => setForm(p => ({ ...p, entries: [...p.entries, { project_id: '', hours: 0, billable: true, note: '', rate: 0, currency: 'INR' }] }));
  const updateEntry = (i, field, value) => {
    const entries = [...form.entries];
    if (field === 'hours' || field === 'rate') entries[i][field] = Number(value);
    else if (field === 'billable') entries[i][field] = value;
    else entries[i][field] = value;
    setForm(p => ({ ...p, entries }));
  };
  const removeEntry = (i) => setForm(p => ({ ...p, entries: p.entries.filter((_, idx) => idx !== i) }));

  const summary = utilization?.summary || {};

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading timesheets...</div>;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6" data-testid="timesheets-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="timesheets-title">Timesheets & Utilization</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Resource tracking & billing</p>
        </div>
        <button onClick={() => setShowForm(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-timesheet-btn"><Plus size={16} /> New Timesheet</button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Avg Utilization', value: `${summary.avg_utilization || 0}%`, icon: TrendingUp, color: summary.avg_utilization >= 75 ? '#22c55e' : '#eab308' },
          { label: 'Total Billable', value: `${summary.total_billable || 0}h`, icon: Clock, color: '#38bdf8' },
          { label: 'Billable Staff', value: summary.headcount || 0, icon: Users, color: '#a78bfa' },
          { label: 'Timesheets', value: timesheets.length, icon: CheckCircle, color: '#00d4aa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`ts-summary-${c.label}`}>
            <div className="flex items-center gap-2 mb-2">
              <c.icon size={16} style={{ color: c.color }} />
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E]">{c.label}</span>
            </div>
            <p className="text-xl font-black text-[#E8EDF2]">{c.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[#1B2D42]">
        {[
          { id: 'utilization', label: 'Utilization Report' },
          { id: 'consolidation', label: 'Project Hours' },
          { id: 'entries', label: 'Timesheet Entries' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} data-testid={`tab-${t.id}`}
            className={`px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${tab === t.id ? 'border-[#00d4aa] text-[#00d4aa]' : 'border-transparent text-[#4A5B6E] hover:text-[#E8EDF2]'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Utilization Tab */}
      {tab === 'utilization' && utilization && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Employee Utilization — Target: {summary.target}%</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
                {['Employee', 'Role', 'Location', 'Billable', 'Non-Bill', 'Total', 'Utilization', 'Status'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
                ))}
              </tr></thead>
              <tbody>
                {utilization.employees.map(emp => (
                  <tr key={emp.employee_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`util-row-${emp.employee_id}`}>
                    <td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] text-[10px]">{emp.employee_id}</span><span className="font-bold text-[#E8EDF2] ml-1.5">{emp.name}</span></td>
                    <td className="px-3 py-2.5 text-[#4A5B6E]">{emp.role}</td>
                    <td className="px-3 py-2.5 text-[#4A5B6E]">{emp.location}</td>
                    <td className="px-3 py-2.5 font-mono text-[#00d4aa] font-bold">{emp.billable_hours}h</td>
                    <td className="px-3 py-2.5 font-mono text-[#4A5B6E]">{emp.non_billable_hours}h</td>
                    <td className="px-3 py-2.5 font-mono text-[#E8EDF2]">{emp.total_hours}h</td>
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-[#1B2D42] rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width: `${Math.min(emp.utilization_pct, 100)}%`, background: emp.utilization_pct >= 80 ? '#22c55e' : emp.utilization_pct >= 50 ? '#eab308' : '#ef4444' }} /></div>
                        <span className="font-bold text-[#E8EDF2]">{emp.utilization_pct}%</span>
                      </div>
                    </td>
                    <td className="px-3 py-2.5"><span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${STATUS_COLORS[emp.status] || '#6b7280'}18`, color: STATUS_COLORS[emp.status] || '#6b7280' }}>{emp.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Consolidation Tab */}
      {tab === 'consolidation' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]"><h2 className="text-sm font-bold text-[#E8EDF2]">Monthly Hours by Project</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
                {['Project', 'Client', 'Type', 'Billable Hrs', 'Non-Bill Hrs', 'Total', 'Team'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
                ))}
              </tr></thead>
              <tbody>
                {consolidation.map(c => (
                  <tr key={c.project_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`consol-row-${c.project_id}`}>
                    <td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] font-bold">{c.project_id}</span><span className="text-[#E8EDF2] ml-1.5">{c.project_name}</span></td>
                    <td className="px-3 py-2.5 text-[#4A5B6E]">{c.client}</td>
                    <td className="px-3 py-2.5 text-[#4A5B6E]">{c.type}</td>
                    <td className="px-3 py-2.5 font-mono text-[#00d4aa] font-bold">{c.billable_hours}h</td>
                    <td className="px-3 py-2.5 font-mono text-[#4A5B6E]">{c.non_billable_hours}h</td>
                    <td className="px-3 py-2.5 font-mono text-[#E8EDF2] font-bold">{c.total_hours}h</td>
                    <td className="px-3 py-2.5 text-[#4A5B6E] text-[10px]">{c.employees?.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Entries Tab */}
      {tab === 'entries' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42] flex items-center justify-between"><h2 className="text-sm font-bold text-[#E8EDF2]">Weekly Timesheet Entries ({timesheets.length})</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
                {['Employee', 'Week', 'Period', 'Total Hrs', 'Status', 'Entries', 'Actions', ''].map(h => (
                  <th key={h || 'expand'} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
                ))}
              </tr></thead>
              <tbody>
                {timesheets.map(ts => (
                  <React.Fragment key={ts.id || ts.employee_id + ts.week}>
                    <tr className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50 cursor-pointer"
                        onClick={() => setExpandedEmployee(expandedEmployee === ts.id ? null : ts.id)}>
                      <td className="px-3 py-2.5"><span className="font-mono text-[#38bdf8] text-[10px]">{ts.employee_id}</span><span className="font-bold text-[#E8EDF2] ml-1.5">{ts.employee_name}</span></td>
                      <td className="px-3 py-2.5 text-[#E8EDF2] font-bold">{ts.week}</td>
                      <td className="px-3 py-2.5 text-[#4A5B6E]">{ts.week_start} - {ts.week_end}</td>
                      <td className="px-3 py-2.5 font-mono text-[#E8EDF2] font-bold">{ts.total_hours}h</td>
                      <td className="px-3 py-2.5"><span className={`px-2 py-0.5 rounded text-[9px] font-bold ${ts.status === 'Approved' ? 'bg-[#22c55e]/10 text-[#22c55e]' : ts.status === 'Rejected' ? 'bg-[#ef4444]/10 text-[#ef4444]' : 'bg-[#eab308]/10 text-[#eab308]'}`}>{ts.status}</span></td>
                      <td className="px-3 py-2.5 text-[#4A5B6E]">{ts.entries?.length} entries</td>
                      <td className="px-3 py-2.5">
                        {ts.status === 'Submitted' && (
                          <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                            <button onClick={() => approveTs(ts.id)} className="px-2 py-1 bg-[#22c55e]/15 text-[#22c55e] rounded text-[10px] font-bold hover:bg-[#22c55e]/25 flex items-center gap-0.5" data-testid={`approve-ts-${ts.id}`}><Check size={10} /> Approve</button>
                            <button onClick={() => rejectTs(ts.id)} className="px-2 py-1 bg-[#ef4444]/15 text-[#ef4444] rounded text-[10px] font-bold hover:bg-[#ef4444]/25 flex items-center gap-0.5" data-testid={`reject-ts-${ts.id}`}><XCircle size={10} /> Reject</button>
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-2.5 text-[#4A5B6E]">{expandedEmployee === ts.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                    </tr>
                    {expandedEmployee === ts.id && (
                      <tr key={`${ts.id}-detail`}>
                        <td colSpan={8} className="p-3 bg-[#152236]/50">
                          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
                            {ts.entries?.map((entry, i) => (
                              <div key={`${entry.project_id}-${i}`} className={`p-2 rounded border text-[10px] ${entry.billable ? 'border-[#00d4aa]/30 bg-[#00d4aa]/5' : 'border-[#1B2D42] bg-[#0A1628]'}`}>
                                <div className="flex items-center gap-1 mb-0.5">
                                  <span className="font-mono font-bold text-[#38bdf8]">{entry.project_id}</span>
                                  <span className={`text-[8px] font-bold px-1 rounded ${entry.billable ? 'bg-[#00d4aa]/20 text-[#00d4aa]' : 'bg-[#4A5B6E]/20 text-[#4A5B6E]'}`}>{entry.billable ? 'BILLABLE' : 'NON-BILL'}</span>
                                </div>
                                <p className="font-bold text-[#E8EDF2]">{entry.hours}h</p>
                                {entry.note && <p className="text-[#4A5B6E]">{entry.note}</p>}
                                {entry.rate > 0 && <p className="text-[#fbbf24]">{entry.currency || 'INR'} {entry.rate}/hr</p>}
                                {entry.ot_hours > 0 && <p className="text-[#f59e0b]">+{entry.ot_hours}h OT</p>}
                              </div>
                            ))}
                            {ts.leave_hours > 0 && (
                              <div className="p-2 rounded border border-[#ef4444]/30 bg-[#ef4444]/5 text-[10px]">
                                <p className="font-bold text-[#ef4444]">{ts.leave_hours}h {ts.leave_type || 'Leave'}</p>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Timesheet Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={createTimesheet} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-[#E8EDF2]">New Timesheet</h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={18} /></button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {employees.length > 0 ? (
                <select value={form.employee_id} onChange={e => { const emp = employees.find(em => em.id === e.target.value); setForm(p => ({ ...p, employee_id: e.target.value, employee_name: emp?.name || '' })); }} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="ts-employee-select">
                  <option value="">Select Employee</option>
                  {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name} ({emp.id})</option>)}
                </select>
              ) : (
                <input placeholder="Employee ID" value={form.employee_id} onChange={e => setForm(p => ({ ...p, employee_id: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="ts-employee-id" />
              )}
              <input placeholder="Week (e.g. W1-Mar)" value={form.week} onChange={e => setForm(p => ({ ...p, week: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="ts-week" />
            </div>
            {!employees.length && (
              <input placeholder="Employee Name" value={form.employee_name} onChange={e => setForm(p => ({ ...p, employee_name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" />
            )}
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs text-[#4A5B6E]">Week Start</label><input type="date" value={form.week_start} onChange={e => setForm(p => ({ ...p, week_start: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" /></div>
              <div><label className="text-xs text-[#4A5B6E]">Week End</label><input type="date" value={form.week_end} onChange={e => setForm(p => ({ ...p, week_end: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" /></div>
            </div>

            {/* Time Entries */}
            <div>
              <div className="flex items-center justify-between mb-2"><span className="text-xs text-[#4A5B6E] uppercase tracking-wider">Time Entries</span><button type="button" onClick={addEntry} className="text-xs text-[#00C9A7] hover:underline">+ Add Entry</button></div>
              {form.entries.map((en, i) => (
                <div key={i} className="bg-[#152236] rounded-lg p-3 mb-2 space-y-2">
                  <div className="flex gap-2">
                    {projects.length > 0 ? (
                      <select value={en.project_id} onChange={e => updateEntry(i, 'project_id', e.target.value)} className="flex-1 px-2 py-1.5 bg-[#0A1628] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" data-testid={`entry-project-${i}`}>
                        <option value="">Select Project</option>
                        {projects.map(p => <option key={p.id} value={p.id}>{p.id} — {p.name}</option>)}
                      </select>
                    ) : (
                      <input placeholder="Project ID" value={en.project_id} onChange={e => updateEntry(i, 'project_id', e.target.value)} className="flex-1 px-2 py-1.5 bg-[#0A1628] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" data-testid={`entry-project-${i}`} />
                    )}
                    <input type="number" placeholder="Hours" value={en.hours || ''} onChange={e => updateEntry(i, 'hours', e.target.value)} className="w-20 px-2 py-1.5 bg-[#0A1628] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" data-testid={`entry-hours-${i}`} />
                    <input type="number" placeholder="Rate/hr" value={en.rate || ''} onChange={e => updateEntry(i, 'rate', e.target.value)} className="w-24 px-2 py-1.5 bg-[#0A1628] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                    <label className="flex items-center gap-1 text-xs text-[#7A8BA0]"><input type="checkbox" checked={en.billable} onChange={e => updateEntry(i, 'billable', e.target.checked)} /> Bill</label>
                    {form.entries.length > 1 && <button type="button" onClick={() => removeEntry(i)} className="text-[#ef4444] text-xs px-1">X</button>}
                  </div>
                  <input placeholder="Note (optional)" value={en.note} onChange={e => updateEntry(i, 'note', e.target.value)} className="w-full px-2 py-1 bg-[#0A1628] border border-[#1B2D42] rounded text-xs text-[#E8EDF2] outline-none" />
                </div>
              ))}
            </div>

            {/* Leave */}
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="Leave Hours" value={form.leave_hours || ''} onChange={e => setForm(p => ({ ...p, leave_hours: Number(e.target.value) }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" />
              <select value={form.leave_type} onChange={e => setForm(p => ({ ...p, leave_type: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none">
                <option value="">Leave Type</option><option value="Casual">Casual</option><option value="Sick">Sick</option><option value="Comp-off">Comp-off</option><option value="Holiday">Holiday</option>
              </select>
            </div>

            <p className="text-xs text-[#4A5B6E]">Total: {form.entries.reduce((s, en) => s + (en.hours || 0), 0) + (form.leave_hours || 0)}h ({form.entries.filter(e => e.billable).reduce((s, en) => s + (en.hours || 0), 0)}h billable)</p>

            <div className="flex gap-2 justify-end pt-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="submit-timesheet-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Submit Timesheet</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
