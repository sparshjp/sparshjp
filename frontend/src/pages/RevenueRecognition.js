import { useState, useEffect } from 'react';
import { API } from '../App';
import { BookOpen, TrendingUp, AlertCircle, ArrowUpRight, ArrowDownRight, FileText, ChevronDown, ChevronUp } from 'lucide-react';

const METHOD_COLORS = {
  'POC - Cost Incurred': '#4ade80',
  'T&M Actuals': '#38bdf8',
  'Milestone': '#a78bfa',
  'Straight-Line Retainer': '#c084fc',
  'POC - Milestone Hybrid': '#f59e0b',
  'T&M Export': '#fbbf24',
};

export default function RevenueRecognition() {
  const [schedule, setSchedule] = useState(null);
  const [disclosure, setDisclosure] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [tab, setTab] = useState('schedule');
  const [loading, setLoading] = useState(true);
  const [expandedTxn, setExpandedTxn] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/revenue/schedule`).then(r => r.ok ? r.json() : {}),
      fetch(`${API}/revenue/ind-as-115`).then(r => r.ok ? r.json() : {}),
      fetch(`${API}/revenue/transactions`).then(r => r.ok ? r.json() : []),
    ]).then(([sch, disc, txns]) => {
      setSchedule(sch);
      setDisclosure(disc);
      setTransactions(txns);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const fmt = (v) => v != null ? `₹${(v / 100000).toFixed(2)}L` : '—';
  const fmtFull = (v) => v != null ? `₹${v.toLocaleString()}` : '—';

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading revenue data...</div>;

  const summ = schedule?.summary || {};
  const disc = disclosure || {};

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6" data-testid="revenue-page">
      <div>
        <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="revenue-title">Revenue Recognition</h1>
        <p className="text-[#4A5B6E] text-sm mt-1">Ind AS 115 — March 2026 (FY-end)</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Revenue (Mar)', value: fmt(summ.total_revenue_march), icon: TrendingUp, color: '#22c55e' },
          { label: 'Contract Assets', value: fmt(summ.total_contract_assets), sub: 'Unbilled AR', icon: ArrowUpRight, color: '#38bdf8' },
          { label: 'Contract Liabilities', value: fmt(summ.total_contract_liabilities), sub: 'Deferred Revenue', icon: ArrowDownRight, color: '#f59e0b' },
          { label: 'Total RPO', value: fmt(disc.total_rpo), sub: 'Remaining Obligations', icon: BookOpen, color: '#a78bfa' },
        ].map((c, i) => (
          <div key={i} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`rev-summary-${i}`}>
            <div className="flex items-center gap-2 mb-2">
              <c.icon size={16} style={{ color: c.color }} />
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5B6E]">{c.label}</span>
            </div>
            <p className="text-xl font-black text-[#E8EDF2]">{c.value}</p>
            {c.sub && <p className="text-[10px] text-[#4A5B6E] mt-0.5">{c.sub}</p>}
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[#1B2D42]">
        {[
          { id: 'schedule', label: 'Revenue Schedule' },
          { id: 'disclosure', label: 'Ind AS 115 Disclosure' },
          { id: 'transactions', label: 'Revenue Transactions' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} data-testid={`rev-tab-${t.id}`}
            className={`px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${tab === t.id ? 'border-[#00d4aa] text-[#00d4aa]' : 'border-transparent text-[#4A5B6E] hover:text-[#E8EDF2]'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Schedule Tab */}
      {tab === 'schedule' && schedule && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]">
            <h2 className="text-sm font-bold text-[#E8EDF2]">Revenue Recognition Schedule — Ind AS 115</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#1B2D42] text-[#4A5B6E]">
                  {['Project', 'Method', 'Total', '% Feb', '% Mar', 'Rev Feb', 'Rev Mar', 'Billed Mar', 'Contract Position'].map((h, i) => (
                    <th key={i} className="px-3 py-2.5 text-left font-bold uppercase tracking-wider text-[10px]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {schedule.schedule.map(s => {
                  const isAsset = (s.contract_asset || 0) > 0;
                  const isLiability = (s.contract_liability || 0) > 0;
                  return (
                    <tr key={s.project_id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50 transition-colors" data-testid={`rev-row-${s.project_id}`}>
                      <td className="px-3 py-2.5">
                        <span className="font-mono font-bold text-[#38bdf8]">{s.project_id}</span>
                        <span className="text-[#E8EDF2] ml-1.5">{s.project_name}</span>
                      </td>
                      <td className="px-3 py-2.5">
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold" style={{ background: `${METHOD_COLORS[s.method] || '#6b7280'}18`, color: METHOD_COLORS[s.method] || '#6b7280' }}>{s.method}</span>
                      </td>
                      <td className="px-3 py-2.5 font-mono text-[#E8EDF2]">{s.total ? fmt(s.total) : 'T&M'}</td>
                      <td className="px-3 py-2.5 text-[#4A5B6E] font-mono">{s.pct_feb != null ? `${s.pct_feb}%` : '—'}</td>
                      <td className="px-3 py-2.5 text-[#E8EDF2] font-mono font-bold">{s.pct_mar != null ? `${s.pct_mar}%` : '—'}</td>
                      <td className="px-3 py-2.5 text-[#4A5B6E] font-mono">{s.rev_feb ? fmt(s.rev_feb) : '—'}</td>
                      <td className="px-3 py-2.5 text-[#00d4aa] font-mono font-bold">{s.rev_mar ? fmt(s.rev_mar) : '—'}</td>
                      <td className="px-3 py-2.5 font-mono text-[#E8EDF2]">{s.billed_to_mar ? fmt(s.billed_to_mar) : '—'}</td>
                      <td className="px-3 py-2.5">
                        {isAsset && <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-[#38bdf8]/10 text-[#38bdf8]">CONTRACT ASSET ₹{(s.contract_asset / 100000).toFixed(2)}L</span>}
                        {isLiability && <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-[#f59e0b]/10 text-[#f59e0b]">DEFERRED REV ₹{(s.contract_liability / 100000).toFixed(2)}L</span>}
                        {!isAsset && !isLiability && <span className="text-[#4A5B6E]">—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="p-3 border-t border-[#1B2D42] flex gap-4 text-[10px]">
            <span className="text-[#38bdf8]">CONTRACT ASSET = Revenue earned {'>'} billed (Unbilled AR on Balance Sheet)</span>
            <span className="text-[#f59e0b]">DEFERRED REV = Billed {'>'} earned (Contract Liability on Balance Sheet)</span>
          </div>
        </div>
      )}

      {/* Disclosure Tab */}
      {tab === 'disclosure' && disc && (
        <div className="space-y-4">
          {/* Disaggregation by Type */}
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <h3 className="text-sm font-bold text-[#E8EDF2] mb-3">Disaggregation by Contract Type</h3>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {disc.disaggregation?.by_type?.map(t => (
                <div key={t.type} className="bg-[#152236] rounded-lg p-3 border border-[#1B2D42]">
                  <p className="text-[10px] font-bold text-[#4A5B6E] uppercase">{t.type}</p>
                  <p className="text-lg font-black text-[#E8EDF2] mt-1">{fmt(t.revenue)}</p>
                  <p className="text-[10px] text-[#4A5B6E]">{t.count} project(s): {t.projects?.join(', ')}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Disaggregation by Geography */}
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <h3 className="text-sm font-bold text-[#E8EDF2] mb-3">Disaggregation by Geography</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#152236] rounded-lg p-4 border border-[#1B2D42]">
                <p className="text-[10px] font-bold text-[#4A5B6E]">DOMESTIC</p>
                <p className="text-lg font-black text-[#E8EDF2] mt-1">{fmt(disc.disaggregation?.by_geography?.domestic)}</p>
              </div>
              <div className="bg-[#152236] rounded-lg p-4 border border-[#fbbf24]/20">
                <p className="text-[10px] font-bold text-[#fbbf24]">EXPORT ({disc.disaggregation?.by_geography?.export_pct}%)</p>
                <p className="text-lg font-black text-[#E8EDF2] mt-1">{fmt(disc.disaggregation?.by_geography?.export)}</p>
              </div>
            </div>
          </div>

          {/* Contract Balances */}
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <h3 className="text-sm font-bold text-[#E8EDF2] mb-3">Contract Balances (B/S as at 31-Mar-2026)</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <h4 className="text-[10px] font-bold text-[#38bdf8] uppercase mb-2">Contract Assets (Unbilled AR) — {fmt(disc.contract_balances?.total_assets)}</h4>
                {disc.contract_balances?.assets?.map(a => (
                  <div key={a.project} className="bg-[#38bdf8]/5 border border-[#38bdf8]/20 rounded p-2 mb-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="font-bold text-[#E8EDF2]">{a.project} — {a.name}</span>
                      <span className="font-mono font-bold text-[#38bdf8]">{fmtFull(a.amount)}</span>
                    </div>
                    <p className="text-[#4A5B6E]">{a.reason}</p>
                  </div>
                ))}
              </div>
              <div>
                <h4 className="text-[10px] font-bold text-[#f59e0b] uppercase mb-2">Contract Liabilities (Deferred Rev) — {fmt(disc.contract_balances?.total_liabilities)}</h4>
                {disc.contract_balances?.liabilities?.map(l => (
                  <div key={l.project} className="bg-[#f59e0b]/5 border border-[#f59e0b]/20 rounded p-2 mb-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="font-bold text-[#E8EDF2]">{l.project} — {l.name}</span>
                      <span className="font-mono font-bold text-[#f59e0b]">{fmtFull(l.amount)}</span>
                    </div>
                    <p className="text-[#4A5B6E]">{l.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RPO */}
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <h3 className="text-sm font-bold text-[#E8EDF2] mb-3">Remaining Performance Obligations (RPO) — {fmt(disc.total_rpo)}</h3>
            <div className="space-y-2">
              {disc.remaining_performance_obligations?.map(r => (
                <div key={r.project} className="flex items-center justify-between bg-[#152236] rounded p-3 text-xs">
                  <div>
                    <span className="font-mono text-[#38bdf8]">{r.project}</span>
                    <span className="text-[#E8EDF2] ml-2 font-bold">{r.name}</span>
                    {r.note && <span className="text-[#4A5B6E] ml-2 text-[10px]">({r.note})</span>}
                  </div>
                  <span className="font-mono font-bold text-[#a78bfa]">{fmtFull(r.remaining_value)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Significant Judgments */}
          <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <h3 className="text-sm font-bold text-[#E8EDF2] mb-3">Significant Judgments & Estimates</h3>
            <ul className="space-y-1.5">
              {disc.significant_judgments?.map((j, i) => (
                <li key={i} className="text-xs text-[#4A5B6E] flex items-start gap-2">
                  <AlertCircle size={12} className="text-[#a78bfa] mt-0.5 shrink-0" />
                  {j}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Transactions Tab */}
      {tab === 'transactions' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="p-4 border-b border-[#1B2D42]">
            <h2 className="text-sm font-bold text-[#E8EDF2]">Revenue-Related Transactions ({transactions.length})</h2>
          </div>
          <div className="space-y-0 max-h-[600px] overflow-y-auto">
            {transactions.map((t, i) => (
              <div key={t.id} className="border-b border-[#1B2D42]/50">
                <div className="px-4 py-3 hover:bg-[#152236]/50 cursor-pointer transition-colors" onClick={() => setExpandedTxn(expandedTxn === i ? null : i)}>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="font-mono text-[#38bdf8] font-bold w-10">{t.id}</span>
                    <span className="text-[#4A5B6E] w-20">{t.date}</span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${t.priority === 'Critical' ? 'bg-[#ef4444]/10 text-[#ef4444]' : t.priority === 'High' ? 'bg-[#f97316]/10 text-[#f97316]' : 'bg-[#1B2D42] text-[#4A5B6E]'}`}>{t.priority}</span>
                    <span className="font-bold text-[#E8EDF2] flex-1">{t.type}</span>
                    <span className="text-[#4A5B6E]">{t.module}</span>
                    {expandedTxn === i ? <ChevronUp size={14} className="text-[#4A5B6E]" /> : <ChevronDown size={14} className="text-[#4A5B6E]" />}
                  </div>
                </div>
                {expandedTxn === i && (
                  <div className="px-4 pb-3 space-y-2">
                    <div className="bg-[#152236] rounded p-3 text-[10px]">
                      <p className="text-[#4A5B6E] font-bold uppercase mb-1">AI Prompt</p>
                      <p className="text-[#E8EDF2] leading-relaxed">{t.prompt}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-[#00d4aa]/5 border border-[#00d4aa]/20 rounded p-2 text-[10px]">
                        <p className="text-[#00d4aa] font-bold uppercase mb-1">Accounting Impact</p>
                        <p className="text-[#E8EDF2]">{t.accounting}</p>
                      </div>
                      <div className="bg-[#a78bfa]/5 border border-[#a78bfa]/20 rounded p-2 text-[10px]">
                        <p className="text-[#a78bfa] font-bold uppercase mb-1">Integrity / Ind AS Check</p>
                        <p className="text-[#E8EDF2]">{t.integrity}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
