import React, { useState, useEffect } from 'react';
import { Download, FileText, ArrowRight, TrendingDown, TrendingUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (n === undefined || n === null) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

function TaxRow({ label, igst, cgst, sgst, utgst, bold, highlight }) {
  const cls = bold ? 'font-bold' : '';
  const color = highlight === 'green' ? 'text-[#00C9A7]' : highlight === 'red' ? 'text-[#FF4D6A]' : 'text-[#E8EDF2]';
  return (
    <tr className={`border-b border-[#1B2D42]/30 ${bold ? 'bg-[#0D1B2A]/60' : 'hover:bg-[#1B2D42]/20'}`}>
      <td className={`py-2.5 px-4 text-xs ${color} ${cls}`}>{label}</td>
      <td className={`py-2.5 px-4 text-right font-mono text-xs ${color} ${cls}`}>{formatINR(igst)}</td>
      <td className={`py-2.5 px-4 text-right font-mono text-xs ${color} ${cls}`}>{formatINR(cgst)}</td>
      <td className={`py-2.5 px-4 text-right font-mono text-xs ${color} ${cls}`}>{formatINR(sgst)}</td>
      <td className={`py-2.5 px-4 text-right font-mono text-xs ${color} ${cls}`}>{formatINR(utgst || 0)}</td>
    </tr>
  );
}

export default function GSTR3BPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/statutory/gstr3b`).then(r => r.json()).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-[#4A5B6E] py-12 text-center">Loading GSTR-3B...</div>;
  if (!data) return <div className="text-[#4A5B6E] py-12 text-center">Failed to load</div>;

  const s31 = data.sections?.["3_1"] || {};
  const s32 = data.sections?.["3_2"] || {};
  const s4 = data.sections?.["4"] || {};
  const s61 = data.sections?.["6_1"] || {};
  const summary = data.summary || {};
  const isPayable = summary.net_payable > 0;

  return (
    <div className="space-y-5" data-testid="gstr3b-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-purple-500/10 flex items-center justify-center">
            <FileText className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">GSTR-3B</h1>
            <p className="text-[#4A5B6E] text-sm">Monthly Summary Return — {data.legal_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#4A5B6E] bg-[#152236] border border-[#1B2D42] px-3 py-1.5 rounded-lg font-mono">
            {data.gstin || 'GSTIN not set'} | {data.return_period}
          </span>
          <button data-testid="gstr3b-export-btn" onClick={() => {
            fetch(`${API}/statutory/gstr3b/export`).then(r => r.blob()).then(b => {
              const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'GSTR3B.json'; a.click();
            });
          }} className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm font-bold transition-colors">
            <Download className="w-4 h-4" /> Export JSON
          </button>
        </div>
      </div>

      {/* Net liability card */}
      <div className={`rounded-xl p-6 border ${isPayable ? 'bg-[#FF4D6A]/5 border-[#FF4D6A]/20' : 'bg-[#00C9A7]/5 border-[#00C9A7]/20'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isPayable ? 'bg-[#FF4D6A]/10' : 'bg-[#00C9A7]/10'}`}>
              {isPayable ? <TrendingUp className="w-6 h-6 text-[#FF4D6A]" /> : <TrendingDown className="w-6 h-6 text-[#00C9A7]" />}
            </div>
            <div>
              <p className="text-[#7A8BA0] text-xs tracking-wider uppercase">Net Tax Liability</p>
              <p className={`text-3xl font-bold font-mono ${isPayable ? 'text-[#FF4D6A]' : 'text-[#00C9A7]'}`}>
                {formatINR(isPayable ? summary.net_payable : summary.net_refundable)}
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-[#E8EDF2] font-mono font-bold text-lg">{formatINR(summary.total_output_tax)}</p>
              <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase">Output Tax</p>
            </div>
            <div className="text-center">
              <p className="text-[#00C9A7] font-mono font-bold text-lg">{formatINR(summary.total_input_credit)}</p>
              <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase">Input Credit</p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3.1 */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="gstr3b-section-31">
        <div className="px-4 py-3 border-b border-[#1B2D42]">
          <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">{s31.label}</h3>
        </div>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase">
            <th className="py-2 px-4 text-left">Nature of Supplies</th>
            <th className="py-2 px-4 text-right">IGST</th><th className="py-2 px-4 text-right">CGST</th>
            <th className="py-2 px-4 text-right">SGST</th><th className="py-2 px-4 text-right">UTGST</th>
          </tr></thead>
          <tbody>
            <TaxRow label="(a) Outward taxable supplies (other than zero rated, nil rated and exempted)" igst={s31.outward_taxable_supplies?.igst} cgst={s31.outward_taxable_supplies?.cgst} sgst={s31.outward_taxable_supplies?.sgst} utgst={s31.outward_taxable_supplies?.utgst} />
            <TaxRow label="(b) Outward taxable supplies (zero rated)" igst={s31.zero_rated?.igst} cgst={0} sgst={0} utgst={0} />
            <TaxRow label="(c) Other outward supplies (Nil rated, exempted)" igst={0} cgst={0} sgst={0} utgst={0} />
            <TaxRow label="(d) Inward supplies (liable to reverse charge)" igst={s31.reverse_charge_inward?.igst} cgst={s31.reverse_charge_inward?.cgst} sgst={s31.reverse_charge_inward?.sgst} utgst={0} />
          </tbody>
        </table>
      </div>

      {/* Section 3.2 */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4" data-testid="gstr3b-section-32">
        <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase mb-3">{s32.label || '3.2 - Inter-State supplies'}</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#0D1B2A] rounded-lg p-3 text-center">
            <p className="text-lg font-bold font-mono text-blue-400">{formatINR(s32.to_unregistered?.taxable)}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Taxable Value (Unregistered)</p>
          </div>
          <div className="bg-[#0D1B2A] rounded-lg p-3 text-center">
            <p className="text-lg font-bold font-mono text-blue-400">{formatINR(s32.to_unregistered?.igst)}</p>
            <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">IGST (Unregistered)</p>
          </div>
        </div>
      </div>

      {/* Section 4 - ITC */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="gstr3b-section-4">
        <div className="px-4 py-3 border-b border-[#1B2D42]">
          <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">{s4.label}</h3>
        </div>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase">
            <th className="py-2 px-4 text-left">Details</th>
            <th className="py-2 px-4 text-right">IGST</th><th className="py-2 px-4 text-right">CGST</th>
            <th className="py-2 px-4 text-right">SGST</th><th className="py-2 px-4 text-right">UTGST</th>
          </tr></thead>
          <tbody>
            <TaxRow label="(A) ITC Available" igst={s4.itc_available?.igst} cgst={s4.itc_available?.cgst} sgst={s4.itc_available?.sgst} utgst={s4.itc_available?.utgst} highlight="green" />
            <TaxRow label="(B) ITC Reversed" igst={s4.itc_reversed?.igst} cgst={s4.itc_reversed?.cgst} sgst={s4.itc_reversed?.sgst} uitgst={0} />
            <TaxRow label="(C) Net ITC Available (A - B)" igst={s4.net_itc?.igst} cgst={s4.net_itc?.cgst} sgst={s4.net_itc?.sgst} utgst={s4.net_itc?.utgst} bold highlight="green" />
          </tbody>
        </table>
      </div>

      {/* Section 6.1 - Tax Payment */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="gstr3b-section-61">
        <div className="px-4 py-3 border-b border-[#1B2D42]">
          <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">{s61.label}</h3>
        </div>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase">
            <th className="py-2 px-4 text-left">Description</th>
            <th className="py-2 px-4 text-right">IGST</th><th className="py-2 px-4 text-right">CGST</th>
            <th className="py-2 px-4 text-right">SGST</th><th className="py-2 px-4 text-right">UTGST</th>
          </tr></thead>
          <tbody>
            <TaxRow label="Total Tax Payable" igst={s61.tax_payable?.igst} cgst={s61.tax_payable?.cgst} sgst={s61.tax_payable?.sgst} utgst={s61.tax_payable?.utgst} />
            <TaxRow label="ITC Utilized" igst={s61.itc_utilized?.igst} cgst={s61.itc_utilized?.cgst} sgst={s61.itc_utilized?.sgst} utgst={s61.itc_utilized?.utgst} highlight="green" />
            <TaxRow label="Tax Payable in Cash" igst={s61.cash_payable?.igst} cgst={s61.cash_payable?.cgst} sgst={s61.cash_payable?.sgst} utgst={s61.cash_payable?.utgst} bold highlight="red" />
          </tbody>
        </table>
      </div>
    </div>
  );
}
