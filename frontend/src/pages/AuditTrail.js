import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Download, Search, ChevronDown, ChevronRight, Filter, Clock, FileText } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const ACTION_COLORS = {
  CREATE: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
  UPDATE: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
  DELETE: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
  SUBMIT: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20' },
  CANCEL: { bg: 'bg-red-500/10', text: 'text-red-300', border: 'border-red-500/20' },
  POST: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20' },
};

function ActionBadge({ action }) {
  const colors = ACTION_COLORS[action] || { bg: 'bg-[#1B2D42]', text: 'text-[#7A8BA0]', border: 'border-[#1B2D42]' };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${colors.bg} ${colors.text} border ${colors.border}`}
      data-testid={`action-badge-${action?.toLowerCase()}`}>
      {action}
    </span>
  );
}

function formatTimestamp(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) +
      ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return ts;
  }
}

function ChangesDiff({ changes }) {
  if (!changes || changes.length === 0) return <span className="text-[#4A5B6E] text-xs">No field changes</span>;
  return (
    <div className="space-y-1.5" data-testid="changes-diff">
      {changes.map((c, i) => (
        <div key={i} className="flex items-start gap-2 text-xs">
          <span className="font-mono text-[#00C9A7] min-w-[120px] flex-shrink-0">{c.field}</span>
          <div className="flex items-center gap-1.5 flex-wrap">
            {c.old_value !== null && c.old_value !== undefined && (
              <span className="px-1.5 py-0.5 bg-red-500/10 text-red-400 rounded font-mono line-through text-[11px]">
                {String(c.old_value).substring(0, 80)}
              </span>
            )}
            <span className="text-[#4A5B6E]">&rarr;</span>
            <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded font-mono text-[11px]">
              {String(c.new_value).substring(0, 80)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

function AuditRow({ entry }) {
  const [expanded, setExpanded] = useState(false);
  const hasDetails = (entry.changes && entry.changes.length > 0) || entry.snapshot || entry.notes;
  return (
    <>
      <tr
        className={`border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20 transition-colors ${hasDetails ? 'cursor-pointer' : ''}`}
        onClick={() => hasDetails && setExpanded(!expanded)}
        data-testid="audit-row"
      >
        <td className="px-3 py-2.5 text-[#4A5B6E]">
          {hasDetails ? (expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />) : <span className="w-3.5 inline-block" />}
        </td>
        <td className="px-3 py-2.5 text-xs text-[#7A8BA0] font-mono whitespace-nowrap">{formatTimestamp(entry.timestamp)}</td>
        <td className="px-3 py-2.5"><ActionBadge action={entry.action} /></td>
        <td className="px-3 py-2.5 text-xs text-[#E8EDF2]">{entry.document_type}</td>
        <td className="px-3 py-2.5 text-xs text-[#00C9A7] font-mono">{entry.document_number}</td>
        <td className="px-3 py-2.5 text-xs text-[#7A8BA0] max-w-[300px] truncate">{entry.notes}</td>
        <td className="px-3 py-2.5 text-xs text-[#4A5B6E]">{entry.user}</td>
      </tr>
      {expanded && (
        <tr className="bg-[#0D1B2A]/50">
          <td colSpan={7} className="px-6 py-4">
            <div className="space-y-3">
              {entry.changes && entry.changes.length > 0 && (
                <div>
                  <p className="text-[10px] font-bold text-[#7A8BA0] tracking-wider uppercase mb-2">Field Changes (Before &rarr; After)</p>
                  <ChangesDiff changes={entry.changes} />
                </div>
              )}
              {entry.snapshot && (
                <div>
                  <p className="text-[10px] font-bold text-[#7A8BA0] tracking-wider uppercase mb-2">Document Snapshot</p>
                  <pre className="text-[11px] text-[#7A8BA0] bg-[#0D1B2A] border border-[#1B2D42] rounded-lg p-3 overflow-x-auto max-h-48 font-mono">
                    {JSON.stringify(entry.snapshot, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function AuditTrail() {
  const [entries, setEntries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [docTypes, setDocTypes] = useState([]);

  // Filters
  const [filterDocType, setFilterDocType] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const [filterSearch, setFilterSearch] = useState('');
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('limit', PAGE_SIZE);
      params.set('skip', page * PAGE_SIZE);
      if (filterDocType) params.set('document_type', filterDocType);
      if (filterAction) params.set('action', filterAction);
      if (filterDateFrom) params.set('date_from', filterDateFrom);
      if (filterDateTo) params.set('date_to', filterDateTo);
      if (filterSearch) params.set('search', filterSearch);

      const res = await fetch(`${API}/api/audit-trail?${params}`);
      const data = await res.json();
      setEntries(data.entries || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [page, filterDocType, filterAction, filterDateFrom, filterDateTo, filterSearch]);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    fetch(`${API}/api/audit-trail/stats`).then(r => r.json()).then(setStats).catch(() => {});
    fetch(`${API}/api/audit-trail/document-types`).then(r => r.json()).then(setDocTypes).catch(() => {});
  }, []);

  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      if (filterDocType) params.set('document_type', filterDocType);
      if (filterAction) params.set('action', filterAction);
      if (filterDateFrom) params.set('date_from', filterDateFrom);
      if (filterDateTo) params.set('date_to', filterDateTo);
      const r = await fetch(`${API}/api/audit-trail/export?${params}`);
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'audit_trail.csv'; a.click();
      URL.revokeObjectURL(url);
      toast.success('Audit trail exported');
    } catch { toast.error('Export failed'); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const ACTIONS = ['CREATE', 'UPDATE', 'DELETE', 'SUBMIT', 'CANCEL', 'POST'];

  return (
    <div className="space-y-5" data-testid="audit-trail-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#00C9A7]/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-[#00C9A7]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">Audit Trail</h1>
            <p className="text-[#4A5B6E] text-sm">Immutable record of all transactions &mdash; Companies Act 2013, Rule 3(1)</p>
          </div>
        </div>
        <button data-testid="audit-export-btn" onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-bold transition-colors">
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {/* Stats cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="audit-stats">
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
            <p className="text-2xl font-bold font-mono text-[#E8EDF2]">{stats.total_entries}</p>
            <p className="text-[10px] text-[#4A5B6E] tracking-wider uppercase mt-1">Total Entries</p>
          </div>
          {Object.entries(stats.by_action || {}).slice(0, 3).map(([action, count]) => (
            <div key={action} className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 text-center">
              <p className="text-2xl font-bold font-mono text-[#E8EDF2]">{count}</p>
              <p className="text-[10px] tracking-wider uppercase mt-1"><ActionBadge action={action} /></p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4" data-testid="audit-filters">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-3.5 h-3.5 text-[#00C9A7]" />
          <span className="text-[10px] font-bold text-[#7A8BA0] tracking-wider uppercase">Filters</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#4A5B6E]" />
            <input data-testid="audit-search" value={filterSearch} onChange={e => { setFilterSearch(e.target.value); setPage(0); }}
              placeholder="Search..." className="w-full pl-8 pr-3 py-2 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg text-xs text-[#E8EDF2] placeholder-[#4A5B6E] outline-none focus:border-[#00C9A7]" />
          </div>
          <select data-testid="audit-filter-doctype" value={filterDocType} onChange={e => { setFilterDocType(e.target.value); setPage(0); }}
            className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]">
            <option value="">All Document Types</option>
            {docTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <select data-testid="audit-filter-action" value={filterAction} onChange={e => { setFilterAction(e.target.value); setPage(0); }}
            className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]">
            <option value="">All Actions</option>
            {ACTIONS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
          <input data-testid="audit-filter-from" type="date" value={filterDateFrom} onChange={e => { setFilterDateFrom(e.target.value); setPage(0); }}
            className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]" />
          <input data-testid="audit-filter-to" type="date" value={filterDateTo} onChange={e => { setFilterDateTo(e.target.value); setPage(0); }}
            className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-xs text-[#E8EDF2] outline-none focus:border-[#00C9A7]" />
          <button onClick={() => { setFilterDocType(''); setFilterAction(''); setFilterDateFrom(''); setFilterDateTo(''); setFilterSearch(''); setPage(0); }}
            className="text-xs text-[#7A8BA0] hover:text-[#00C9A7] transition-colors">Clear All</button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm" data-testid="audit-table">
            <thead>
              <tr className="bg-[#0D1B2A] border-b border-[#1B2D42]">
                <th className="px-3 py-2.5 w-8"></th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">Timestamp</th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">Action</th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">Document Type</th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">Document #</th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">Notes</th>
                <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0]">User</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="py-12 text-center text-[#4A5B6E]">Loading audit trail...</td></tr>
              ) : entries.length === 0 ? (
                <tr><td colSpan={7} className="py-12 text-center">
                  <div className="space-y-2">
                    <Clock className="w-8 h-8 text-[#1B2D42] mx-auto" />
                    <p className="text-[#4A5B6E] text-sm">No audit entries yet</p>
                    <p className="text-[#4A5B6E] text-xs">Create a transaction to see the audit trail</p>
                  </div>
                </td></tr>
              ) : entries.map(e => <AuditRow key={e.id} entry={e} />)}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-[#1B2D42]">
            <span className="text-xs text-[#4A5B6E]">
              Showing {page * PAGE_SIZE + 1}-{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
            </span>
            <div className="flex items-center gap-2">
              <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
                className="px-3 py-1.5 text-xs bg-[#0D1B2A] border border-[#1B2D42] rounded text-[#7A8BA0] hover:text-[#E8EDF2] disabled:opacity-30">Prev</button>
              <span className="text-xs text-[#7A8BA0]">Page {page + 1} of {totalPages}</span>
              <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}
                className="px-3 py-1.5 text-xs bg-[#0D1B2A] border border-[#1B2D42] rounded text-[#7A8BA0] hover:text-[#E8EDF2] disabled:opacity-30">Next</button>
            </div>
          </div>
        )}
      </div>

      {/* Compliance footer */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4 flex items-start gap-3">
        <FileText className="w-4 h-4 text-[#00C9A7] flex-shrink-0 mt-0.5" />
        <div className="text-xs text-[#4A5B6E] space-y-1">
          <p className="text-[#7A8BA0] font-medium">Companies Act 2013 Compliance</p>
          <p>This audit trail is append-only and cannot be modified or deleted. All transactions are logged with timestamp, user, action, and field-level changes per Rule 3(1) of Companies (Accounts) Rules, 2014. Logs preserved per Section 128(5) &mdash; 8 year retention.</p>
        </div>
      </div>
    </div>
  );
}
