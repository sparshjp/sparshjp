import React, { useState, useEffect } from 'react';
import { Package, Plus, Search, Check, Loader2, X, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;
const GST_RATES = [0, 0.25, 3, 5, 12, 18, 28];
const UOMS = ['KG', 'LTR', 'MT', 'NOS', 'PCS', 'BAG', 'BOX', 'SET', 'SQM', 'CUM', 'KM', 'PAIR', 'ROLL', 'DRUM', 'BTL'];
const VALUATION_METHODS = ['FIFO', 'Weighted Average', 'LIFO', 'Standard Cost'];

function Input({ label, value, onChange, placeholder, required, type = 'text', disabled, className = '' }) {
  return (
    <div className={className}>
      <label className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0] mb-1.5 block">
        {label}{required && <span className="text-[#FF4D6A] ml-0.5">*</span>}
      </label>
      <input type={type} value={value || ''} onChange={e => onChange(e.target.value)} placeholder={placeholder} disabled={disabled}
        className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] outline-none disabled:opacity-50" />
    </div>
  );
}

function Select({ label, value, onChange, options, placeholder }) {
  return (
    <div>
      <label className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0] mb-1.5 block">{label}</label>
      <select value={value || ''} onChange={e => onChange(e.target.value)}
        className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] outline-none">
        <option value="">{placeholder || 'Select...'}</option>
        {options.map(o => <option key={typeof o === 'string' ? o : o.value} value={typeof o === 'string' ? o : o.value}>{typeof o === 'string' ? o : o.label}</option>)}
      </select>
    </div>
  );
}

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [form, setForm] = useState({
    item_code: '', item_name: '', hsn_sac: '', gst_rate: '18',
    uom: 'KG', item_group: '', description: '',
    valuation_method: 'FIFO', valuation_rate: '', opening_stock: '0',
    reorder_level: '', reorder_qty: '', shelf_life: '',
    is_service: false,
  });

  useEffect(() => { loadItems(); }, []);

  const loadItems = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/stock/items`);
      setItems(await r.json());
    } catch { toast.error('Failed to load items'); }
    setLoading(false);
  };

  const suggestHSN = async () => {
    if (!form.item_name && !form.description) { toast.error('Enter item name or description first'); return; }
    setSuggesting(true);
    try {
      const r = await fetch(`${API}/api/gst/suggest-hsn`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: form.description || form.item_name, item_name: form.item_name }),
      });
      const data = await r.json();
      if (data.hsn_sac) {
        setForm(f => ({...f, hsn_sac: data.hsn_sac, gst_rate: String(data.gst_rate || 18), is_service: data.type === 'SAC'}));
        toast.success(`AI suggested: ${data.type} ${data.hsn_sac} (${data.gst_rate}%) — ${data.description || ''}`);
      } else { toast.error('Could not determine HSN/SAC'); }
    } catch { toast.error('HSN suggest failed'); }
    setSuggesting(false);
  };

  const handleSave = async () => {
    if (!form.item_name) { toast.error('Item name is required'); return; }
    if (!form.item_code) { toast.error('Item code is required'); return; }
    setSaving(true);
    try {
      const payload = {
        ...form,
        gst_rate: parseFloat(form.gst_rate) || 18,
        valuation_rate: parseFloat(form.valuation_rate) || 0,
        current_stock: parseFloat(form.opening_stock) || 0,
        reorder_level: parseFloat(form.reorder_level) || 0,
      };
      const r = await fetch(`${API}/api/stock/items`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Failed'); }
      toast.success(`Item "${form.item_name}" created`);
      setShowForm(false);
      setForm({ item_code: '', item_name: '', hsn_sac: '', gst_rate: '18', uom: 'KG', item_group: '', description: '', valuation_method: 'FIFO', valuation_rate: '', opening_stock: '0', reorder_level: '', reorder_qty: '', shelf_life: '', is_service: false });
      loadItems();
    } catch (e) { toast.error(e.message); }
    setSaving(false);
  };

  const filtered = items.filter(i => !search || i.item_name?.toLowerCase().includes(search.toLowerCase()) || i.item_code?.toLowerCase().includes(search.toLowerCase()) || i.hsn_sac?.includes(search));

  return (
    <div className="space-y-5" data-testid="items-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Package className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">Items</h1>
            <p className="text-[#4A5B6E] text-sm">{items.length} items in master data</p>
          </div>
        </div>
        <button data-testid="add-item-btn" onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors">
          <Plus className="w-4 h-4" /> Add Item
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#4A5B6E]" />
        <input data-testid="item-search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name, code, or HSN..."
          className="w-full pl-10 pr-4 py-2.5 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] placeholder-[#4A5B6E] outline-none focus:border-[#00C9A7]" />
      </div>

      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        <table className="w-full text-sm" data-testid="items-table">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2.5 px-4 text-left">Code</th>
            <th className="py-2.5 px-4 text-left">Name</th>
            <th className="py-2.5 px-4 text-left">HSN/SAC</th>
            <th className="py-2.5 px-4 text-right">GST %</th>
            <th className="py-2.5 px-4 text-left">UOM</th>
            <th className="py-2.5 px-4 text-right">Stock</th>
            <th className="py-2.5 px-4 text-right">Rate</th>
          </tr></thead>
          <tbody>
            {loading ? <tr><td colSpan={7} className="py-8 text-center text-[#4A5B6E]">Loading...</td></tr> :
              filtered.length === 0 ? <tr><td colSpan={7} className="py-8 text-center text-[#4A5B6E]">No items found</td></tr> :
              filtered.map((it, i) => (
                <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20" data-testid="item-row">
                  <td className="py-2.5 px-4 font-mono text-[#00C9A7] text-xs font-bold">{it.item_code}</td>
                  <td className="py-2.5 px-4 text-xs text-[#E8EDF2]">{it.item_name}</td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#7A8BA0]">{it.hsn_sac || it.hsn || '—'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-[#7A8BA0]">{it.gst_rate || 18}%</td>
                  <td className="py-2.5 px-4 text-xs text-[#7A8BA0]">{it.uom || 'KG'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-[#E8EDF2]">{it.current_stock || 0}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-[#7A8BA0]">{it.valuation_rate || '—'}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-[70] flex items-start justify-center pt-8 overflow-y-auto">
          <div className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl w-full max-w-3xl mb-8" data-testid="item-form-modal">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#1B2D42]">
              <h2 className="text-lg font-bold text-[#E8EDF2]">New Item</h2>
              <button onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X className="w-5 h-5" /></button>
            </div>
            <div className="px-6 py-5 space-y-5">
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3">Identification</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Item Code" value={form.item_code} onChange={v => setForm({...form, item_code: v.toUpperCase()})} placeholder="e.g., RM-BPA" required />
                  <Input label="Item Name" value={form.item_name} onChange={v => setForm({...form, item_name: v})} placeholder="Full item name" required />
                  <Input label="Description" value={form.description} onChange={v => setForm({...form, description: v})} placeholder="Detailed description for AI HSN lookup" className="md:col-span-2" />
                  <Input label="Item Group" value={form.item_group} onChange={v => setForm({...form, item_group: v})} placeholder="e.g., Raw Material, Finished Goods" />
                </div>
              </div>

              {/* HSN/SAC + GST with AI suggest */}
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3">GST Classification</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0] mb-1.5 block">HSN/SAC Code<span className="text-[#FF4D6A] ml-0.5">*</span></label>
                    <div className="flex gap-2">
                      <input value={form.hsn_sac || ''} onChange={e => setForm({...form, hsn_sac: e.target.value})} placeholder="e.g., 2907"
                        className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] outline-none font-mono" />
                      <button data-testid="ai-suggest-hsn-btn" onClick={suggestHSN} disabled={suggesting}
                        className="flex items-center gap-1.5 px-3 py-2 bg-[#00C9A7]/10 border border-[#00C9A7]/20 rounded-lg text-xs text-[#00C9A7] hover:bg-[#00C9A7]/20 transition-colors disabled:opacity-50" title="AI Suggest HSN/SAC">
                        {suggesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />} AI
                      </button>
                    </div>
                  </div>
                  <Select label="GST Rate %" value={form.gst_rate} onChange={v => setForm({...form, gst_rate: v})} options={GST_RATES.map(r => ({value: String(r), label: `${r}%`}))} />
                  <Select label="UOM" value={form.uom} onChange={v => setForm({...form, uom: v})} options={UOMS} />
                </div>
              </div>

              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3">Inventory & Valuation</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Select label="Valuation Method" value={form.valuation_method} onChange={v => setForm({...form, valuation_method: v})} options={VALUATION_METHODS} />
                  <Input label="Valuation Rate (INR)" value={form.valuation_rate} onChange={v => setForm({...form, valuation_rate: v})} placeholder="0.00" type="number" />
                  <Input label="Opening Stock" value={form.opening_stock} onChange={v => setForm({...form, opening_stock: v})} placeholder="0" type="number" />
                  <Input label="Reorder Level" value={form.reorder_level} onChange={v => setForm({...form, reorder_level: v})} placeholder="Min stock" type="number" />
                  <Input label="Reorder Qty" value={form.reorder_qty} onChange={v => setForm({...form, reorder_qty: v})} placeholder="Order qty" type="number" />
                  <Input label="Shelf Life (days)" value={form.shelf_life} onChange={v => setForm({...form, shelf_life: v})} placeholder="0" type="number" />
                </div>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[#1B2D42]">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-[#7A8BA0] hover:text-[#E8EDF2]">Cancel</button>
              <button data-testid="save-item-btn" onClick={handleSave} disabled={saving}
                className="flex items-center gap-2 px-5 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors disabled:opacity-50">
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />} Save Item
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
