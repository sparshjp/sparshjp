import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, ArrowRightLeft, Sparkles } from 'lucide-react';
import AiEntryModal from '../components/AiEntryModal';

export default function ForexPage() {
  const [tab, setTab] = useState('rates');
  const [rates, setRates] = useState({});
  const [transactions, setTransactions] = useState([]);
  const [revaluation, setRevaluation] = useState({ transactions: [], total_unrealized_gain_loss: 0 });
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [showAiModal, setShowAiModal] = useState(false);

  const load = useCallback(async () => {
    try {
      const [rt, tx, rv] = await Promise.all([
        fetch(`${API}/forex/rates`).then(r => r.json()),
        fetch(`${API}/forex/transactions`).then(r => r.json()),
        fetch(`${API}/forex/revaluation`).then(r => r.json()),
      ]);
      setRates(rt || {});
      setTransactions(Array.isArray(tx) ? tx : []);
      setRevaluation(rv || { transactions: [], total_unrealized_gain_loss: 0 });
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const fetchLiveRates = async () => {
    setFetching(true);
    try { await fetch(`${API}/forex/rates/fetch-live`, { method: 'POST' }); load(); } catch {}
    setFetching(false);
  };

  const createTransaction = async (data) => {
    const res = await fetch(`${API}/forex/transactions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to create forex transaction');
    load();
  };

  const settle = async (txnId) => {
    const rate = prompt('Enter settlement rate:');
    if (!rate) return;
    await fetch(`${API}/forex/transactions/${txnId}/settle`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ settlement_rate: Number(rate) }) });
    load();
  };

  const rateEntries = Object.entries(rates.rates || {});

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading forex data...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="forex-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="forex-title">Multi-Currency & Forex</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Exchange rates, gain/loss tracking & revaluation</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-forex-txn-btn"><Sparkles size={16} /> New Transaction</button>
          <button onClick={fetchLiveRates} disabled={fetching} className="px-3 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm hover:bg-[#152236] flex items-center gap-1" data-testid="fetch-rates-btn"><RefreshCw size={14} className={fetching ? 'animate-spin' : ''} /> Live Rates</button>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Currencies', value: rateEntries.length, icon: DollarSign, color: '#38bdf8' },
          { label: 'Open Transactions', value: transactions.filter(t => !t.settled).length, icon: ArrowRightLeft, color: '#f59e0b' },
          { label: 'Settled', value: transactions.filter(t => t.settled).length, icon: TrendingUp, color: '#22c55e' },
          { label: 'Unrealized P&L', value: `${revaluation.total_unrealized_gain_loss >= 0 ? '+' : ''}${revaluation.total_unrealized_gain_loss?.toLocaleString('en-IN')}`, icon: revaluation.total_unrealized_gain_loss >= 0 ? TrendingUp : TrendingDown, color: revaluation.total_unrealized_gain_loss >= 0 ? '#22c55e' : '#ef4444' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit">
        {['rates', 'transactions', 'revaluation'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`tab-${t}`}>{t}</button>
        ))}
      </div>

      {tab === 'rates' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-[#4A5B6E]">Base: INR | As of: {rates.date || '-'} | Source: {rates.source || 'default'}</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {rateEntries.map(([cur, rate]) => (
              <div key={cur} className="bg-[#152236] rounded-lg p-3 text-center">
                <p className="text-lg font-bold text-[#E8EDF2]">{cur}</p>
                <p className="text-sm text-[#00C9A7]">{rate?.toFixed(2)}</p>
                <p className="text-xs text-[#4A5B6E]">INR per {cur}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'transactions' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          {transactions.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No forex transactions</p> : (
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
                <th className="text-left p-3">Reference</th><th className="text-center p-3">Currency</th><th className="text-right p-3">Foreign Amt</th><th className="text-right p-3">Booking Rate</th><th className="text-right p-3">INR Value</th><th className="text-right p-3">Gain/Loss</th><th className="text-center p-3">Status</th>
              </tr></thead>
              <tbody>
                {transactions.map(t => (
                  <tr key={t.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`forex-txn-${t.id}`}>
                    <td className="p-3 text-[#E8EDF2]">{t.reference_name || t.type}</td>
                    <td className="p-3 text-center text-[#7A8BA0]">{t.currency}</td>
                    <td className="p-3 text-right text-[#E8EDF2]">{t.foreign_amount?.toLocaleString()}</td>
                    <td className="p-3 text-right text-[#7A8BA0]">{t.booking_rate}</td>
                    <td className="p-3 text-right text-[#E8EDF2]">{t.booking_inr?.toLocaleString('en-IN')}</td>
                    <td className="p-3 text-right font-bold" style={{ color: (t.forex_gain_loss || 0) >= 0 ? '#22c55e' : '#ef4444' }}>{t.forex_gain_loss != null ? `${t.forex_gain_loss >= 0 ? '+' : ''}${t.forex_gain_loss.toLocaleString('en-IN')}` : '-'}</td>
                    <td className="p-3 text-center">
                      {t.settled ? <span className="px-2 py-0.5 rounded-full text-xs text-[#22c55e] bg-[#22c55e]/15 font-bold">Settled</span>
                        : <button onClick={() => settle(t.id)} className="px-2 py-0.5 rounded-full text-xs text-[#f59e0b] bg-[#f59e0b]/15 font-bold hover:bg-[#f59e0b]/25" data-testid={`settle-${t.id}`}>Settle</button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'revaluation' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
          <h2 className="text-sm font-bold text-[#E8EDF2] mb-3">Unrealized Gain/Loss — Mark-to-Market</h2>
          <p className="text-2xl font-bold mb-4" style={{ color: revaluation.total_unrealized_gain_loss >= 0 ? '#22c55e' : '#ef4444' }}>
            {revaluation.total_unrealized_gain_loss >= 0 ? '+' : ''}{revaluation.total_unrealized_gain_loss?.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
          </p>
          {revaluation.transactions?.length > 0 && (
            <div className="space-y-2">
              {revaluation.transactions.map(t => (
                <div key={t.id} className="flex items-center justify-between bg-[#152236] rounded p-3 text-sm">
                  <span className="text-[#E8EDF2]">{t.reference_name} — {t.currency} {t.foreign_amount?.toLocaleString()}</span>
                  <span className="font-bold" style={{ color: (t.unrealized_gain_loss || 0) >= 0 ? '#22c55e' : '#ef4444' }}>{t.unrealized_gain_loss >= 0 ? '+' : ''}{t.unrealized_gain_loss?.toLocaleString('en-IN')}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <AiEntryModal open={showAiModal} onClose={() => setShowAiModal(false)} module="forex_transaction" title="New Forex Transaction" placeholder='e.g. "Invoice to TechCorp USD 25000 at rate 84.50"' onSubmit={createTransaction} />
    </div>
  );
}
