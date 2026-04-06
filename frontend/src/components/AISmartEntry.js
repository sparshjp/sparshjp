import React, { useState, useRef, useEffect } from 'react';
import { Zap, Send, Loader2, X, Check, AlertCircle, Plus, Trash2, Sparkles } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Intent display config
const INTENT_CONFIG = {
  purchase_order: { label: 'Purchase Order', color: '#F59E0B' },
  sales_order: { label: 'Sales Order', color: '#10B981' },
  work_order: { label: 'Work Order', color: '#8B5CF6' },
  journal_entry: { label: 'Journal Entry', color: '#EC4899' },
  goods_receipt: { label: 'Goods Receipt (GRN)', color: '#F97316' },
  delivery_note: { label: 'Delivery Note', color: '#06B6D4' },
  crm_lead: { label: 'CRM Lead', color: '#3B82F6' },
};

// Field schemas per intent
const FIELD_SCHEMAS = {
  purchase_order: {
    simple: [
      { key: 'vendor', label: 'Vendor', type: 'strict_suggest', source: 'vendors', required: true },
      { key: 'cost_center', label: 'Cost Center', type: 'suggest', source: 'cost_centers', required: true },
      { key: 'delivery_date', label: 'Delivery Date', type: 'date' },
      { key: 'gst_rate', label: 'GST %', type: 'number', default: 18 },
      { key: 'payment_terms', label: 'Payment Terms', type: 'text' },
    ],
    items: true,
  },
  sales_order: {
    simple: [
      { key: 'customer', label: 'Customer', type: 'strict_suggest', source: 'customers', required: true },
      { key: 'cost_center', label: 'Cost Center', type: 'suggest', source: 'cost_centers', required: true },
      { key: 'delivery_date', label: 'Delivery Date', type: 'date' },
      { key: 'gst_rate', label: 'GST %', type: 'number', default: 18 },
      { key: 'payment_terms', label: 'Payment Terms', type: 'text' },
      { key: 'po_no', label: 'Customer PO #', type: 'text' },
    ],
    items: true,
  },
  work_order: {
    simple: [
      { key: 'production_item', label: 'FG Item Code', type: 'strict_suggest', source: 'items_code', required: true },
      { key: 'qty_to_produce', label: 'Qty to Produce', type: 'number', required: true },
      { key: 'cost_center', label: 'Cost Center', type: 'suggest', source: 'cost_centers', required: true },
      { key: 'planned_start', label: 'Planned Start', type: 'date' },
      { key: 'planned_end', label: 'Planned End', type: 'date' },
    ],
    items: false,
  },
  journal_entry: {
    simple: [
      { key: 'narration', label: 'Narration', type: 'text', required: true },
      { key: 'posting_date', label: 'Date', type: 'date' },
      { key: 'cost_center', label: 'Cost Center', type: 'suggest', source: 'cost_centers' },
    ],
    entries: true,
  },
  goods_receipt: {
    simple: [
      { key: 'po_id', label: 'Purchase Order', type: 'select_po', required: true },
    ],
  },
  delivery_note: {
    simple: [
      { key: 'so_id', label: 'Sales Order', type: 'select_so', required: true },
    ],
  },
  crm_lead: {
    simple: [
      { key: 'company', label: 'Company', type: 'text', required: true },
      { key: 'contact_name', label: 'Contact Name', type: 'text', required: true },
      { key: 'phone', label: 'Phone', type: 'text' },
      { key: 'email', label: 'Email', type: 'text' },
      { key: 'interest', label: 'Interest / Requirement', type: 'text' },
      { key: 'source', label: 'Source', type: 'text' },
      { key: 'est_value', label: 'Est. Value (INR)', type: 'number' },
    ],
  },
};

