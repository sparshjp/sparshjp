import React, { useState, useEffect } from 'react';
import { Clock, TrendingDown, TrendingUp, ChevronDown, ChevronRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (!n) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

const BUCKET_COLORS = {
  '0-30': { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
  '30-60': { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
  '60-90': { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/20' },
  '90+': { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
};

function BucketCard({ label, amount, total }) {
  const pct = total > 0 ? Math.round((amount / total) * 100) : 0;
  const colors = BUCKET_COLORS[label] || BUCKET_COLORS['0-30'];
  return (
    <div className={`${colors.bg} border ${colors.border} rounded-lg p-4`}>
      <p className={`text-xl font-bold font-mono ${colors.text}`}>{formatINR(amount)}</p>
      <div className="flex items-center justify-between mt-1">
        <p className="text-[10px] text-[#4A5B6E] tracking-wider uppercase">{label} days</p>
        <span className={`text-[10px] font-bold ${colors.text}`}>{pct}%</span>
      </div>
      <div className="w-full bg-[#0D1B2A] rounded-full h-1 mt-2">
        <div className={`h-1 rounded-full ${label === '0-30' ? 'bg-emerald-400' : label === '30-60' ? 'bg-amber-400' : label === '60-90' ? 'bg-orange-400' : 'bg-red-400'}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function AgingTable({ data, entityKey, entityLabel }) {
  const [expanded, setExpanded] = useState(null);
  const entities = data?.[entityKey] || [];
  return (
    <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#0D1B2A]/50">
          <th className="py-2.5 px-4 w-8"></th>
          <th className="py-2.5 px-4 text-left">{entityLabel}</th>
          <th className="py-2.5 px-4 text-right">0-30</th>
          <th className="py-2.5 px-4 text-right">30-60</th>
          <th className="py-2.5 px-4 text-right">60-90</th>
          <th className="py-2.5 px-4 text-right">90+</th>
          <th className="py-2.5 px-4 text-right">Total</th>
        </tr></thead>
        <tbody>
          {entities.length === 0 ? (
            <tr><td colSpan={7} className="py-8 text-center text-[#4A5B6E]">No outstanding amounts</td></tr>
          ) : entities.map((e, i) => {
            const key = e.vendor || e.customer;
            const isOpen = expanded === key;
            const relatedDetails = (data?.details || []).filter(d => (d.vendor || d.customer) === key);
            return (
              <React.Fragment key={i}>
                <tr className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20 cursor-pointer" onClick={() => setExpanded(isOpen ? null : key)}>
                  <td className="py-2.5 px-4 text-[#4A5B6E]">{isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}</td>
                  <td className="py-2.5 px-4 text-xs text-[#E8EDF2] font-medium">{key}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-emerald-400">{e['0-30'] ? formatINR(e['0-30']) : '—'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-amber-400">{e['30-60'] ? formatINR(e['30-60']) : '—'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-orange-400">{e['60-90'] ? formatINR(e['60-90']) : '—'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs text-red-400">{e['90+'] ? formatINR(e['90+']) : '—'}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-xs font-bold text-[#E8EDF2]">{formatINR(e.total)}</td>
                </tr>
                {isOpen && relatedDetails.map((d, j) => (
                  <tr key={j} className="bg-[#0D1B2A]/40 border-b border-[#1B2D42]/20">
                    <td></td>
                    <td className="py-1.5 px-4 text-[#00C9A7] font-mono text-[11px] pl-10">{d.invoice_number}</td>
                    <td colSpan={3} className="py-1.5 px-4 text-[#4A5B6E] text-[11px]">
                      Date: {d.invoice_date} | {d.days} days | Inv: {formatINR(d.grand_total)} | Paid: {formatINR(d.amount_paid)}
                    </td>
                    <td className="py-1.5 px-4 text-right">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${BUCKET_COLORS[d.bucket]?.text} ${BUCKET_COLORS[d.bucket]?.bg} border ${BUCKET_COLORS[d.bucket]?.border}`}>{d.bucket}d</span>
                    </td>
                    <td className="py-1.5 px-4 text-right font-mono text-[11px] font-bold text-[#E8EDF2]">{formatINR(d.outstanding)}</td>
                  </tr>
                ))}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function AgingReport() {
  const [tab, setTab] = useState('payables');
  const [apData, setApData] = useState(null);
  const [arData, setArData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/aging/payables`).then(r => r.json()),
      fetch(`${API}/aging/receivables`).then(r => r.json()),
    ]).then(([ap, ar]) => { setApData(ap); setArData(ar); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-[#4A5B6E] py-12 text-center">Loading aging report...</div>;

  const data = tab === 'payables' ? apData : arData;
  const buckets = data?.buckets || {};
  const total = data?.total_outstanding || 0;

  return (
    <div className="space-y-5" data-testid="aging-report-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#00C9A7]/10 flex items-center justify-center">
            <Clock className="w-5 h-5 text-[#00C9A7]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">AP / AR Aging</h1>
            <p className="text-[#4A5B6E] text-sm">Outstanding balances as of {data?.as_of}</p>
          </div>
        </div>
      </div>

      {/* Tab toggle */}
      <div className="flex gap-2" data-testid="aging-tabs">
        <button onClick={() => setTab('payables')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-colors ${tab === 'payables' ? 'bg-[#FF4D6A]/10 text-[#FF4D6A] border border-[#FF4D6A]/20' : 'bg-[#152236] text-[#4A5B6E] border border-[#1B2D42] hover:text-[#7A8BA0]'}`}>
          <TrendingDown className="w-4 h-4" /> Accounts Payable
          <span className="font-mono text-xs ml-1">{formatINR(apData?.total_outstanding)}</span>
        </button>
        <button onClick={() => setTab('receivables')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-colors ${tab === 'receivables' ? 'bg-[#00C9A7]/10 text-[#00C9A7] border border-[#00C9A7]/20' : 'bg-[#152236] text-[#4A5B6E] border border-[#1B2D42] hover:text-[#7A8BA0]'}`}>
          <TrendingUp className="w-4 h-4" /> Accounts Receivable
          <span className="font-mono text-xs ml-1">{formatINR(arData?.total_outstanding)}</span>
        </button>
      </div>

      {/* Bucket cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="aging-buckets">
        {['0-30', '30-60', '60-90', '90+'].map(b => (
          <BucketCard key={b} label={b} amount={buckets[b] || 0} total={total} />
        ))}
      </div>

      {/* Total */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 flex items-center justify-between">
        <span className="text-sm text-[#7A8BA0]">Total Outstanding</span>
        <span className="text-2xl font-bold font-mono text-[#E8EDF2]">{formatINR(total)}</span>
      </div>

      {/* Aging table */}
      {tab === 'payables' ? (
        <AgingTable data={apData} entityKey="by_vendor" entityLabel="Vendor" />
      ) : (
        <AgingTable data={arData} entityKey="by_customer" entityLabel="Customer" />
      )}
    </div>
  );
}
