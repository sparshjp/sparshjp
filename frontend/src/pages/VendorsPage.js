import React, { useState, useEffect, useCallback } from 'react';
import { Building, Plus, Search, Check, Loader2, X, MapPin, FileText } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;
const STATES = [];
const CONSTITUTIONS = ['Private Limited Company', 'Public Limited Company', 'LLP', 'Partnership Firm', 'Sole Proprietorship', 'HUF', 'Trust', 'Society', 'Government', 'Foreign Company', 'Casual Taxable Person', 'SEZ Unit/Developer'];
const PAYMENT_TERMS = ['Advance', 'Net 15', 'Net 30', 'Net 45', 'Net 60', 'Net 90', 'LC 30 days', 'LC 60 days', 'LC 90 days', 'Against Delivery'];

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

function Select({ label, value, onChange, options, placeholder, required }) {
  return (
    <div>
      <label className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0] mb-1.5 block">
        {label}{required && <span className="text-[#FF4D6A] ml-0.5">*</span>}
      </label>
      <select value={value || ''} onChange={e => onChange(e.target.value)}
        className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] outline-none">
        <option value="">{placeholder || 'Select...'}</option>
        {options.map(o => <option key={typeof o === 'string' ? o : o.value} value={typeof o === 'string' ? o : o.value}>{typeof o === 'string' ? o : o.label}</option>)}
      </select>
    </div>
  );
}