/* Strict dropdown — only allows values from the master list. No free-text. */
function StrictDropdown({ value, onChange, options, placeholder, invalid }) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const optList = (options || []).map(o => typeof o === 'string' ? o : o.code || o.name || '');
  const filtered = optList.filter(o => o.toLowerCase().includes(filter.toLowerCase()));
  const isValid = !value || optList.includes(value);

  return (
    <div ref={ref} className="relative">
      <div
        onClick={() => setOpen(!open)}
        className={`w-full bg-[#0D1B2A] border rounded px-2.5 py-1.5 text-xs cursor-pointer flex items-center justify-between ${!isValid || invalid ? 'border-red-400 text-red-400' : value ? 'border-[#00C9A7]/40 text-[#E8EDF2]' : 'border-[#1B2D42] text-[#4A5B6E]'}`}
      >
        <span className="truncate">{value || placeholder}</span>
        <svg className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </div>
      {open && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-[#152236] border border-[#1B2D42] rounded shadow-lg max-h-44 overflow-hidden flex flex-col">
          <input
            autoFocus
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Search..."
            className="w-full bg-[#0D1B2A] border-b border-[#1B2D42] px-2.5 py-1.5 text-xs text-[#E8EDF2] outline-none placeholder-[#4A5B6E]"
          />
          <div className="overflow-y-auto flex-1">
            {filtered.length === 0 ? (
              <p className="px-2.5 py-2 text-[10px] text-[#4A5B6E]">No match found. Create in Master Data first.</p>
            ) : filtered.map((o, i) => (
              <button key={i} onClick={() => { onChange(o); setOpen(false); setFilter(''); }}
                className={`w-full text-left px-2.5 py-1.5 text-xs hover:bg-[#00C9A7]/10 hover:text-[#00C9A7] transition-colors ${o === value ? 'text-[#00C9A7] bg-[#00C9A7]/5' : 'text-[#E8EDF2]'}`}>
                {o}
              </button>
            ))}
          </div>
        </div>
      )}
      {!isValid && value && <p className="text-[9px] text-red-400 mt-0.5">Not in master data</p>}
    </div>
  );
}

