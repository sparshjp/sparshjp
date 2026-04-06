import React, { useState, useEffect } from 'react';
import { Factory, Play, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import { ModuleAIPrompt } from '../components/AISmartEntry';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(num) {
  if (!num && num !== 0) return '--';
  return new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num);
}

export default function ManufacturingModule() {
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedWO, setExpandedWO] = useState(null);
  const [completeData, setCompleteData] = useState({ qty_produced: 0, qty_rejected: 0, scrap_reason: '' });
  const [showCompleteModal, setShowCompleteModal] = useState(null);

  useEffect(() => { fetchWorkOrders(); }, []);

  async function fetchWorkOrders() {
    try {
      setLoading(true);
      const r = await fetch(`${API}/api/manufacturing/work-orders`);
      if (r.ok) setWorkOrders(await r.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function startWO(woId) {
    try {
      const r = await fetch(`${API}/api/manufacturing/work-orders/${woId}/start`, { method: 'POST' });
      if (r.ok) { toast.success('Work Order started - materials issued'); fetchWorkOrders(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
  }

  async function completeWO(woId) {
    try {
      const r = await fetch(`${API}/api/manufacturing/work-orders/${woId}/complete`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(completeData)
      });
      if (r.ok) { toast.success('Work Order completed - FG received'); setShowCompleteModal(null); fetchWorkOrders(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
  }

  async function cancelWO(woId) {
    try {
      const r = await fetch(`${API}/api/manufacturing/work-orders/${woId}/cancel`, { method: 'POST' });
      if (r.ok) { toast.success('Work Order cancelled'); fetchWorkOrders(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
  }

  const statusColor = (s) => {
    switch (s) {
      case 'Draft': return 'bg-[#1B2D42] text-[#7A8BA0]';
      case 'In Progress': return 'bg-[#FFB547]/15 text-[#FFB547]';
      case 'Completed': return 'bg-[#00C9A7]/15 text-[#00C9A7]';
      case 'Cancelled': return 'bg-[#FF4D6A]/15 text-[#FF4D6A]';
      default: return 'bg-[#1B2D42] text-[#7A8BA0]';
    }
  };

  return (
    <div className="space-y-6" data-testid="manufacturing-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Manufacturing</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Work Orders, BOM, Production tracking with auto-accounting</p>
        </div>
      </div>

      {/* AI Prompt — replaces old form */}
      <ModuleAIPrompt
        placeholder={`Describe your work order... e.g. "Produce 3000 KG PU-C450"`}
        defaultIntent="work_order"
        onCreated={fetchWorkOrders}
      />

      {/* Complete WO Modal */}
      {showCompleteModal && (
        <div className="bg-[#152236] border border-[#FFB547]/30 rounded-lg p-6 space-y-4" data-testid="mfg-complete-modal">
          <h2 className="text-base font-bold text-[#FFB547]">Complete Work Order</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Qty Produced</label>
              <input type="number" value={completeData.qty_produced}
                onChange={(e) => setCompleteData({ ...completeData, qty_produced: parseFloat(e.target.value) || 0 })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Qty Rejected (Scrap)</label>
              <input type="number" value={completeData.qty_rejected}
                onChange={(e) => setCompleteData({ ...completeData, qty_rejected: parseFloat(e.target.value) || 0 })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Scrap Reason</label>
              <input type="text" value={completeData.scrap_reason}
                onChange={(e) => setCompleteData({ ...completeData, scrap_reason: e.target.value })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] placeholder:text-[#4A5B6E]" placeholder="Optional" />
            </div>
          </div>
          <div className="flex gap-3">
            <button data-testid="mfg-confirm-complete" onClick={() => completeWO(showCompleteModal)}
              className="flex items-center gap-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] px-5 py-2 rounded-lg text-sm font-semibold transition-colors">
              <CheckCircle size={14} /> Confirm Completion
            </button>
            <button onClick={() => setShowCompleteModal(null)} className="bg-[#1B2D42] hover:bg-[#152236] text-[#7A8BA0] px-5 py-2 rounded-lg text-sm font-medium transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Work Orders List */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6" data-testid="mfg-wo-list">
        <h2 className="text-base font-bold text-[#E8EDF2] mb-4">Work Orders ({workOrders.length})</h2>
        {loading ? (
          <div className="text-[#4A5B6E] py-8 text-center">Loading...</div>
        ) : workOrders.length === 0 ? (
          <div className="text-center py-12">
            <Factory className="mx-auto mb-3 text-[#1B2D42]" size={48} />
            <p className="text-[#4A5B6E]">No work orders yet</p>
            <p className="text-xs text-[#4A5B6E] mt-1">Create your first work order to start production</p>
          </div>
        ) : (
          <div className="space-y-3">
            {workOrders.map((wo) => (
              <div key={wo.id} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg" data-testid={`mfg-wo-${wo.id}`}>
                <div className="p-4 flex justify-between items-start cursor-pointer" onClick={() => setExpandedWO(expandedWO === wo.id ? null : wo.id)}>
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      {expandedWO === wo.id ? <ChevronDown className="w-4 h-4 text-[#4A5B6E]" /> : <ChevronRight className="w-4 h-4 text-[#4A5B6E]" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm font-bold text-[#00C9A7]">{wo.wo_number}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusColor(wo.status)}`}>{wo.status}</span>
                      </div>
                      <p className="text-sm text-[#E8EDF2]">{wo.production_item_name || wo.production_item}</p>
                      <p className="text-xs text-[#4A5B6E] font-mono mt-1">Qty: {wo.qty_to_produce} | RM Cost: {formatINR(wo.total_rm_cost)} | Cost/Unit: {formatINR(wo.cost_per_unit)}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {wo.status === 'Draft' && (
                      <button data-testid={`mfg-start-${wo.id}`} onClick={(e) => { e.stopPropagation(); startWO(wo.id); }}
                        className="flex items-center gap-1 px-3 py-1 bg-[#FFB547]/15 text-[#FFB547] rounded text-xs font-semibold hover:bg-[#FFB547]/25 transition-colors">
                        <Play size={12} /> Start
                      </button>
                    )}
                    {wo.status === 'In Progress' && (
                      <button data-testid={`mfg-complete-${wo.id}`} onClick={(e) => { e.stopPropagation(); setCompleteData({ qty_produced: wo.qty_to_produce, qty_rejected: 0, scrap_reason: '' }); setShowCompleteModal(wo.id); }}
                        className="flex items-center gap-1 px-3 py-1 bg-[#00C9A7]/15 text-[#00C9A7] rounded text-xs font-semibold hover:bg-[#00C9A7]/25 transition-colors">
                        <CheckCircle size={12} /> Complete
                      </button>
                    )}
                    {(wo.status === 'Draft' || wo.status === 'In Progress') && (
                      <button onClick={(e) => { e.stopPropagation(); cancelWO(wo.id); }}
                        className="flex items-center gap-1 px-3 py-1 bg-[#FF4D6A]/15 text-[#FF4D6A] rounded text-xs font-semibold hover:bg-[#FF4D6A]/25 transition-colors">
                        <XCircle size={12} /> Cancel
                      </button>
                    )}
                  </div>
                </div>

                {expandedWO === wo.id && (
                  <div className="border-t border-[#1B2D42] p-4 space-y-3">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                      <div><span className="text-[#4A5B6E]">Planned Start:</span> <span className="text-[#E8EDF2] font-mono ml-1">{wo.planned_start || '--'}</span></div>
                      <div><span className="text-[#4A5B6E]">Planned End:</span> <span className="text-[#E8EDF2] font-mono ml-1">{wo.planned_end || '--'}</span></div>
                      <div><span className="text-[#4A5B6E]">Actual Start:</span> <span className="text-[#E8EDF2] font-mono ml-1">{wo.actual_start?.split('T')[0] || '--'}</span></div>
                      <div><span className="text-[#4A5B6E]">Actual End:</span> <span className="text-[#E8EDF2] font-mono ml-1">{wo.actual_end?.split('T')[0] || '--'}</span></div>
                    </div>
                    {wo.qty_produced > 0 && (
                      <div className="flex gap-4 text-xs">
                        <span className="text-[#00C9A7]">Produced: {wo.qty_produced}</span>
                        {wo.qty_rejected > 0 && <span className="text-[#FF4D6A]">Rejected: {wo.qty_rejected}</span>}
                      </div>
                    )}
                    {wo.bom_items && wo.bom_items.length > 0 && (
                      <div>
                        <p className="text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E] mb-2">Bill of Materials</p>
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="border-b border-[#1B2D42]">
                              <th className="pb-1 text-left text-[#4A5B6E]">Item</th>
                              <th className="pb-1 text-right text-[#4A5B6E]">Qty</th>
                              <th className="pb-1 text-right text-[#4A5B6E]">Rate</th>
                              <th className="pb-1 text-right text-[#4A5B6E]">Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {wo.bom_items.map((bom, i) => (
                              <tr key={i} className="border-b border-[#1B2D42]/30">
                                <td className="py-1 text-[#E8EDF2]">{bom.item_name || bom.item_code}</td>
                                <td className="py-1 text-right font-mono text-[#7A8BA0]">{bom.qty}</td>
                                <td className="py-1 text-right font-mono text-[#7A8BA0]">{formatINR(bom.rate)}</td>
                                <td className="py-1 text-right font-mono text-[#E8EDF2]">{formatINR(bom.qty * bom.rate)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
