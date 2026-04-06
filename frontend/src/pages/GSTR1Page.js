import React, { useState, useEffect } from 'react';
import { Download, FileText, ChevronDown, ChevronRight, Search } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (n === undefined || n === null) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

function SupplyBadge({ type }) {
  if (!type) return null;
  const isIGST = type.includes('IGST');
  return (
    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider ${isIGST ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>
      {isIGST ? 'INTER' : 'INTRA'}
    </span>
  );
}

function Section({ title, count, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-4 py-3 hover:bg-[#1B2D42]/30 transition-colors">
        <div className="flex items-center gap-2">
          {open ? <ChevronDown className="w-4 h-4 text-[#4A5B6E]" /> : <ChevronRight className="w-4 h-4 text-[#4A5B6E]" />}
          <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">{title}</h3>
        </div>
        <span className="text-[10px] text-[#4A5B6E] bg-[#0D1B2A] px-2 py-0.5 rounded-full">{count} records</span>
      </button>
      {open && children}
    </div>
  );
}

export default function GSTR1Page() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/statutory/gstr1`).then(r => r.json()).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-[#4A5B6E] py-12 text-center">Loading GSTR-1...</div>;
  if (!data) return <div className="text-[#4A5B6E] py-12 text-center">Failed to load GSTR-1 data</div>;

  const s = data.summary || {};

  return (
    <div className="space-y-5" data-testid="gstr1-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#00C9A7]/10 flex items-center justify-center">
            <FileText className="w-5 h-5 text-[#00C9A7]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">GSTR-1</h1>
            <p className="text-[#4A5B6E] text-sm">Outward Supplies — {data.legal_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#4A5B6E] bg-[#152236] border border-[#1B2D42] px-3 py-1.5 rounded-lg font-mono">
            {data.gstin || 'GSTIN not set'} | {data.return_period}
          </span>
          <button data-testid="gstr1-export-btn" onClick={() => {
            fetch(`${API}/api/statutory/gstr1/export`).then(r => r.blob()).then(b => {
              const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'GSTR1.csv'; a.click();
            });
          }} className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 sm:grid-cols-7 gap-3" data-testid="gstr1-summary">
        {[
          { label: 'Total Invoices', value: s.total_invoices, color: 'text-[#E8EDF2]' },
          { label: 'B2B', value: s.b2b_count, color: 'text-blue-400' },
          { label: 'B2C (Large)', value: s.b2c_large_count, color: 'text-purple-400' },
          { label: 'B2C (Small)', value: s.b2c_small_count, color: 'text-amber-400' },
          { label: 'IGST', value: formatINR(s.total_igst), color: 'text-blue-400' },
          { label: 'CGST', value: formatINR(s.total_cgst), color: 'text-emerald-400' },
          { label: 'SGST', value: formatINR(s.total_sgst), color: 'text-emerald-400' },
        ].map((c, i) => (
          <div key={i} className="bg-[#152236] border border-[#1B2D42] rounded-lg p-3 text-center">
            <p className={`text-lg font-bold font-mono ${c.color}`}>{c.value}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      {/* B2B Section */}
      <Section title={data.sections?.b2b?.label || 'B2B Invoices'} count={data.sections?.b2b?.count || 0} defaultOpen>
        <table className="w-full text-sm" data-testid="gstr1-b2b-table">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2 px-3 text-left">GSTIN</th><th className="py-2 px-3 text-left">Recipient</th>
            <th className="py-2 px-3 text-left">Invoice</th><th className="py-2 px-3 text-left">Supply</th>
            <th className="py-2 px-3 text-right">Taxable</th><th className="py-2 px-3 text-right">IGST</th>
            <th className="py-2 px-3 text-right">CGST</th><th className="py-2 px-3 text-right">SGST</th>
            <th className="py-2 px-3 text-right">Total</th>
          </tr></thead>
          <tbody>
            {(data.sections?.b2b?.invoices || []).map((inv, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-3 font-mono text-[11px] text-[#7A8BA0]">{inv.gstin_of_recipient || '—'}</td>
                <td className="py-2 px-3 text-xs text-[#E8EDF2]">{inv.receiver_name}</td>
                <td className="py-2 px-3 text-[#00C9A7] font-mono text-[11px]">{inv.invoice_number}</td>
                <td className="py-2 px-3"><SupplyBadge type={inv.supply_type} /></td>
                <td className="py-2 px-3 text-right font-mono text-xs text-[#7A8BA0]">{formatINR(inv.taxable_value)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-blue-400">{formatINR(inv.igst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-emerald-400">{formatINR(inv.cgst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-emerald-400">{formatINR(inv.sgst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs font-semibold text-[#E8EDF2]">{formatINR(inv.invoice_value)}</td>
              </tr>
            ))}
            {(data.sections?.b2b?.invoices || []).length === 0 && (
              <tr><td colSpan={9} className="py-6 text-center text-[#4A5B6E] text-xs">No B2B invoices. Invoices to registered GSTINs will appear here.</td></tr>
            )}
          </tbody>
        </table>
      </Section>

      {/* B2C Large */}
      <Section title={data.sections?.b2c_large?.label || 'B2C Large'} count={data.sections?.b2c_large?.count || 0}>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2 px-3 text-left">Recipient</th><th className="py-2 px-3 text-left">Invoice</th>
            <th className="py-2 px-3 text-left">Place of Supply</th>
            <th className="py-2 px-3 text-right">Taxable</th><th className="py-2 px-3 text-right">IGST</th>
            <th className="py-2 px-3 text-right">Total</th>
          </tr></thead>
          <tbody>
            {(data.sections?.b2c_large?.invoices || []).map((inv, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-3 text-xs text-[#E8EDF2]">{inv.receiver_name}</td>
                <td className="py-2 px-3 text-[#00C9A7] font-mono text-[11px]">{inv.invoice_number}</td>
                <td className="py-2 px-3 text-xs text-[#7A8BA0]">{inv.place_of_supply}</td>
                <td className="py-2 px-3 text-right font-mono text-xs">{formatINR(inv.taxable_value)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-blue-400">{formatINR(inv.igst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs font-semibold">{formatINR(inv.invoice_value)}</td>
              </tr>
            ))}
            {(data.sections?.b2c_large?.invoices || []).length === 0 && (
              <tr><td colSpan={6} className="py-6 text-center text-[#4A5B6E] text-xs">No B2C (Large) invoices. Inter-state invoices to unregistered parties exceeding 2.5L will appear here.</td></tr>
            )}
          </tbody>
        </table>
      </Section>

      {/* B2C Small */}
      <Section title={data.sections?.b2c_small?.label || 'B2C Small'} count={data.sections?.b2c_small?.count || 0}>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2 px-3 text-left">Recipient</th><th className="py-2 px-3 text-left">Invoice</th>
            <th className="py-2 px-3 text-left">Place of Supply</th>
            <th className="py-2 px-3 text-right">Taxable</th><th className="py-2 px-3 text-right">CGST</th>
            <th className="py-2 px-3 text-right">SGST</th><th className="py-2 px-3 text-right">Total</th>
          </tr></thead>
          <tbody>
            {(data.sections?.b2c_small?.invoices || []).map((inv, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-3 text-xs text-[#E8EDF2]">{inv.receiver_name}</td>
                <td className="py-2 px-3 text-[#00C9A7] font-mono text-[11px]">{inv.invoice_number}</td>
                <td className="py-2 px-3 text-xs text-[#7A8BA0]">{inv.place_of_supply}</td>
                <td className="py-2 px-3 text-right font-mono text-xs">{formatINR(inv.taxable_value)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-emerald-400">{formatINR(inv.cgst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs text-emerald-400">{formatINR(inv.sgst)}</td>
                <td className="py-2 px-3 text-right font-mono text-xs font-semibold">{formatINR(inv.invoice_value)}</td>
              </tr>
            ))}
            {(data.sections?.b2c_small?.invoices || []).length === 0 && (
              <tr><td colSpan={7} className="py-6 text-center text-[#4A5B6E] text-xs">No B2C (Small) invoices.</td></tr>
            )}
          </tbody>
        </table>
      </Section>

      {/* HSN Summary */}
      <Section title={data.sections?.hsn?.label || 'HSN Summary'} count={data.sections?.hsn?.count || 0}>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2 px-3 text-left">HSN/SAC</th><th className="py-2 px-3 text-left">Description</th>
            <th className="py-2 px-3 text-left">UQC</th>
            <th className="py-2 px-3 text-right">Qty</th><th className="py-2 px-3 text-right">Taxable Value</th>
          </tr></thead>
          <tbody>
            {(data.sections?.hsn?.items || []).map((h, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-3 font-mono text-[#00C9A7] text-xs">{h.hsn_sac}</td>
                <td className="py-2 px-3 text-xs text-[#E8EDF2]">{h.description}</td>
                <td className="py-2 px-3 text-xs text-[#7A8BA0]">{h.uqc}</td>
                <td className="py-2 px-3 text-right font-mono text-xs">{h.total_qty}</td>
                <td className="py-2 px-3 text-right font-mono text-xs">{formatINR(h.taxable_value)}</td>
              </tr>
            ))}
            {(data.sections?.hsn?.items || []).length === 0 && (
              <tr><td colSpan={5} className="py-6 text-center text-[#4A5B6E] text-xs">No HSN data. Items with HSN/SAC codes will be summarized here.</td></tr>
            )}
          </tbody>
        </table>
      </Section>

      {/* Document Summary */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4">
        <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase mb-3">{data.sections?.docs?.label || 'Document Summary'}</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-[#0D1B2A] rounded-lg p-3 text-center">
            <p className="text-lg font-bold font-mono text-[#E8EDF2]">{data.sections?.docs?.invoices_issued || 0}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Invoices Issued</p>
          </div>
          <div className="bg-[#0D1B2A] rounded-lg p-3 text-center">
            <p className="text-lg font-bold font-mono text-[#E8EDF2]">{data.sections?.docs?.credit_notes || 0}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Credit Notes</p>
          </div>
          <div className="bg-[#0D1B2A] rounded-lg p-3 text-center">
            <p className="text-lg font-bold font-mono text-[#E8EDF2]">{data.sections?.docs?.debit_notes || 0}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Debit Notes</p>
          </div>
        </div>
      </div>
    </div>
  );
}
