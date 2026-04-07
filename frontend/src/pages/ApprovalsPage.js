import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { CheckCircle2, XCircle, Clock, Shield, Sparkles } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

const STATUS_COLORS = { pending: '#f59e0b', approved: '#22c55e', rejected: '#ef4444' };

export default function ApprovalsPage() {
  const [tab, setTab] = useState('requests');
  const [requests, setRequests] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showWfModal, setShowWfModal] = useState(false);
  const [showReqModal, setShowReqModal] = useState(false);

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

  const createWorkflow = async (data) => {
    const res = await fetch(`${API}/approvals/workflows`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to create workflow');
    load();
  };

  const submitRequest = async (data) => {
    const res = await fetch(`${API}/approvals/requests`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to submit request');
    load();
  };

  const handleAction = async (reqId, action) => {
    await fetch(`${API}/approvals/requests/${reqId}/${action}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ approved_by: 'admin', rejected_by: 'admin', comments: '' }) });
    load();
  };

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
          <button onClick={() => setShowReqModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] transition-colors flex items-center gap-1" data-testid="new-request-btn"><Sparkles size={16} /> New Request</button>
          <button onClick={() => setShowWfModal(true)} className="px-3 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm hover:bg-[#152236] transition-colors flex items-center gap-1" data-testid="new-workflow-btn"><Shield size={16} /> New Workflow</button>
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

      {/* AI Entry Modals */}
      <AiEntryModal open={showWfModal} onClose={() => setShowWfModal(false)} module="approval_workflow" title="New Approval Workflow" placeholder='e.g. "PO approval: above 50K needs finance_manager, above 5L needs admin"' onSubmit={createWorkflow} />
      <AiEntryModal open={showReqModal} onClose={() => setShowReqModal(false)} module="approval_request" title="Submit Approval Request" placeholder='e.g. "Submit expense claim for Raj - 45000 INR for client travel"' onSubmit={submitRequest} />
    </div>
  );
}
