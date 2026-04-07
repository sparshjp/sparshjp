import React, { useState, useEffect, useRef } from 'react';
import { Building2, Save, Upload, Check, Loader2, MapPin, Globe, Banknote, FileText, Shield } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const LEGAL_STRUCTURES = ['Private Limited', 'Public Limited', 'LLP', 'Sole Proprietor', 'Partnership', 'OPC', 'Section 8'];
const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD', 'JPY'];

function Section({ icon: Icon, title, children }) {
  return (
    <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
      <div className="flex items-center gap-2.5 px-5 py-3 border-b border-[#1B2D42] bg-[#0D1B2A]/50">
        <Icon className="w-4 h-4 text-[#00C9A7]" />
        <h3 className="text-sm font-bold text-[#E8EDF2] tracking-wide">{title}</h3>
      </div>
      <div className="px-5 py-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {children}
      </div>
    </div>
  );
}

function Field({ label, children, span }) {
  return (
    <div className={span === 2 ? 'md:col-span-2' : span === 3 ? 'md:col-span-3 lg:col-span-3' : ''}>
      <label className="text-[10px] font-medium tracking-wider uppercase text-[#7A8BA0] mb-1.5 block">{label}</label>
      {children}
    </div>
  );
}

function Input({ value, onChange, placeholder, type = 'text' }) {
  return (
    <input type={type} value={value || ''} onChange={e => onChange(e.target.value)} placeholder={placeholder}
      className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] focus:ring-1 focus:ring-[#00C9A7]/20 outline-none transition-colors" />
  );
}

function TextArea({ value, onChange, placeholder, rows = 3 }) {
  return (
    <textarea value={value || ''} onChange={e => onChange(e.target.value)} placeholder={placeholder} rows={rows}
      className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] focus:ring-1 focus:ring-[#00C9A7]/20 outline-none transition-colors resize-none" />
  );
}

function Select({ value, onChange, options, placeholder }) {
  return (
    <select value={value || ''} onChange={e => onChange(e.target.value)}
      className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7] outline-none">
      <option value="">{placeholder || 'Select...'}</option>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  );
}

