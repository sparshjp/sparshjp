import React, { useState, useEffect } from 'react';
import { Download, Scale } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (n === undefined || n === null) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

export default function TDSPage() {
  const [tds, setTds] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/statutory/tds-return`).then(r => r.json()).then(d => { setTds(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-[#4A5B6E] py-12 text-center">Loading TDS Return...</div>;
  if (!tds) return <div className="text-[#4A5B6E] py-12 text-center">Failed to load</div>;

  return (
    <div className="space-y-5" data-testid="tds-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-orange-500/10 flex items-center justify-center">
            <Scale className="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">TDS Returns</h1>
            <p className="text-[#4A5B6E] text-sm">Form 26Q — {tds.deductor_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#4A5B6E] bg-[#152236] border border-[#1B2D42] px-3 py-1.5 rounded-lg font-mono">
            TAN: {tds.tan || 'Not set'} | {tds.quarter} FY {tds.financial_year}
          </span>
          <button data-testid="tds-export-btn" onClick={() => {
            fetch(`${API}/api/statutory/tds-return/export`).then(r => r.blob()).then(b => {
              const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'TDS_Return_26Q.csv'; a.click();
            });
          }} className="flex items-center gap-2 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm font-bold transition-colors">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="tds-summary">
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
          <p className="text-2xl font-bold font-mono text-[#E8EDF2]">{tds.summary?.total_deductees || 0}</p>
          <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Deductees</p>
        </div>
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
          <p className="text-2xl font-bold font-mono text-[#E8EDF2]">{formatINR(tds.summary?.total_amount_paid)}</p>
          <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Total Amount Paid</p>
        </div>
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
          <p className="text-2xl font-bold font-mono text-[#FF4D6A]">{formatINR(tds.summary?.total_tds_deducted)}</p>
          <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">TDS Deducted</p>
        </div>
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
          <p className="text-2xl font-bold font-mono text-amber-400">{formatINR(tds.summary?.tds_pending_deposit)}</p>
          <p className="text-[9px] text-[#4A5B6E] tracking-wider uppercase mt-1">Pending Deposit</p>
        </div>
      </div>

      {/* Deductees table */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-[#1B2D42]">
          <h3 className="text-xs font-semibold text-orange-400 tracking-wider uppercase">Deductee Details (Form 26Q)</h3>
        </div>
        <table className="w-full text-sm" data-testid="tds-table">
          <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
            <th className="py-2.5 px-4 text-left">Deductee</th><th className="py-2.5 px-4 text-left">PAN</th>
            <th className="py-2.5 px-4 text-left">Section</th><th className="py-2.5 px-4 text-left">Date</th>
            <th className="py-2.5 px-4 text-right">Amount Paid</th><th className="py-2.5 px-4 text-right">TDS Rate</th>
            <th className="py-2.5 px-4 text-right">TDS Amount</th>
          </tr></thead>
          <tbody>
            {tds.deductees?.length > 0 ? tds.deductees.map((d, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-4 text-xs text-[#E8EDF2]">{d.deductee_name}</td>
                <td className="py-2 px-4 font-mono text-xs text-[#7A8BA0]">{d.pan || '—'}</td>
                <td className="py-2 px-4"><span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">{d.section}</span></td>
                <td className="py-2 px-4 text-xs text-[#7A8BA0]">{d.date_of_payment}</td>
                <td className="py-2 px-4 text-right font-mono text-xs text-[#E8EDF2]">{formatINR(d.amount_paid)}</td>
                <td className="py-2 px-4 text-right font-mono text-xs text-[#7A8BA0]">{d.tds_rate}%</td>
                <td className="py-2 px-4 text-right font-mono text-xs font-semibold text-[#FF4D6A]">{formatINR(d.tds_amount)}</td>
              </tr>
            )) : (
              <tr><td colSpan={7} className="py-12 text-center text-[#4A5B6E]">
                <Scale className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-xs">No TDS deductions found.</p>
                <p className="text-xs mt-1">Process transactions with TDS to see data here.</p>
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
