import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { CheckCircle2, XCircle, Clock, Plus, ChevronDown, ChevronUp, Shield, Loader2, AlertTriangle } from 'lucide-react';

const STATUS_COLORS = { pending: '#f59e0b', approved: '#22c55e', rejected: '#ef4444' };
const TYPES = ['purchase_order', 'sales_invoice', 'expense', 'journal_entry', 'leave_request', 'timesheet'];

export default function ApprovalsPage() {
  const [tab, setTab] = useState('requests');
  const [requests, setRequests] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showWfForm, setShowWfForm] = useState(false);
  const [showReqForm, setShowReqForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [wfForm, setWfForm] = useState({ name: '', type: 'purchase_order', threshold_amount: 0, steps: [{ role: 'admin', label: 'Admin Approval' }] });
  const [reqForm, setReqForm] = useState({ type: 'purchase_order', reference_name: '', amount: 0, requester_name: '', comments: '' });

  const load = useCallback(async () => {
    try {
      const [rq, wf, st] = await Promise.all([
        fetch(`${API}/approvals/requests`).then(r => r.json()),
        fetch(`${API}/approvals/workflows`).then(r => r.json()),
        fetch(`${API}/approvals/stats`).then(r => r.json()),
      ]);
      setRequests(Array.isArray(rq) ? rq : []);
      setWorkflows(Array.isArray(wf) ? wf : []);
      setStats(st || {});
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createWorkflow = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await fetch(`${API}/approvals/workflows`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(wfForm) });
      setShowWfForm(false);
      setWfForm({ name: '', type: 'purchase_order', threshold_amount: 0, steps: [{ role: 'admin', label: 'Admin Approval' }] });
      load();
    } catch {}
    setSubmitting(false);
  };

  const submitRequest = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await fetch(`${API}/approvals/requests`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(reqForm) });
      setShowReqForm(false);
      setReqForm({ type: 'purchase_order', reference_name: '', amount: 0, requester_name: '', comments: '' });
      load();
    } catch {}
    setSubmitting(false);
  };

  const handleAction = async (reqId, action) => {
    await fetch(`${API}/approvals/requests/${reqId}/${action}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ approved_by: 'admin', rejected_by: 'admin', comments: '' }) });
    load();
  };

  const addStep = () => setWfForm(p => ({ ...p, steps: [...p.steps, { role: 'admin', label: '' }] }));
  const removeStep = (i) => setWfForm(p => ({ ...p, steps: p.steps.filter((_, idx) => idx !== i) }));

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading approvals...</div>;

  const pending = requests.filter(r => r.status === 'pending');

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="approvals-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="approvals-title">Approval Workflows</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Configurable approval chains for POs, invoices, expenses</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowReqForm(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] transition-colors flex items-center gap-1" data-testid="new-request-btn"><Plus size={16} /> New Request</button>
          <button onClick={() => setShowWfForm(true)} className="px-3 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm hover:bg-[#152236] transition-colors flex items-center gap-1" data-testid="new-workflow-btn"><Shield size={16} /> New Workflow</button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Pending', value: stats.pending?.count || 0, icon: Clock, color: '#f59e0b' },
          { label: 'Approved', value: stats.approved?.count || 0, icon: CheckCircle2, color: '#22c55e' },
          { label: 'Rejected', value: stats.rejected?.count || 0, icon: XCircle, color: '#ef4444' },
          { label: 'Workflows', value: workflows.length, icon: Shield, color: '#38bdf8' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`stat-${c.label.toLowerCase()}`}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit">
        {['requests', 'workflows'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`tab-${t}`}>{t} {t === 'requests' && pending.length > 0 && <span className="ml-1 px-1.5 py-0.5 rounded-full bg-[#f59e0b]/20 text-[#f59e0b] text-xs">{pending.length}</span>}</button>
        ))}
      </div>

      {/* Requests Tab */}
      {tab === 'requests' && (
        <div className="space-y-3">
          {requests.length === 0 && <p className="text-[#4A5B6E] text-center py-8">No approval requests yet</p>}
          {requests.map(r => (
            <div key={r.id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`request-${r.id}`}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-[#E8EDF2]">{r.reference_name || r.type}</span>
                    <span className="px-2 py-0.5 rounded-full text-xs font-bold capitalize" style={{ color: STATUS_COLORS[r.status], background: STATUS_COLORS[r.status] + '15' }}>{r.status}</span>
                    <span className="px-2 py-0.5 rounded-full text-xs bg-[#152236] text-[#7A8BA0] capitalize">{r.type?.replace('_', ' ')}</span>
                  </div>
                  <p className="text-xs text-[#4A5B6E] mt-1">By {r.requester_name || 'Unknown'} | Amount: {r.amount?.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</p>
                  {r.comments && <p className="text-xs text-[#4A5B6E] mt-1 italic">{r.comments}</p>}
                </div>
                {r.status === 'pending' && (
                  <div className="flex gap-2">
                    <button onClick={() => handleAction(r.id, 'approve')} className="px-3 py-1.5 bg-[#22c55e]/15 text-[#22c55e] rounded text-xs font-bold hover:bg-[#22c55e]/25" data-testid={`approve-${r.id}`}>Approve</button>
                    <button onClick={() => handleAction(r.id, 'reject')} className="px-3 py-1.5 bg-[#ef4444]/15 text-[#ef4444] rounded text-xs font-bold hover:bg-[#ef4444]/25" data-testid={`reject-${r.id}`}>Reject</button>
                  </div>
                )}
              </div>
              {/* Steps */}
              <div className="mt-3 flex gap-2 flex-wrap">
                {(r.steps || []).map((s, i) => (
                  <div key={i} className="flex items-center gap-1 text-xs">
                    {s.status === 'approved' ? <CheckCircle2 size={14} className="text-[#22c55e]" /> : s.status === 'rejected' ? <XCircle size={14} className="text-[#ef4444]" /> : <Clock size={14} className="text-[#f59e0b]" />}
                    <span className="text-[#7A8BA0]">{s.label || s.role}</span>
                    {i < r.steps.length - 1 && <span className="text-[#1B2D42] mx-1">&rarr;</span>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Workflows Tab */}
      {tab === 'workflows' && (
        <div className="space-y-3">
          {workflows.length === 0 && <p className="text-[#4A5B6E] text-center py-8">No workflows configured</p>}
          {workflows.map(w => (
            <div key={w.id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`workflow-${w.id}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-bold text-[#E8EDF2]">{w.name}</p>
                  <p className="text-xs text-[#4A5B6E]">Type: {w.type?.replace('_', ' ')} | Threshold: {w.threshold_amount?.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${w.is_active ? 'text-[#22c55e] bg-[#22c55e]/15' : 'text-[#4A5B6E] bg-[#152236]'}`}>{w.is_active ? 'Active' : 'Inactive'}</span>
              </div>
              <div className="mt-2 flex gap-2 flex-wrap">
                {(w.steps || []).map((s, i) => (
                  <span key={i} className="px-2 py-1 rounded bg-[#152236] text-xs text-[#7A8BA0]">{i + 1}. {s.label || s.role}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Workflow Form Modal */}
      {showWfForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowWfForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={createWorkflow} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-lg space-y-4">
            <h2 className="text-lg font-bold text-[#E8EDF2]">New Approval Workflow</h2>
            <input placeholder="Workflow Name" value={wfForm.name} onChange={e => setWfForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] focus:border-[#00C9A7] outline-none" required data-testid="wf-name" />
            <div className="grid grid-cols-2 gap-3">
              <select value={wfForm.type} onChange={e => setWfForm(p => ({ ...p, type: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="wf-type">
                {TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
              </select>
              <input type="number" placeholder="Threshold Amount" value={wfForm.threshold_amount} onChange={e => setWfForm(p => ({ ...p, threshold_amount: Number(e.target.value) }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="wf-threshold" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2"><span className="text-xs text-[#4A5B6E] uppercase tracking-wider">Approval Steps</span><button type="button" onClick={addStep} className="text-xs text-[#00C9A7] hover:underline">+ Add Step</button></div>
              {wfForm.steps.map((s, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <select value={s.role} onChange={e => { const ns = [...wfForm.steps]; ns[i].role = e.target.value; setWfForm(p => ({ ...p, steps: ns })); }} className="flex-1 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none">
                    {['admin', 'creator', 'finance_manager', 'project_manager', 'hr_manager'].map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                  </select>
                  <input placeholder="Step Label" value={s.label} onChange={e => { const ns = [...wfForm.steps]; ns[i].label = e.target.value; setWfForm(p => ({ ...p, steps: ns })); }} className="flex-1 px-2 py-1.5 bg-[#152236] border border-[#1B2D42] rounded text-sm text-[#E8EDF2] outline-none" />
                  {wfForm.steps.length > 1 && <button type="button" onClick={() => removeStep(i)} className="text-[#ef4444] text-xs px-2">X</button>}
                </div>
              ))}
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowWfForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="create-workflow-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Create</button>
            </div>
          </form>
        </div>
      )}

      {/* Request Form Modal */}
      {showReqForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowReqForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={submitRequest} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-lg space-y-4">
            <h2 className="text-lg font-bold text-[#E8EDF2]">Submit Approval Request</h2>
            <select value={reqForm.type} onChange={e => setReqForm(p => ({ ...p, type: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="req-type">
              {TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
            </select>
            <input placeholder="Reference Name" value={reqForm.reference_name} onChange={e => setReqForm(p => ({ ...p, reference_name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="req-ref-name" />
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="Amount" value={reqForm.amount} onChange={e => setReqForm(p => ({ ...p, amount: Number(e.target.value) }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="req-amount" />
              <input placeholder="Requester Name" value={reqForm.requester_name} onChange={e => setReqForm(p => ({ ...p, requester_name: e.target.value }))} className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="req-requester" />
            </div>
            <textarea placeholder="Comments" value={reqForm.comments} onChange={e => setReqForm(p => ({ ...p, comments: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none h-20 resize-none" />
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowReqForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="submit-request-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Submit</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
