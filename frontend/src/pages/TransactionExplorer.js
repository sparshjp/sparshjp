import { useState, useEffect, useMemo } from 'react';
import { API } from '../App';
import { Search, Copy, Check, ChevronDown, ChevronUp, Filter } from 'lucide-react';

const MOD_META = {
  CRM: { color: '#a78bfa', icon: 'CRM' },
  Projects: { color: '#38bdf8', icon: 'PRJ' },
  Timesheets: { color: '#00d4aa', icon: 'TS' },
  Buying: { color: '#fbbf24', icon: 'BUY' },
  Selling: { color: '#4ade80', icon: 'SEL' },
  HR: { color: '#f472b6', icon: 'HR' },
  Accounting: { color: '#60a5fa', icon: 'ACC' },
  Reports: { color: '#94a3b8', icon: 'RPT' },
};
const PRI_COLOR = { Critical: '#ef4444', High: '#f97316', Normal: '#64748b' };

export default function TransactionExplorer() {
  const [data, setData] = useState({ transactions: [], module_counts: {} });
  const [module, setModule] = useState('All');
  const [priority, setPriority] = useState('All');
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState(null);
  const [copied, setCopied] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/revenue/all-transactions`).then(r => r.json()).then(d => { setData(d); setLoading(false); });
  }, []);

  const filtered = useMemo(() => {
    return data.transactions.filter(t => {
      if (module !== 'All' && t.module !== module) return false;
      if (priority !== 'All' && t.priority !== priority) return false;
      if (search) {
        const s = search.toLowerCase();
        if (!t.prompt?.toLowerCase().includes(s) && !t.type?.toLowerCase().includes(s) && !t.id?.toLowerCase().includes(s)) return false;
      }
      return true;
    });
  }, [data.transactions, module, priority, search]);

  const copyPrompt = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading transactions...</div>;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6" data-testid="txn-explorer">
      <div>
        <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="txn-explorer-title">Transaction Explorer</h1>
        <p className="text-[#4A5B6E] text-sm mt-1">Nexora Digital Solutions — {data.total} ERP Transactions — March 2026</p>
      </div>

      {/* Module Chips */}
      <div className="flex flex-wrap gap-2">
        {Object.entries(data.module_counts).map(([mod, count]) => {
          const mc = MOD_META[mod] || { color: '#94a3b8', icon: mod.slice(0, 3) };
          return (
            <button key={mod} onClick={() => setModule(module === mod ? 'All' : mod)} data-testid={`mod-chip-${mod}`}
              className={`px-3 py-1.5 rounded-md text-[10px] font-bold border transition-all ${module === mod ? `border-[${mc.color}]` : 'border-[#1B2D42]'}`}
              style={{ background: module === mod ? `${mc.color}15` : '#0A1628', color: module === mod ? mc.color : '#4A5B6E', borderColor: module === mod ? mc.color : '#1B2D42' }}>
              {mc.icon} {count} {mod}
            </button>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap items-center">
        {['All', 'Critical', 'High', 'Normal'].map(p => (
          <button key={p} onClick={() => setPriority(p)} data-testid={`pri-${p}`}
            className="px-3 py-1 rounded-full text-[10px] font-bold border transition-all"
            style={{ background: priority === p ? `${PRI_COLOR[p] || '#00d4aa'}15` : 'transparent', color: priority === p ? (PRI_COLOR[p] || '#00d4aa') : '#4A5B6E', borderColor: priority === p ? (PRI_COLOR[p] || '#00d4aa') : '#1B2D42' }}>
            {p}
          </button>
        ))}
        <div className="flex-1 min-w-[200px] relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#4A5B6E]" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search transactions..." data-testid="txn-search"
            className="w-full pl-9 pr-3 py-1.5 bg-[#0A1628] border border-[#1B2D42] rounded-lg text-xs text-[#E8EDF2] focus:outline-none focus:border-[#00d4aa]/50" />
        </div>
        <span className="text-[10px] text-[#4A5B6E] font-bold">{filtered.length}/{data.transactions.length} shown</span>
      </div>

      {/* Transactions List */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="max-h-[calc(100vh-320px)] overflow-y-auto">
          {filtered.map(t => {
            const mc = MOD_META[t.module] || { color: '#94a3b8', icon: '?' };
            const isOpen = expanded === t.id;
            return (
              <div key={t.id} className="border-b border-[#1B2D42]/50" data-testid={`txn-${t.id}`}>
                <div className="px-4 py-3 hover:bg-[#152236]/30 cursor-pointer transition-colors flex items-start gap-3" onClick={() => setExpanded(isOpen ? null : t.id)}>
                  <div className="w-8 h-8 rounded flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5" style={{ background: `${mc.color}15`, color: mc.color }}>{mc.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono text-[#38bdf8] text-[10px] font-bold">{t.id}</span>
                      <span className="text-[#4A5B6E] text-[10px]">{t.date}</span>
                      <span className="text-[10px] font-bold" style={{ color: mc.color }}>{t.module}</span>
                      <span className="px-1.5 py-0.5 rounded text-[8px] font-bold" style={{ background: `${PRI_COLOR[t.priority] || '#64748b'}18`, color: PRI_COLOR[t.priority] || '#64748b' }}>{t.priority}</span>
                    </div>
                    <p className="text-xs font-bold text-[#E8EDF2]">{t.type}</p>
                    {!isOpen && <p className="text-[10px] text-[#4A5B6E] mt-0.5 truncate">{t.prompt?.slice(0, 120)}...</p>}
                  </div>
                  <div className="text-[#4A5B6E] shrink-0">{isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</div>
                </div>
                {isOpen && (
                  <div className="px-4 pb-4 space-y-3">
                    <div className="bg-[#152236] rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[9px] font-bold uppercase text-[#00d4aa] tracking-wider">AI Prompt — Paste into Kairos Bot</span>
                        <button onClick={(e) => { e.stopPropagation(); copyPrompt(t.id, t.prompt); }} data-testid={`copy-${t.id}`}
                          className="flex items-center gap-1 px-2 py-1 rounded text-[9px] font-bold border transition-all"
                          style={{ background: copied === t.id ? '#065f46' : `${mc.color}15`, color: copied === t.id ? '#34d399' : mc.color, borderColor: copied === t.id ? '#34d399' : mc.color }}>
                          {copied === t.id ? <><Check size={10} /> COPIED</> : <><Copy size={10} /> COPY PROMPT</>}
                        </button>
                      </div>
                      <p className="text-[11px] text-[#E8EDF2] leading-relaxed whitespace-pre-wrap">{t.prompt}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-[#00d4aa]/5 border border-[#00d4aa]/20 rounded-lg p-3">
                        <p className="text-[9px] font-bold uppercase text-[#00d4aa] mb-1">Accounting Impact</p>
                        <p className="text-[10px] text-[#E8EDF2] leading-relaxed">{t.accounting}</p>
                      </div>
                      <div className="bg-[#a78bfa]/5 border border-[#a78bfa]/20 rounded-lg p-3">
                        <p className="text-[9px] font-bold uppercase text-[#a78bfa] mb-1">Integrity / Ind AS Check</p>
                        <p className="text-[10px] text-[#E8EDF2] leading-relaxed">{t.integrity}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {filtered.length === 0 && (
            <div className="p-12 text-center text-[#4A5B6E]">
              <Search size={32} className="mx-auto mb-3 opacity-30" />
              <p className="text-sm font-bold">No matching transactions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