export default function VendorsPage() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [states, setStates] = useState([]);
  const [form, setForm] = useState({
    entity_type: 'vendor', name: '', legal_name: '', gstin: '', pan: '',
    constitution: '', status: 'Active', address: '', city: '', state: '',
    pin_code: '', country: 'India', contact: '', email: '', phone: '',
    payment_terms: 'Net 30', bank_name: '', bank_account: '', ifsc: '', msme_reg: '',
  });

  useEffect(() => {
    loadVendors();
    fetch(`${API}/api/gst/states`).then(r => r.json()).then(s => setStates(s)).catch(() => {});
  }, []);

  const loadVendors = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/entities?entity_type=vendor`);
      setVendors(await r.json());
    } catch { toast.error('Failed to load vendors'); }
    setLoading(false);
  };

  const handleSave = async () => {
    if (!form.name) { toast.error('Vendor name is required'); return; }
    setSaving(true);
    try {
      const r = await fetch(`${API}/api/entities`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Failed'); }
      const data = await r.json();
      toast.success(`Vendor "${data.name}" created`);
      if (data.gstin_valid) toast.info(`GSTIN validated: ${data.state || ''} | ${data.constitution || ''}`);
      setShowForm(false);
      setForm({ entity_type: 'vendor', name: '', legal_name: '', gstin: '', pan: '', constitution: '', status: 'Active', address: '', city: '', state: '', pin_code: '', country: 'India', contact: '', email: '', phone: '', payment_terms: 'Net 30', bank_name: '', bank_account: '', ifsc: '', msme_reg: '' });
      loadVendors();
    } catch (e) { toast.error(e.message); }
    setSaving(false);
  };

  const filtered = vendors.filter(v => !search || v.name?.toLowerCase().includes(search.toLowerCase()) || v.gstin?.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-5" data-testid="vendors-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Building className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">Vendors</h1>
            <p className="text-[#4A5B6E] text-sm">{vendors.length} vendors in master data</p>
          </div>
        </div>
        <button data-testid="add-vendor-btn" onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors">
          <Plus className="w-4 h-4" /> Add Vendor
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#4A5B6E]" />
        <input data-testid="vendor-search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search vendors by name or GSTIN..."
          className="w-full pl-10 pr-4 py-2.5 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] placeholder-[#4A5B6E] outline-none focus:border-[#00C9A7]" />
      </div>

      {/* Vendor table */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        <table className="w-full text-sm" data-testid="vendors-table">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2.5 px-4 text-left">Name</th>
            <th className="py-2.5 px-4 text-left">GSTIN</th>
            <th className="py-2.5 px-4 text-left">PAN</th>
            <th className="py-2.5 px-4 text-left">State</th>
            <th className="py-2.5 px-4 text-left">Payment Terms</th>
            <th className="py-2.5 px-4 text-left">Status</th>
          </tr></thead>
          <tbody>
            {loading ? <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">Loading...</td></tr> :
              filtered.length === 0 ? <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No vendors found</td></tr> :
              filtered.map((v, i) => (
                <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20" data-testid="vendor-row">
                  <td className="py-2.5 px-4">
                    <p className="text-[#E8EDF2] font-medium text-xs">{v.name}</p>
                    {v.legal_name && v.legal_name !== v.name && <p className="text-[10px] text-[#4A5B6E]">{v.legal_name}</p>}
                  </td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#7A8BA0]">{v.gstin || '—'}</td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#7A8BA0]">{v.pan || '—'}</td>
                  <td className="py-2.5 px-4 text-xs text-[#7A8BA0]">{v.state || v.state_name || '—'}</td>
                  <td className="py-2.5 px-4 text-xs text-[#7A8BA0]">{v.payment_terms || '—'}</td>
                  <td className="py-2.5 px-4"><span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{v.status || 'Active'}</span></td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Add Vendor Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-[70] flex items-start justify-center pt-8 overflow-y-auto">
          <div className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl w-full max-w-3xl mb-8" data-testid="vendor-form-modal">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#1B2D42]">
              <h2 className="text-lg font-bold text-[#E8EDF2]">New Vendor</h2>
              <button onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X className="w-5 h-5" /></button>
            </div>
            <div className="px-6 py-5 space-y-5">
              {/* Identity */}
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3 flex items-center gap-2"><Building className="w-3.5 h-3.5" /> Identity</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Vendor Name" value={form.name} onChange={v => setForm({...form, name: v})} placeholder="e.g., BASF India Pvt. Ltd." required />
                  <Input label="Legal Name (as per PAN)" value={form.legal_name} onChange={v => setForm({...form, legal_name: v})} placeholder="Full legal name" />
                  <Input label="GSTIN" value={form.gstin} onChange={v => setForm({...form, gstin: v.toUpperCase()})} placeholder="e.g., 27AABCB1234A1Z5" />
                  <Input label="PAN" value={form.pan} onChange={v => setForm({...form, pan: v.toUpperCase()})} placeholder="e.g., AABCB1234A" />
                  <Select label="Constitution" value={form.constitution} onChange={v => setForm({...form, constitution: v})} options={CONSTITUTIONS} placeholder="Select type..." />
                  <Input label="MSME Registration" value={form.msme_reg} onChange={v => setForm({...form, msme_reg: v})} placeholder="MSME Udyam number" />
                </div>
              </div>

              {/* Address */}
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3 flex items-center gap-2"><MapPin className="w-3.5 h-3.5" /> Address</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Address" value={form.address} onChange={v => setForm({...form, address: v})} placeholder="Street address" className="md:col-span-2" />
                  <Input label="City" value={form.city} onChange={v => setForm({...form, city: v})} placeholder="City" />
                  <Select label="State" value={form.state} onChange={v => setForm({...form, state: v})} options={states.map(s => ({value: s.name, label: `${s.code} - ${s.name}`}))} placeholder="Select state..." required />
                  <Input label="PIN Code" value={form.pin_code} onChange={v => setForm({...form, pin_code: v})} placeholder="6-digit PIN" />
                  <Input label="Country" value={form.country} onChange={v => setForm({...form, country: v})} placeholder="Country" disabled />
                </div>
              </div>

              {/* Contact */}
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3">Contact</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input label="Contact Person" value={form.contact} onChange={v => setForm({...form, contact: v})} placeholder="Name" />
                  <Input label="Email" value={form.email} onChange={v => setForm({...form, email: v})} placeholder="vendor@example.com" type="email" />
                  <Input label="Phone" value={form.phone} onChange={v => setForm({...form, phone: v})} placeholder="+91..." />
                </div>
              </div>

              {/* Financial */}
              <div>
                <p className="text-[10px] font-bold text-[#00C9A7] tracking-wider uppercase mb-3">Financial & Banking</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Select label="Payment Terms" value={form.payment_terms} onChange={v => setForm({...form, payment_terms: v})} options={PAYMENT_TERMS} />
                  <Input label="Bank Name" value={form.bank_name} onChange={v => setForm({...form, bank_name: v})} placeholder="Bank name" />
                  <Input label="Account Number" value={form.bank_account} onChange={v => setForm({...form, bank_account: v})} placeholder="Account number" />
                  <Input label="IFSC Code" value={form.ifsc} onChange={v => setForm({...form, ifsc: v.toUpperCase()})} placeholder="e.g., SBIN0001234" />
                </div>
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[#1B2D42]">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-[#7A8BA0] hover:text-[#E8EDF2]">Cancel</button>
              <button data-testid="save-vendor-btn" onClick={handleSave} disabled={saving}
                className="flex items-center gap-2 px-5 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors disabled:opacity-50">
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />} Save Vendor
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