function SuggestInput({ value, onChange, suggestions, placeholder }) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filtered = (suggestions || []).filter(s => {
    const label = typeof s === 'string' ? s : s.code || s.name || '';
    return label.toLowerCase().includes((filter || value || '').toLowerCase());
  });

  return (
    <div ref={ref} className="relative">
      <input
        value={value || ''}
        onChange={e => { onChange(e.target.value); setFilter(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        placeholder={placeholder}
        className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2.5 py-1.5 text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] focus:ring-1 focus:ring-[#00C9A7]/20 outline-none"
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-[#152236] border border-[#1B2D42] rounded shadow-lg max-h-36 overflow-y-auto">
          {filtered.slice(0, 8).map((s, i) => {
            const label = typeof s === 'string' ? s : `${s.code} — ${s.name}`;
            const val = typeof s === 'string' ? s : s.code;
            return (
              <button key={i} onClick={() => { onChange(val); setOpen(false); }}
                className="w-full text-left px-2.5 py-1.5 text-xs text-[#E8EDF2] hover:bg-[#00C9A7]/10 hover:text-[#00C9A7] transition-colors">
                {label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}


/* ─── Smart Popup (shared between universal + module prompts) ─── */
export function SmartFormPopup({ parsed, masterData, onConfirm, onCancel, loading }) {
  const intent = parsed.intent;
  const config = INTENT_CONFIG[intent] || { label: intent, color: '#00C9A7' };
  const schema = FIELD_SCHEMAS[intent] || { simple: [] };

  const [formData, setFormData] = useState(() => {
    const ext = parsed.extracted || {};
    const data = { ...ext };
    (schema.simple || []).forEach(f => { if (f.default && !data[f.key]) data[f.key] = f.default; });
    return data;
  });

  const [items, setItems] = useState(() => parsed.extracted?.items || [{ item_code: '', item_name: '', qty: '', rate: '', uom: 'KG', amount: 0 }]);
  const [entries, setEntries] = useState(() => parsed.extracted?.entries || [{ account: '', debit: '', credit: '', description: '' }]);

  const missing = parsed.missing || [];
  const set = (key, val) => setFormData(prev => ({ ...prev, [key]: val }));

  const updateItem = (idx, key, val) => {
    setItems(prev => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], [key]: val };
      if (key === 'qty' || key === 'rate') {
        copy[idx].amount = (parseFloat(copy[idx].qty) || 0) * (parseFloat(copy[idx].rate) || 0);
      }
      return copy;
    });
  };
  const updateEntry = (idx, key, val) => setEntries(prev => { const c = [...prev]; c[idx] = { ...c[idx], [key]: val }; return c; });
  const addItem = () => setItems(prev => [...prev, { item_code: '', item_name: '', qty: '', rate: '', uom: 'KG', amount: 0 }]);
  const removeItem = (idx) => setItems(prev => prev.filter((_, i) => i !== idx));
  const addEntry = () => setEntries(prev => [...prev, { account: '', debit: '', credit: '', description: '' }]);
  const removeEntry = (idx) => setEntries(prev => prev.filter((_, i) => i !== idx));

  const getSuggestions = (source) => {
    if (!masterData) return [];
    if (source === 'vendors') return masterData.vendors || [];
    if (source === 'customers') return masterData.customers || [];
    if (source === 'cost_centers') return masterData.cost_centers || [];
    if (source === 'items_code') return (masterData.items || []).map(i => ({ code: i.code, name: i.name }));
    if (source === 'ledgers') return masterData.ledgers || [];
    return [];
  };

  const getStrictOptions = (source) => {
    if (!masterData) return [];
    if (source === 'vendors') return masterData.vendors || [];
    if (source === 'customers') return masterData.customers || [];
    if (source === 'items_code') return (masterData.items || []).map(i => i.code);
    return [];
  };

  const itemOptions = (masterData?.items || []).map(i => i.code);
  const itemSuggestions = (masterData?.items || []).map(i => ({ code: i.code, name: i.name, rate: i.rate }));

  const handleConfirm = () => {
    const payload = { ...formData };
    if (schema.items) payload.items = items.map(i => ({ ...i, qty: parseFloat(i.qty) || 0, rate: parseFloat(i.rate) || 0, amount: (parseFloat(i.qty) || 0) * (parseFloat(i.rate) || 0) }));
    if (schema.entries) payload.entries = entries.map(e => ({ ...e, debit: parseFloat(e.debit) || 0, credit: parseFloat(e.credit) || 0 }));
    onConfirm(intent, payload);
  };

  const subtotal = items.reduce((s, i) => s + ((parseFloat(i.qty) || 0) * (parseFloat(i.rate) || 0)), 0);
  const gstRate = parseFloat(formData.gst_rate) || 18;
  const gstAmount = subtotal * gstRate / 100;
  const grandTotal = subtotal + gstAmount;

  const totalDebit = entries.reduce((s, e) => s + (parseFloat(e.debit) || 0), 0);
  const totalCredit = entries.reduce((s, e) => s + (parseFloat(e.credit) || 0), 0);
  const jeBalanced = Math.abs(totalDebit - totalCredit) < 0.01;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4" data-testid="ai-smart-popup">
      <div className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1B2D42]">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full animate-pulse" style={{ background: config.color }} />
            <span className="text-sm font-bold text-[#E8EDF2]">{config.label}</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: config.color + '20', color: config.color }}>
              {Math.round((parsed.confidence || 0) * 100)}% match
            </span>
          </div>
          <button onClick={onCancel} className="p-1.5 hover:bg-[#152236] rounded-lg text-[#7A8BA0]"><X className="w-4 h-4" /></button>
        </div>

        {/* AI Summary */}
        <div className="px-5 py-2.5 bg-[#152236]/50 border-b border-[#1B2D42] flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-[#00C9A7] flex-shrink-0" />
          <p className="text-xs text-[#7A8BA0]">{parsed.summary}</p>
        </div>

        {/* Form Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {/* Simple fields */}
          <div className="grid grid-cols-2 gap-3">
            {(schema.simple || []).map(f => {
              const isMissing = missing.includes(f.key);
              const isFilled = formData[f.key] !== undefined && formData[f.key] !== '' && formData[f.key] !== null;
              return (
                <div key={f.key} className="space-y-1">
                  <label className="text-[10px] font-medium tracking-wider uppercase flex items-center gap-1.5" style={{ color: isMissing && !isFilled ? '#F59E0B' : '#7A8BA0' }}>
                    {f.label} {f.required && <span className="text-red-400">*</span>}
                    {isFilled && !isMissing && <Check className="w-3 h-3 text-[#00C9A7]" />}
                    {isMissing && !isFilled && <AlertCircle className="w-3 h-3 text-amber-400" />}
                  </label>
                  {f.type === 'strict_suggest' ? (
                    <StrictDropdown value={formData[f.key] || ''} onChange={v => set(f.key, v)} options={getStrictOptions(f.source)} placeholder={`Select ${f.label}`} />
                  ) : f.type === 'suggest' ? (
                    <SuggestInput value={formData[f.key] || ''} onChange={v => set(f.key, v)} suggestions={getSuggestions(f.source)} placeholder={`Select ${f.label.toLowerCase()}`} />
                  ) : f.type === 'select_po' ? (
                    <select value={formData[f.key] || ''} onChange={e => set(f.key, e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2.5 py-1.5 text-xs text-[#E8EDF2] focus:border-[#00C9A7] outline-none">
                      <option value="">Select PO</option>
                      {(masterData?.pending_pos || []).map(p => <option key={p.id} value={p.id}>{p.number} — {p.vendor}</option>)}
                    </select>
                  ) : f.type === 'select_so' ? (
                    <select value={formData[f.key] || ''} onChange={e => set(f.key, e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2.5 py-1.5 text-xs text-[#E8EDF2] focus:border-[#00C9A7] outline-none">
                      <option value="">Select SO</option>
                      {(masterData?.pending_sos || []).map(s => <option key={s.id} value={s.id}>{s.number} — {s.customer}</option>)}
                    </select>
                  ) : (
                    <input
                      type={f.type}
                      value={formData[f.key] ?? ''}
                      onChange={e => set(f.key, e.target.value)}
                      className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2.5 py-1.5 text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] focus:ring-1 focus:ring-[#00C9A7]/20 outline-none"
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Items table — item_code uses strict dropdown */}
          {schema.items && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0]">Line Items</p>
                <button onClick={addItem} className="flex items-center gap-1 text-[10px] text-[#00C9A7] hover:text-[#00B396]"><Plus className="w-3 h-3" /> Add Item</button>
              </div>
              <div className="border border-[#1B2D42] rounded overflow-hidden">
                <table className="w-full text-xs">
                  <thead><tr className="bg-[#152236] text-[#7A8BA0]">
                    <th className="px-2 py-1.5 text-left font-medium">Item</th>
                    <th className="px-2 py-1.5 text-right font-medium w-20">Qty</th>
                    <th className="px-2 py-1.5 text-left font-medium w-14">UOM</th>
                    <th className="px-2 py-1.5 text-right font-medium w-24">Rate</th>
                    <th className="px-2 py-1.5 text-right font-medium w-28">Amount</th>
                    <th className="w-8"></th>
                  </tr></thead>
                  <tbody>
                    {items.map((item, idx) => (
                      <tr key={idx} className="border-t border-[#1B2D42]/50">
                        <td className="px-1 py-1">
                          <StrictDropdown
                            value={item.item_code || ''}
                            onChange={v => {
                              const match = itemSuggestions.find(s => s.code === v);
                              updateItem(idx, 'item_code', v);
                              if (match) {
                                updateItem(idx, 'item_name', match.name);
                                if (!item.rate) updateItem(idx, 'rate', match.rate);
                              }
                            }}
                            options={itemOptions}
                            placeholder="Select item"
                          />
                        </td>
                        <td className="px-1 py-1">
                          <input type="number" value={item.qty || ''} onChange={e => updateItem(idx, 'qty', e.target.value)}
                            className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-right text-[#E8EDF2] outline-none focus:border-[#00C9A7]" />
                        </td>
                        <td className="px-1 py-1">
                          <input value={item.uom || 'KG'} onChange={e => updateItem(idx, 'uom', e.target.value)}
                            className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]" />
                        </td>
                        <td className="px-1 py-1">
                          <input type="number" value={item.rate || ''} onChange={e => updateItem(idx, 'rate', e.target.value)}
                            className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-right text-[#E8EDF2] outline-none focus:border-[#00C9A7]" />
                        </td>
                        <td className="px-2 py-1 text-right text-[#E8EDF2] font-mono">{((parseFloat(item.qty) || 0) * (parseFloat(item.rate) || 0)).toLocaleString('en-IN')}</td>
                        <td className="px-1">{items.length > 1 && <button onClick={() => removeItem(idx)} className="text-red-400/60 hover:text-red-400"><Trash2 className="w-3 h-3" /></button>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex justify-end">
                <div className="w-64 space-y-1 text-xs">
                  <div className="flex justify-between text-[#7A8BA0]"><span>Subtotal</span><span className="font-mono">{subtotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span></div>
                  <div className="flex justify-between text-[#7A8BA0]"><span>GST ({gstRate}%)</span><span className="font-mono">{gstAmount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span></div>
                  <div className="flex justify-between text-[#E8EDF2] font-bold border-t border-[#1B2D42] pt-1"><span>Grand Total</span><span className="font-mono">{grandTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span></div>
                </div>
              </div>
            </div>
          )}

          {/* Journal Entries table */}
          {schema.entries && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0]">Journal Lines</p>
                <button onClick={addEntry} className="flex items-center gap-1 text-[10px] text-[#00C9A7] hover:text-[#00B396]"><Plus className="w-3 h-3" /> Add Line</button>
              </div>
              <div className="border border-[#1B2D42] rounded overflow-hidden">
                <table className="w-full text-xs">
                  <thead><tr className="bg-[#152236] text-[#7A8BA0]">
                    <th className="px-2 py-1.5 text-left font-medium">Account</th>
                    <th className="px-2 py-1.5 text-right font-medium w-28">Debit</th>
                    <th className="px-2 py-1.5 text-right font-medium w-28">Credit</th>
                    <th className="px-2 py-1.5 text-left font-medium w-32">Description</th>
                    <th className="w-8"></th>
                  </tr></thead>
                  <tbody>
                    {entries.map((e, idx) => (
                      <tr key={idx} className="border-t border-[#1B2D42]/50">
                        <td className="px-1 py-1"><SuggestInput value={e.account || ''} onChange={v => updateEntry(idx, 'account', v)} suggestions={masterData?.ledgers || []} placeholder="Account" /></td>
                        <td className="px-1 py-1"><input type="number" value={e.debit || ''} onChange={ev => updateEntry(idx, 'debit', ev.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-right text-[#E8EDF2] outline-none focus:border-[#00C9A7]" /></td>
                        <td className="px-1 py-1"><input type="number" value={e.credit || ''} onChange={ev => updateEntry(idx, 'credit', ev.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-right text-[#E8EDF2] outline-none focus:border-[#00C9A7]" /></td>
                        <td className="px-1 py-1"><input value={e.description || ''} onChange={ev => updateEntry(idx, 'description', ev.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]" placeholder="Desc" /></td>
                        <td className="px-1">{entries.length > 1 && <button onClick={() => removeEntry(idx)} className="text-red-400/60 hover:text-red-400"><Trash2 className="w-3 h-3" /></button>}</td>
                      </tr>
                    ))}
                    <tr className="border-t border-[#1B2D42] bg-[#152236]/50">
                      <td className="px-2 py-1.5 text-right font-medium text-[#7A8BA0]">Total</td>
                      <td className="px-2 py-1.5 text-right font-mono text-[#E8EDF2]">{totalDebit.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                      <td className="px-2 py-1.5 text-right font-mono text-[#E8EDF2]">{totalCredit.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                      <td colSpan={2} className="px-2 py-1.5">
                        {jeBalanced ? <span className="text-[#00C9A7] text-[10px] font-medium">Balanced</span> : <span className="text-red-400 text-[10px] font-medium">Diff: {(totalDebit - totalCredit).toLocaleString('en-IN')}</span>}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3.5 border-t border-[#1B2D42] bg-[#152236]/30">
          <div className="flex items-center gap-2 text-[10px] text-[#4A5B6E]">
            {missing.length > 0 && <AlertCircle className="w-3.5 h-3.5 text-amber-400" />}
            {missing.length > 0 ? <span className="text-amber-400">{missing.length} field{missing.length > 1 ? 's' : ''} need your input</span> : <span className="text-[#00C9A7]">All fields parsed from prompt</span>}
          </div>
          <div className="flex gap-2">
            <button onClick={onCancel} data-testid="ai-popup-cancel" className="px-4 py-2 text-xs font-medium text-[#7A8BA0] hover:text-[#E8EDF2] border border-[#1B2D42] rounded-lg hover:bg-[#152236] transition-colors">Cancel</button>
            <button onClick={handleConfirm} disabled={loading} data-testid="ai-popup-confirm"
              className="px-5 py-2 text-xs font-bold bg-[#00C9A7] text-[#0D1B2A] rounded-lg hover:bg-[#00B396] disabled:opacity-50 transition-colors flex items-center gap-2">
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
              Confirm & Create
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


/* ─── Module-level AI Prompt Bar (inline, replaces old forms) ─── */
export function ModuleAIPrompt({ placeholder, defaultIntent, onCreated }) {
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsed, setParsed] = useState(null);
  const [masterData, setMasterData] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleParse = async () => {
    if (!prompt.trim() || parsing) return;
    setParsing(true);
    try {
      const res = await fetch(`${API}/api/ai/parse-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Parse failed');
      const data = await res.json();
      setParsed(data);
      setMasterData(data.master_data || {});
    } catch (e) {
      showToast(e.message, 'error');
    }
    setParsing(false);
  };

  const handleConfirm = async (intent, payload) => {
    setSubmitting(true);
    try {
      let url = '', body = payload;

      switch (intent) {
        case 'purchase_order':
          url = `${API}/api/purchase/orders`; break;
        case 'sales_order':
          url = `${API}/api/selling/sales-orders`; break;
        case 'work_order':
          url = `${API}/api/manufacturing/work-orders`;
          body = { ...payload, bom_items: payload.bom_items || [] }; break;
        case 'journal_entry':
          url = `${API}/api/journal-entries/manual`;
          body = { posting_date: payload.posting_date || new Date().toISOString().split('T')[0], cost_center: payload.cost_center || 'General', journal_entries: payload.entries, narration: payload.narration }; break;
        case 'goods_receipt':
          url = `${API}/api/purchase/grn/from-po/${payload.po_id}`;
          body = {}; break;
        case 'delivery_note':
          url = `${API}/api/selling/delivery-notes/from-so/${payload.so_id}`;
          body = {}; break;
        case 'crm_lead':
          url = `${API}/api/crm/leads`;
          body = { lead_name: payload.contact_name, company_name: payload.company, ...payload }; break;
        default: throw new Error(`Unsupported intent: ${intent}`);
      }

      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail || JSON.stringify(err)); }
      const result = await res.json();
      const docId = result.po_number || result.so_number || result.wo_number || result.grn_number || result.id || 'Created';
      showToast(`${INTENT_CONFIG[intent]?.label || intent} ${docId} created!`, 'success');
      setParsed(null);
      setPrompt('');
      if (onCreated) onCreated();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setSubmitting(false);
  };

  return (
    <>
      {/* Inline prompt bar */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-3" data-testid="module-ai-prompt">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#00C9A7]/10 border border-[#00C9A7]/20 rounded-lg">
            <Zap className="w-3.5 h-3.5 text-[#00C9A7]" />
            <span className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase">AI</span>
          </div>
          <input
            data-testid="module-ai-input"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleParse()}
            placeholder={placeholder}
            className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] outline-none focus:border-[#00C9A7] transition-colors"
            disabled={parsing}
          />
          <button
            data-testid="module-ai-go"
            onClick={handleParse}
            disabled={parsing || !prompt.trim()}
            className="px-4 py-2 bg-[#00C9A7] text-[#0D1B2A] rounded-lg font-bold text-xs hover:bg-[#00B396] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
          >
            {parsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            {parsing ? 'Parsing...' : 'Go'}
          </button>
        </div>
      </div>

      {/* Smart Popup */}
      {parsed && <SmartFormPopup parsed={parsed} masterData={masterData} onConfirm={handleConfirm} onCancel={() => setParsed(null)} loading={submitting} />}

      {/* Inline toast */}
      {toast && (
        <div className={`fixed top-5 right-5 z-[200] px-4 py-3 rounded-xl shadow-lg text-sm font-medium flex items-center gap-2 ${
          toast.type === 'success' ? 'bg-[#00C9A7] text-[#0D1B2A]' : 'bg-red-500 text-white'
        }`} data-testid="module-ai-toast">
          {toast.type === 'success' ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {toast.msg}
        </div>
      )}
    </>
  );
}
