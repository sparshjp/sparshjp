import React, { useState, useEffect } from 'react';
import { Scale, Download, FileText, ChevronDown, ChevronRight, IndianRupee, AlertTriangle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (n === undefined || n === null) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

export default function GSTModule() {
  const [activeTab, setActiveTab] = useState('gstr1');
  const [gstr1, setGstr1] = useState(null);
  const [gstr3b, setGstr3b] = useState(null);
  const [tds, setTds] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadData(); }, [activeTab]);

  async function loadData() {
    setLoading(true);
    try {
      if (activeTab === 'gstr1') {
        const r = await fetch(`${API}/statutory/gstr1`);
        setGstr1(await r.json());
      } else if (activeTab === 'gstr3b') {
        const r = await fetch(`${API}/statutory/gstr3b`);
        setGstr3b(await r.json());
      } else if (activeTab === 'tds') {
        const r = await fetch(`${API}/statutory/tds-return`);
        setTds(await r.json());
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  async function handleExport(type) {
    const endpoints = { gstr1: 'gstr1/export', gstr3b: 'gstr3b/export', tds: 'tds-return/export' };
    const filenames = { gstr1: 'GSTR1.csv', gstr3b: 'GSTR3B.json', tds: 'TDS_Return_26Q.csv' };
    try {
      const r = await fetch(`${API}/statutory/${endpoints[type]}`);
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filenames[type]; a.click();
      URL.revokeObjectURL(url);
    } catch (e) { console.error(e); }
  }

  const tabs = [
    { id: 'gstr1', label: 'GSTR-1', desc: 'Outward Supplies' },
    { id: 'gstr3b', label: 'GSTR-3B', desc: 'Monthly Summary' },
    { id: 'tds', label: 'TDS Return', desc: 'Form 26Q' },
  ];

  return (
    <div className="space-y-6" data-testid="gst-tds-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">GST & TDS</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Statutory Returns for Filing</p>
        </div>
        <button
          data-testid="gst-export-btn"
          onClick={() => handleExport(activeTab)}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-semibold transition-colors"
        >
          <Download className="w-4 h-4" /> Download {tabs.find(t => t.id === activeTab)?.label}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0D1B2A] border border-[#1B2D42] p-1 rounded-lg w-fit" data-testid="gst-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            data-testid={`gst-tab-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-col px-5 py-2.5 rounded-md text-sm transition-all ${
              activeTab === tab.id
                ? 'bg-[#00C9A7]/15 text-[#00C9A7] border border-[#00C9A7]/30'
                : 'text-[#7A8BA0] hover:text-[#E8EDF2] hover:bg-[#152236]'
            }`}
          >
            <span className="font-semibold">{tab.label}</span>
            <span className="text-[10px] opacity-60">{tab.desc}</span>
          </button>
        ))}
      </div>

      {loading && <div className="text-[#4A5B6E] py-8 text-center">Loading...</div>}

      {/* GSTR-1 */}
      {activeTab === 'gstr1' && gstr1 && (
        <div className="space-y-4" data-testid="gstr1-content">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-[#E8EDF2]">{gstr1.legal_name}</h2>
                <p className="text-[#4A5B6E] text-xs">GSTIN: {gstr1.gstin} | Period: {gstr1.return_period}</p>
              </div>
              <div className="text-right">
                <p className="text-[#00C9A7] text-xl font-bold font-mono">{formatINR(gstr1.summary?.total_tax)}</p>
                <p className="text-[#4A5B6E] text-xs">Total Tax</p>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {[
                { label: 'Invoices', value: gstr1.summary?.total_invoices },
                { label: 'Taxable Value', value: formatINR(gstr1.summary?.total_taxable_value) },
                { label: 'IGST', value: formatINR(gstr1.summary?.total_igst) },
                { label: 'CGST', value: formatINR(gstr1.summary?.total_cgst) },
                { label: 'SGST', value: formatINR(gstr1.summary?.total_sgst) },
              ].map((s, i) => (
                <div key={i} className="bg-[#0D1B2A] rounded-lg p-3 text-center">
                  <p className="text-[#E8EDF2] font-mono font-semibold">{s.value}</p>
                  <p className="text-[#4A5B6E] text-[10px] mt-1 tracking-wider uppercase">{s.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
            <div className="px-4 py-3 border-b border-[#1B2D42]">
              <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">{gstr1.sections?.b2b?.label}</h3>
            </div>
            <table className="w-full text-sm" data-testid="gstr1-table">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs">
                <th className="py-2.5 px-4 text-left">GSTIN</th><th className="py-2.5 px-4 text-left">Recipient</th>
                <th className="py-2.5 px-4 text-left">Invoice</th><th className="py-2.5 px-4 text-right">Value</th>
                <th className="py-2.5 px-4 text-right">Taxable</th><th className="py-2.5 px-4 text-right">CGST</th>
                <th className="py-2.5 px-4 text-right">SGST</th>
              </tr></thead>
              <tbody>
                {gstr1.sections?.b2b?.invoices?.map((inv, i) => (
                  <tr key={i} className="border-b border-[#1B2D42]/50 hover:bg-[#1B2D42]/30">
                    <td className="py-2 px-4 font-mono text-xs text-[#7A8BA0]">{inv.gstin_of_recipient || '—'}</td>
                    <td className="py-2 px-4 text-[#E8EDF2]">{inv.receiver_name}</td>
                    <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{inv.invoice_number}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{formatINR(inv.invoice_value)}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(inv.taxable_value)}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(inv.cgst)}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(inv.sgst)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* GSTR-3B */}
      {activeTab === 'gstr3b' && gstr3b && (
        <div className="space-y-4" data-testid="gstr3b-content">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-[#E8EDF2]">{gstr3b.legal_name}</h2>
                <p className="text-[#4A5B6E] text-xs">GSTIN: {gstr3b.gstin} | Period: {gstr3b.return_period}</p>
              </div>
              <div className={`px-4 py-2 rounded-lg text-center ${
                gstr3b.summary?.net_payable > 0 ? 'bg-[#FF4D6A]/10 border border-[#FF4D6A]/20' : 'bg-[#00C9A7]/10 border border-[#00C9A7]/20'
              }`}>
                <p className={`text-xl font-bold font-mono ${gstr3b.summary?.net_payable > 0 ? 'text-[#FF4D6A]' : 'text-[#00C9A7]'}`}>
                  {formatINR(gstr3b.summary?.net_payable > 0 ? gstr3b.summary.net_payable : gstr3b.summary?.net_refundable)}
                </p>
                <p className="text-[10px] text-[#4A5B6E] tracking-wider uppercase">{gstr3b.summary?.net_payable > 0 ? 'Net Payable' : 'Net Refundable'}</p>
              </div>
            </div>
          </div>

          {/* Section 3.1 */}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase mb-4">{gstr3b.sections?.["3_1"]?.label}</h3>
            <div className="grid grid-cols-4 gap-3">
              {["IGST", "CGST", "SGST", "Cess"].map((tax, i) => (
                <div key={tax} className="bg-[#0D1B2A] rounded-lg p-3 text-center">
                  <p className="text-[#E8EDF2] font-mono font-semibold">
                    {formatINR(gstr3b.sections?.["3_1"]?.outward_taxable_supplies?.[tax.toLowerCase()] || 0)}
                  </p>
                  <p className="text-[#4A5B6E] text-[10px] mt-1">{tax}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 4 - ITC */}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase mb-4">{gstr3b.sections?.["4"]?.label}</h3>
            <div className="grid grid-cols-4 gap-3">
              {["IGST", "CGST", "SGST", "Cess"].map((tax) => (
                <div key={tax} className="bg-[#0D1B2A] rounded-lg p-3 text-center">
                  <p className="text-[#00C9A7] font-mono font-semibold">
                    {formatINR(gstr3b.sections?.["4"]?.itc_available?.[tax.toLowerCase()] || 0)}
                  </p>
                  <p className="text-[#4A5B6E] text-[10px] mt-1">{tax}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 6.1 - Payment */}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase mb-4">{gstr3b.sections?.["6_1"]?.label}</h3>
            <table className="w-full text-sm" data-testid="gstr3b-payment-table">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs">
                <th className="py-2 px-4 text-left">Description</th><th className="py-2 px-4 text-right">IGST</th>
                <th className="py-2 px-4 text-right">CGST</th><th className="py-2 px-4 text-right">SGST</th>
              </tr></thead>
              <tbody>
                <tr className="border-b border-[#1B2D42]/50">
                  <td className="py-2 px-4 text-[#E8EDF2]">Tax Payable</td>
                  <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{formatINR(gstr3b.sections?.["6_1"]?.tax_payable?.igst)}</td>
                  <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{formatINR(gstr3b.sections?.["6_1"]?.tax_payable?.cgst)}</td>
                  <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{formatINR(gstr3b.sections?.["6_1"]?.tax_payable?.sgst)}</td>
                </tr>
                <tr className="border-b border-[#1B2D42]/50">
                  <td className="py-2 px-4 text-[#00C9A7]">ITC Utilized</td>
                  <td className="py-2 px-4 text-right font-mono text-[#00C9A7]">{formatINR(gstr3b.sections?.["6_1"]?.itc_utilized?.igst)}</td>
                  <td className="py-2 px-4 text-right font-mono text-[#00C9A7]">{formatINR(gstr3b.sections?.["6_1"]?.itc_utilized?.cgst)}</td>
                  <td className="py-2 px-4 text-right font-mono text-[#00C9A7]">{formatINR(gstr3b.sections?.["6_1"]?.itc_utilized?.sgst)}</td>
                </tr>
                <tr className="bg-[#0D1B2A]">
                  <td className="py-2.5 px-4 font-bold text-[#FF4D6A]">Cash Payable</td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-[#FF4D6A]">{formatINR(gstr3b.sections?.["6_1"]?.cash_payable?.igst)}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-[#FF4D6A]">{formatINR(gstr3b.sections?.["6_1"]?.cash_payable?.cgst)}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-[#FF4D6A]">{formatINR(gstr3b.sections?.["6_1"]?.cash_payable?.sgst)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TDS Return */}
      {activeTab === 'tds' && tds && (
        <div className="space-y-4" data-testid="tds-content">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-[#E8EDF2]">{tds.deductor_name}</h2>
                <p className="text-[#4A5B6E] text-xs">TAN: {tds.tan} | {tds.quarter} FY {tds.financial_year}</p>
              </div>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="bg-[#0D1B2A] rounded-lg px-4 py-2">
                  <p className="text-[#FF4D6A] font-mono font-bold">{formatINR(tds.summary?.total_tds_deducted)}</p>
                  <p className="text-[#4A5B6E] text-[10px]">TDS Deducted</p>
                </div>
                <div className="bg-[#0D1B2A] rounded-lg px-4 py-2">
                  <p className="text-[#FFB547] font-mono font-bold">{formatINR(tds.summary?.tds_pending_deposit)}</p>
                  <p className="text-[#4A5B6E] text-[10px]">Pending Deposit</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
            <table className="w-full text-sm" data-testid="tds-table">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#0D1B2A]/50">
                <th className="py-2.5 px-4 text-left">Deductee</th><th className="py-2.5 px-4 text-left">Section</th>
                <th className="py-2.5 px-4 text-left">Date</th><th className="py-2.5 px-4 text-right">Amount Paid</th>
                <th className="py-2.5 px-4 text-right">TDS Rate</th><th className="py-2.5 px-4 text-right">TDS Amt</th>
              </tr></thead>
              <tbody>
                {tds.deductees?.length > 0 ? tds.deductees.map((d, i) => (
                  <tr key={i} className="border-b border-[#1B2D42]/50 hover:bg-[#1B2D42]/30">
                    <td className="py-2 px-4 text-[#E8EDF2]">{d.deductee_name}</td>
                    <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{d.section}</td>
                    <td className="py-2 px-4 text-[#7A8BA0]">{d.date_of_payment}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#E8EDF2]">{formatINR(d.amount_paid)}</td>
                    <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{d.tds_rate}%</td>
                    <td className="py-2 px-4 text-right font-mono font-semibold text-[#FF4D6A]">{formatINR(d.tds_amount)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No TDS deductions found. Process transactions with TDS to see data here.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
