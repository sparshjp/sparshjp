import React, { useState, useEffect } from 'react';
import { Factory, Plus, Play, CheckCircle, XCircle, ChevronDown, ChevronRight, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(num) {
  if (!num && num !== 0) return '--';
  return new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num);
}

export default function ManufacturingModule() {
  const [workOrders, setWorkOrders] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [expandedWO, setExpandedWO] = useState(null);
  const [completeData, setCompleteData] = useState({ qty_produced: 0, qty_rejected: 0, scrap_reason: '' });
  const [showCompleteModal, setShowCompleteModal] = useState(null);
  const [formData, setFormData] = useState({
    production_item: '',
    production_item_name: '',
    qty_to_produce: 1,
    additional_costs: 0,
    planned_start: new Date().toISOString().split('T')[0],
    planned_end: '',
    cost_center: 'Manufacturing',
    bom_items: [{ item_code: '', item_name: '', qty: 0, rate: 0 }]
  });

  useEffect(() => { fetchWorkOrders(); }, []);

  async function fetchWorkOrders() {
    try {
      setLoading(true);
      const r = await fetch(`${API}/api/manufacturing/work-orders`);
      if (r.ok) setWorkOrders(await r.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  function addBomRow() {
    setFormData({ ...formData, bom_items: [...formData.bom_items, { item_code: '', item_name: '', qty: 0, rate: 0 }] });
  }

  function removeBomRow(idx) {
    setFormData({ ...formData, bom_items: formData.bom_items.filter((_, i) => i !== idx) });
  }

  function updateBomRow(idx, field, value) {
    const items = [...formData.bom_items];
    items[idx][field] = ['qty', 'rate'].includes(field) ? parseFloat(value) || 0 : value;
    setFormData({ ...formData, bom_items: items });
  }

  const totalRMCost = formData.bom_items.reduce((s, i) => s + i.qty * i.rate, 0);

  async function createWorkOrder() {
    if (!formData.production_item) { toast.error('Production item is required'); return; }
    try {
      const r = await fetch(`${API}/api/manufacturing/work-orders`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (r.ok) {
        toast.success('Work Order created');
        setShowForm(false);
        setFormData({ production_item: '', production_item_name: '', qty_to_produce: 1, additional_costs: 0,
          planned_start: new Date().toISOString().split('T')[0], planned_end: '', cost_center: 'Manufacturing',
          bom_items: [{ item_code: '', item_name: '', qty: 0, rate: 0 }] });
        fetchWorkOrders();
      } else {
        const err = await r.json();
        toast.error(err.detail || 'Failed to create Work Order');
      }
    } catch (e) { toast.error('Network error'); }
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
        <button data-testid="mfg-new-wo-btn" onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-semibold transition-colors">
          <Plus size={16} /> New Work Order
        </button>
      </div>

      {/* Create WO Form */}
      {showForm && (
        <div className="bg-[#152236] border border-[#00C9A7]/30 rounded-lg p-6 space-y-4" data-testid="mfg-wo-form">
          <h2 className="text-base font-bold text-[#E8EDF2]">Create Work Order</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Production Item (Code)</label>
              <input data-testid="mfg-prod-item" type="text" value={formData.production_item}
                onChange={(e) => setFormData({ ...formData, production_item: e.target.value })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] placeholder:text-[#4A5B6E]" placeholder="e.g. FG-CHIP-001" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Item Name</label>
              <input type="text" value={formData.production_item_name}
                onChange={(e) => setFormData({ ...formData, production_item_name: e.target.value })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] placeholder:text-[#4A5B6E]" placeholder="e.g. NanoChip X1" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Qty to Produce</label>
              <input data-testid="mfg-qty" type="number" value={formData.qty_to_produce}
                onChange={(e) => setFormData({ ...formData, qty_to_produce: parseFloat(e.target.value) || 0 })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Planned Start</label>
              <input type="date" value={formData.planned_start}
                onChange={(e) => setFormData({ ...formData, planned_start: e.target.value })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Planned End</label>
              <input type="date" value={formData.planned_end}
                onChange={(e) => setFormData({ ...formData, planned_end: e.target.value })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Additional Costs</label>
              <input type="number" value={formData.additional_costs}
                onChange={(e) => setFormData({ ...formData, additional_costs: parseFloat(e.target.value) || 0 })}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
          </div>

          {/* BOM */}
          <div className="border-t border-[#1B2D42] pt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-[#E8EDF2] text-sm">Bill of Materials (BOM)</h3>
              <button onClick={addBomRow} className="text-xs text-[#00C9A7] hover:text-[#00B396] font-medium flex items-center gap-1">
                <Plus size={14} /><span>Add Row</span>
              </button>
            </div>
            <table className="w-full text-sm" data-testid="mfg-bom-table">
              <thead>
                <tr className="border-b border-[#1B2D42]">
                  <th className="pb-2 text-left text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Item Code</th>
                  <th className="pb-2 text-left text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Item Name</th>
                  <th className="pb-2 text-right text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Qty</th>
                  <th className="pb-2 text-right text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Rate</th>
                  <th className="pb-2 text-right text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Amount</th>
                  <th className="pb-2 w-8"></th>
                </tr>
              </thead>
              <tbody>
                {formData.bom_items.map((item, idx) => (
                  <tr key={idx} className="border-b border-[#1B2D42]/30">
                    <td className="py-2 pr-2"><input type="text" value={item.item_code} onChange={(e) => updateBomRow(idx, 'item_code', e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="RM-001" /></td>
                    <td className="py-2 pr-2"><input type="text" value={item.item_name} onChange={(e) => updateBomRow(idx, 'item_name', e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="Silicon Wafer" /></td>
                    <td className="py-2 pr-2"><input type="number" value={item.qty || ''} onChange={(e) => updateBomRow(idx, 'qty', e.target.value)} className="w-24 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm font-mono text-right text-[#E8EDF2] focus:border-[#00C9A7]" /></td>
                    <td className="py-2 pr-2"><input type="number" value={item.rate || ''} onChange={(e) => updateBomRow(idx, 'rate', e.target.value)} className="w-28 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm font-mono text-right text-[#E8EDF2] focus:border-[#00C9A7]" /></td>
                    <td className="py-2 pr-2 text-right font-mono text-sm text-[#7A8BA0]">{formatINR(item.qty * item.rate)}</td>
                    <td className="py-2"><button onClick={() => removeBomRow(idx)} className="p-1 text-[#FF4D6A] hover:bg-[#FF4D6A]/10 rounded"><Trash2 size={14} /></button></td>
                  </tr>
                ))}
                <tr className="border-t-2 border-[#00C9A7]/30">
                  <td colSpan={4} className="py-3 font-semibold text-[#E8EDF2] text-right">Total RM Cost</td>
                  <td className="py-3 text-right font-mono font-bold text-[#00C9A7]">{formatINR(totalRMCost)}</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="flex gap-3 pt-2">
            <button data-testid="mfg-create-wo-btn" onClick={createWorkOrder}
              className="flex items-center gap-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] px-5 py-2 rounded-lg text-sm font-semibold transition-colors">
              <Factory size={14} /> Create Work Order
            </button>
            <button onClick={() => setShowForm(false)} className="bg-[#1B2D42] hover:bg-[#152236] text-[#7A8BA0] px-5 py-2 rounded-lg text-sm font-medium transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

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