export default function CompanySetup() {
  const [data, setData] = useState({});
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/company/settings`).then(r => r.json()).then(d => {
      if (d.exists) { delete d.exists; setData(d); }
      setLoaded(true);
    }).catch(() => setLoaded(true));
  }, []);

  const set = (key, val) => setData(prev => ({ ...prev, [key]: val }));

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/company/settings`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.ok) toast.success('Company settings saved');
      else toast.error('Failed to save');
    } catch { toast.error('Network error'); }
    setSaving(false);
  };

  const handleLogoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/company/settings/logo`, { method: 'POST', body: formData });
      if (res.ok) {
        const { logo_url } = await res.json();
        set('logo_url', logo_url);
        toast.success('Logo uploaded');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Upload failed');
      }
    } catch { toast.error('Upload failed'); }
    setUploading(false);
  };

  if (!loaded) return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 animate-spin text-[#00C9A7]" /></div>;

  return (
    <div className="space-y-5 pb-20" data-testid="company-setup-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Company Setup</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Core identification, financial settings, and document configuration</p>
        </div>
        <button data-testid="company-save-btn" onClick={handleSave} disabled={saving}
          className="flex items-center gap-2 px-5 py-2.5 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors disabled:opacity-50">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      {/* 1. Core Identification & Legal */}
      <Section icon={Building2} title="Core Identification & Legal Information">
        <Field label="Legal Entity Name *" span={2}>
          <Input value={data.legal_name} onChange={v => set('legal_name', v)} placeholder="e.g. PolyMerx Specialty Chemicals Pvt. Ltd." />
        </Field>
        <Field label="Company Tagline / Short Name">
          <Input value={data.short_name} onChange={v => set('short_name', v)} placeholder="e.g. PolyMerx" />
        </Field>
        <Field label="Company Logo">
          <div className="flex items-center gap-3">
            {data.logo_url ? (
              <img src={`${API}${data.logo_url}`} alt="Logo" className="w-12 h-12 rounded-lg object-cover border border-[#1B2D42]" />
            ) : (
              <div className="w-12 h-12 rounded-lg bg-[#0D1B2A] border border-dashed border-[#1B2D42] flex items-center justify-center">
                <Building2 className="w-5 h-5 text-[#4A5B6E]" />
              </div>
            )}
            <input ref={fileRef} type="file" accept="image/*" onChange={handleLogoUpload} className="hidden" />
            <button onClick={() => fileRef.current?.click()} disabled={uploading} data-testid="logo-upload-btn"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1B2D42] hover:bg-[#1B2D42]/70 text-[#E8EDF2] rounded-lg text-xs font-medium transition-colors">
              {uploading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Upload className="w-3 h-3" />}
              {uploading ? 'Uploading...' : 'Upload Logo'}
            </button>
          </div>
        </Field>
        <Field label="Registration Number (CIN)">
          <Input value={data.registration_number} onChange={v => set('registration_number', v)} placeholder="e.g. U24110MH2018PTC123456" />
        </Field>
        <Field label="Tax ID (GSTIN)">
          <Input value={data.gstin} onChange={v => set('gstin', v)} placeholder="e.g. 27AABCU9603R1ZM" />
        </Field>
        <Field label="PAN">
          <Input value={data.pan} onChange={v => set('pan', v)} placeholder="e.g. AABCU9603R" />
        </Field>
        <Field label="Legal Structure">
          <Select value={data.legal_structure} onChange={v => set('legal_structure', v)} options={LEGAL_STRUCTURES} placeholder="Select structure" />
        </Field>
      </Section>

      {/* 2. Contact & Address */}
      <Section icon={MapPin} title="Contact Information & Address">
        <Field label="Registered Address" span={3}>
          <TextArea value={data.registered_address} onChange={v => set('registered_address', v)} placeholder="Full registered office address" rows={2} />
        </Field>
        <Field label="Billing Address" span={3}>
          <TextArea value={data.billing_address} onChange={v => set('billing_address', v)} placeholder="Address for invoices (leave blank if same as registered)" rows={2} />
        </Field>
        <Field label="Shipping / Factory Address" span={3}>
          <TextArea value={data.shipping_address} onChange={v => set('shipping_address', v)} placeholder="Manufacturing / warehouse address" rows={2} />
        </Field>
        <Field label="Phone">
          <Input value={data.phone} onChange={v => set('phone', v)} placeholder="+91 22 2345 6789" />
        </Field>
        <Field label="Email">
          <Input value={data.email} onChange={v => set('email', v)} placeholder="info@polymerx.in" type="email" />
        </Field>
        <Field label="Website">
          <Input value={data.website} onChange={v => set('website', v)} placeholder="https://polymerx.in" />
        </Field>
      </Section>

      {/* 3. Financial & Operational */}
      <Section icon={Banknote} title="Financial & Operational Settings">
        <Field label="Base Currency *">
          <Select value={data.base_currency} onChange={v => set('base_currency', v)} options={CURRENCIES} placeholder="Select currency" />
        </Field>
        <Field label="Financial Year Start Date *">
          <Input value={data.fy_start_date} onChange={v => set('fy_start_date', v)} type="date" />
        </Field>
        <Field label="Book Beginning Date">
          <Input value={data.book_start_date} onChange={v => set('book_start_date', v)} type="date" />
        </Field>
        <Field label="Multi-Company (Parent)" span={2}>
          <Input value={data.parent_company} onChange={v => set('parent_company', v)} placeholder="Leave blank if standalone" />
        </Field>
        <Field label="Branch / Division Name">
          <Input value={data.branch_name} onChange={v => set('branch_name', v)} placeholder="e.g. Thane Unit 1" />
        </Field>
      </Section>

      {/* 4. Statutory & Regional */}
      <Section icon={Globe} title="Statutory & Regional Information">
        <Field label="Country / Region">
          <Input value={data.country} onChange={v => set('country', v)} placeholder="India" />
        </Field>
        <Field label="State">
          <Input value={data.state} onChange={v => set('state', v)} placeholder="Maharashtra" />
        </Field>
        <Field label="Time Zone">
          <Select value={data.timezone} onChange={v => set('timezone', v)}
            options={['Asia/Kolkata', 'Asia/Dubai', 'Asia/Singapore', 'Europe/London', 'America/New_York', 'America/Los_Angeles']}
            placeholder="Select timezone" />
        </Field>
        <Field label="Language Preference">
          <Select value={data.language} onChange={v => set('language', v)}
            options={['English', 'Hindi', 'Marathi', 'Tamil', 'Telugu', 'Kannada', 'Bengali', 'Gujarati']}
            placeholder="Select language" />
        </Field>
        <Field label="Local Tax Regime" span={2}>
          <Input value={data.tax_regime} onChange={v => set('tax_regime', v)} placeholder="e.g. GST Regular, GST Composition, SEZ" />
        </Field>
      </Section>

      {/* 5. Document Configuration */}
      <Section icon={FileText} title="Document Configuration">
        <Field label="Bank Name">
          <Input value={data.bank_name} onChange={v => set('bank_name', v)} placeholder="HDFC Bank" />
        </Field>
        <Field label="Account Number">
          <Input value={data.bank_account_no} onChange={v => set('bank_account_no', v)} placeholder="50100123456789" />
        </Field>
        <Field label="IFSC / SWIFT Code">
          <Input value={data.bank_ifsc} onChange={v => set('bank_ifsc', v)} placeholder="HDFC0001234" />
        </Field>
        <Field label="Digital Signature (Name)" span={2}>
          <Input value={data.digital_signature_name} onChange={v => set('digital_signature_name', v)} placeholder="Authorized signatory name for documents" />
        </Field>
        <Field label="Designation">
          <Input value={data.signatory_designation} onChange={v => set('signatory_designation', v)} placeholder="Director / CFO" />
        </Field>
        <Field label="Default Terms & Conditions" span={3}>
          <TextArea value={data.terms_and_conditions} onChange={v => set('terms_and_conditions', v)}
            placeholder="Standard terms and conditions to print on POs and Invoices..."
            rows={4} />
        </Field>
      </Section>

      {/* Bottom save */}
      <div className="flex justify-end pt-2">
        <button onClick={handleSave} disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors disabled:opacity-50">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save All Settings'}
        </button>
      </div>
    </div>
  );
}
