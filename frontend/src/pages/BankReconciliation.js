import { useState, useEffect, useRef } from 'react';
import { API } from '../App';
import {
  Upload, CheckCircle2, XCircle, RefreshCw, Landmark, ArrowRightLeft,
  FileSpreadsheet, TrendingUp, TrendingDown, AlertTriangle, Loader2
} from 'lucide-react';

const ACCOUNTS = [
  { id: 'HDFC Bank - Current', label: 'HDFC Bank - Current A/c' },
  { id: 'Axis Bank - Current', label: 'Axis Bank - Current A/c' },
  { id: 'EEFC USD Account', label: 'EEFC USD Account' },
];

export default function BankReconciliation() {
  const [account, setAccount] = useState(ACCOUNTS[0].id);
  const [summary, setSummary] = useState(null);
  const [unmatched, setUnmatched] = useState({ bank_entries: [], book_entries: [] });
  const [selectedBank, setSelectedBank] = useState(null);
  const [selectedBook, setSelectedBook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [matching, setMatching] = useState(false);
  const fileRef = useRef(null);

  const loadData = async (acc) => {
    setLoading(true);
    try {
      const [sumRes, unmRes] = await Promise.all([
        fetch(`${API}/bank-recon/summary?account=${encodeURIComponent(acc)}`),
        fetch(`${API}/bank-recon/unmatched?account=${encodeURIComponent(acc)}`),
      ]);
      if (sumRes.ok) setSummary(await sumRes.json());
      if (unmRes.ok) setUnmatched(await unmRes.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { loadData(account); }, [account]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadMsg('Uploading...');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/bank-recon/statements?account=${encodeURIComponent(account)}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setUploadMsg(`Uploaded ${data.imported || 0} entries, ${data.auto_matched || 0} auto-matched`);
        loadData(account);
      } else {
        setUploadMsg(`Error: ${data.detail || 'Upload failed'}`);
      }
    } catch (err) {
      setUploadMsg(`Error: ${err.message}`);
    }
    if (fileRef.current) fileRef.current.value = '';
  };

  const handleMatch = async () => {
    if (!selectedBank || !selectedBook) return;
    setMatching(true);
    try {
      const res = await fetch(`${API}/bank-recon/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bank_entry_id: selectedBank, book_entry_id: selectedBook }),
      });
      if (res.ok) {
        setSelectedBank(null);
        setSelectedBook(null);
        loadData(account);
      }
    } catch {}
    setMatching(false);
  };

  const fmt = (n) => {
    if (n == null) return '--';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
  };

  const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' }) : '--';

  return (
    <div className="space-y-5" data-testid="bank-reconciliation-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#60a5fa]/10 border border-[#60a5fa]/20 flex items-center justify-center">
            <Landmark size={20} className="text-[#60a5fa]" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-[#E8EDF2]">Bank Reconciliation</h1>
            <p className="text-xs text-[#4A5B6E]">Match bank statements with book entries</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Account Selector */}
          <select
            value={account}
            onChange={e => { setAccount(e.target.value); setSelectedBank(null); setSelectedBook(null); }}
            data-testid="account-selector"
            className="px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-xs text-[#E8EDF2] focus:outline-none focus:border-[#60a5fa]/50"
          >
            {ACCOUNTS.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
          </select>

          {/* CSV Upload */}
          <input type="file" ref={fileRef} onChange={handleUpload} accept=".csv" className="hidden" />
          <button
            onClick={() => fileRef.current?.click()}
            data-testid="upload-csv-btn"
            className="flex items-center gap-1.5 px-3 py-2 bg-[#22c55e]/10 border border-[#22c55e]/25 rounded-lg text-xs font-bold text-[#22c55e] hover:bg-[#22c55e]/20 transition-colors"
          >
            <Upload size={14} /> Upload Statement
          </button>

          <button onClick={() => loadData(account)} data-testid="refresh-btn"
            className="p-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-[#4A5B6E] hover:text-[#E8EDF2] transition-colors">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {uploadMsg && (
        <div className={`px-3 py-2 rounded-lg text-xs font-medium ${uploadMsg.startsWith('Error') ? 'bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20' : 'bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20'}`} data-testid="upload-message">
          {uploadMsg}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="recon-summary">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-xl p-3">
            <p className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Book Balance</p>
            <p className="text-base font-bold text-[#E8EDF2] mt-1">{fmt(summary.book_balance)}</p>
          </div>
          <div className="bg-[#152236] border border-[#1B2D42] rounded-xl p-3">
            <p className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Bank Balance</p>
            <p className="text-base font-bold text-[#E8EDF2] mt-1">{fmt(summary.bank_balance)}</p>
          </div>
          <div className="bg-[#152236] border border-[#1B2D42] rounded-xl p-3">
            <p className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Difference</p>
            <p className={`text-base font-bold mt-1 ${summary.difference === 0 ? 'text-[#22c55e]' : 'text-[#f59e0b]'}`}>
              {fmt(summary.difference)}
            </p>
          </div>
          <div className="bg-[#152236] border border-[#1B2D42] rounded-xl p-3">
            <p className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Matched</p>
            <p className="text-base font-bold text-[#22c55e] mt-1">{summary.matched_bank_count ?? 0}</p>
          </div>
          <div className="bg-[#152236] border border-[#1B2D42] rounded-xl p-3">
            <p className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider">Unmatched</p>
            <p className="text-base font-bold text-[#f59e0b] mt-1">{summary.unmatched_bank_count ?? 0}</p>
          </div>
        </div>
      )}

      {/* Match Action Bar */}
      {(selectedBank || selectedBook) && (
        <div className="flex items-center gap-3 p-3 bg-[#00d4aa]/5 border border-[#00d4aa]/20 rounded-xl" data-testid="match-bar">
          <ArrowRightLeft size={16} className="text-[#00d4aa]" />
          <span className="text-xs text-[#E8EDF2]">
            {selectedBank && selectedBook ? 'Ready to match selected entries' : 'Select one entry from each table to match'}
          </span>
          <div className="flex-1" />
          {selectedBank && selectedBook && (
            <button onClick={handleMatch} disabled={matching} data-testid="match-btn"
              className="flex items-center gap-1.5 px-4 py-2 bg-[#00d4aa]/15 border border-[#00d4aa]/30 rounded-lg text-xs font-bold text-[#00d4aa] hover:bg-[#00d4aa]/25 transition-colors disabled:opacity-50">
              {matching ? <Loader2 size={13} className="animate-spin" /> : <CheckCircle2 size={13} />}
              Match Selected
            </button>
          )}
          <button onClick={() => { setSelectedBank(null); setSelectedBook(null); }}
            className="px-3 py-2 text-xs text-[#4A5B6E] hover:text-[#ef4444] transition-colors" data-testid="clear-selection-btn">
            Clear
          </button>
        </div>
      )}

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Bank Entries */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-xl overflow-hidden" data-testid="bank-entries-table">
          <div className="px-4 py-3 border-b border-[#1B2D42] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingDown size={14} className="text-[#60a5fa]" />
              <h3 className="text-xs font-bold text-[#E8EDF2]">Unmatched Bank Entries</h3>
            </div>
            <span className="text-[10px] font-bold text-[#4A5B6E] bg-[#0D1B2A] px-2 py-0.5 rounded-full">
              {unmatched.bank_entries?.length || 0}
            </span>
          </div>
          <div className="overflow-y-auto max-h-80">
            {(!unmatched.bank_entries || unmatched.bank_entries.length === 0) ? (
              <p className="text-xs text-[#4A5B6E] text-center py-8">No unmatched bank entries</p>
            ) : (
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider border-b border-[#1B2D42]">
                    <td className="px-3 py-2">Date</td>
                    <td className="px-3 py-2">Description</td>
                    <td className="px-3 py-2 text-right">Amount</td>
                  </tr>
                </thead>
                <tbody>
                  {unmatched.bank_entries.map(e => (
                    <tr key={e.id} onClick={() => setSelectedBank(selectedBank === e.id ? null : e.id)}
                      data-testid={`bank-entry-${e.id}`}
                      className={`cursor-pointer transition-colors border-b border-[#1B2D42]/50 ${selectedBank === e.id ? 'bg-[#60a5fa]/10 border-l-2 border-l-[#60a5fa]' : 'hover:bg-[#0D1B2A]'}`}>
                      <td className="px-3 py-2 text-[#7A8BA0]">{fmtDate(e.date)}</td>
                      <td className="px-3 py-2 text-[#E8EDF2] truncate max-w-[200px]">{e.description || e.narration || '--'}</td>
                      <td className={`px-3 py-2 text-right font-mono ${(e.debit || e.amount > 0) ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>
                        {fmt(e.debit || e.credit || e.amount || 0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Book Entries */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-xl overflow-hidden" data-testid="book-entries-table">
          <div className="px-4 py-3 border-b border-[#1B2D42] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp size={14} className="text-[#a78bfa]" />
              <h3 className="text-xs font-bold text-[#E8EDF2]">Unmatched Book Entries</h3>
            </div>
            <span className="text-[10px] font-bold text-[#4A5B6E] bg-[#0D1B2A] px-2 py-0.5 rounded-full">
              {unmatched.book_entries?.length || 0}
            </span>
          </div>
          <div className="overflow-y-auto max-h-80">
            {(!unmatched.book_entries || unmatched.book_entries.length === 0) ? (
              <p className="text-xs text-[#4A5B6E] text-center py-8">No unmatched book entries</p>
            ) : (
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-[10px] font-bold text-[#4A5B6E] uppercase tracking-wider border-b border-[#1B2D42]">
                    <td className="px-3 py-2">Date</td>
                    <td className="px-3 py-2">Description</td>
                    <td className="px-3 py-2 text-right">Debit</td>
                    <td className="px-3 py-2 text-right">Credit</td>
                  </tr>
                </thead>
                <tbody>
                  {unmatched.book_entries.map(e => (
                    <tr key={e.id} onClick={() => setSelectedBook(selectedBook === e.id ? null : e.id)}
                      data-testid={`book-entry-${e.id}`}
                      className={`cursor-pointer transition-colors border-b border-[#1B2D42]/50 ${selectedBook === e.id ? 'bg-[#a78bfa]/10 border-l-2 border-l-[#a78bfa]' : 'hover:bg-[#0D1B2A]'}`}>
                      <td className="px-3 py-2 text-[#7A8BA0]">{fmtDate(e.posting_date || e.date)}</td>
                      <td className="px-3 py-2 text-[#E8EDF2] truncate max-w-[200px]">{e.description || '--'}</td>
                      <td className="px-3 py-2 text-right font-mono text-[#22c55e]">{e.debit ? fmt(e.debit) : '--'}</td>
                      <td className="px-3 py-2 text-right font-mono text-[#ef4444]">{e.credit ? fmt(e.credit) : '--'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
