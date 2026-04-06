import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Loader2, Download, Table2, BarChart3, MessageSquare } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const CHART_COLORS = ['#00C9A7', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#FF4D6A', '#10B981', '#3B82F6', '#EF4444', '#A855F7'];

const EXAMPLE_QUERIES = [
  "Top 5 vendors by purchase value",
  "Monthly revenue from sales invoices",
  "Customer-wise outstanding receivables",
  "Item-wise purchase quantity breakdown",
  "Expense breakdown by category from CoA",
  "Top 10 items by sales volume",
  "Vendor-wise GRN count",
  "Cost center wise expense distribution",
];

function formatValue(val, format) {
  if (val === null || val === undefined) return '—';
  if (format === 'currency') return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);
  if (format === 'number') return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(val);
  if (format === 'percent') return `${(val * 100).toFixed(1)}%`;
  if (format === 'date') return val;
  return String(val);
}

function DataTable({ columns, data }) {
  if (!data || data.length === 0) return <p className="text-[#4A5B6E] text-sm py-4 text-center">No data returned</p>;
  return (
    <div className="border border-[#1B2D42] rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm" data-testid="report-table">
          <thead>
            <tr className="bg-[#0D1B2A]">
              <th className="px-3 py-2.5 text-left text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0] border-b border-[#1B2D42]">#</th>
              {columns.map(c => (
                <th key={c.key} className={`px-3 py-2.5 text-[10px] tracking-wider uppercase font-semibold text-[#7A8BA0] border-b border-[#1B2D42] ${['number','currency','percent'].includes(c.format) ? 'text-right' : 'text-left'}`}>
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20 transition-colors">
                <td className="px-3 py-2 text-[#4A5B6E] font-mono text-xs">{i + 1}</td>
                {columns.map(c => (
                  <td key={c.key} className={`px-3 py-2 ${['number','currency','percent'].includes(c.format) ? 'text-right font-mono text-[#E8EDF2]' : 'text-[#E8EDF2]'}`}>
                    {formatValue(row[c.key], c.format)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ChartView({ chart, data, columns }) {
  if (!chart || chart.type === 'none' || !data || data.length === 0) return null;

  const xKey = chart.x_key || chart.label_key;
  const yKey = chart.y_key;

  if (chart.type === 'bar') {
    return (
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4" data-testid="report-chart">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B2D42" />
            <XAxis dataKey={xKey} tick={{ fill: '#7A8BA0', fontSize: 10 }} angle={-25} textAnchor="end" />
            <YAxis tick={{ fill: '#7A8BA0', fontSize: 10 }} tickFormatter={v => new Intl.NumberFormat('en-IN', { notation: 'compact' }).format(v)} />
            <Tooltip contentStyle={{ background: '#0D1B2A', border: '1px solid #1B2D42', borderRadius: 8, fontSize: 12 }}
              formatter={v => [new Intl.NumberFormat('en-IN').format(v), '']} labelStyle={{ color: '#7A8BA0' }} />
            <Bar dataKey={yKey} radius={[4, 4, 0, 0]}>
              {data.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (chart.type === 'line') {
    return (
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4" data-testid="report-chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B2D42" />
            <XAxis dataKey={xKey} tick={{ fill: '#7A8BA0', fontSize: 10 }} angle={-25} textAnchor="end" />
            <YAxis tick={{ fill: '#7A8BA0', fontSize: 10 }} tickFormatter={v => new Intl.NumberFormat('en-IN', { notation: 'compact' }).format(v)} />
            <Tooltip contentStyle={{ background: '#0D1B2A', border: '1px solid #1B2D42', borderRadius: 8, fontSize: 12 }}
              formatter={v => [new Intl.NumberFormat('en-IN').format(v), '']} labelStyle={{ color: '#7A8BA0' }} />
            <Line type="monotone" dataKey={yKey} stroke="#00C9A7" strokeWidth={2} dot={{ fill: '#00C9A7', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (chart.type === 'pie') {
    return (
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-4" data-testid="report-chart">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              labelLine={{ stroke: '#4A5B6E' }}>
              {data.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: '#0D1B2A', border: '1px solid #1B2D42', borderRadius: 8, fontSize: 12 }}
              formatter={v => [new Intl.NumberFormat('en-IN').format(v), '']} />
            <Legend wrapperStyle={{ fontSize: 11, color: '#7A8BA0' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return null;
}

export default function ReportingAI() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [history]);

  const handleQuery = async (q) => {
    const query = q || question.trim();
    if (!query || loading) return;
    setLoading(true);
    setQuestion('');

    // Add user message
    setHistory(prev => [...prev, { role: 'user', text: query }]);

    try {
      const res = await fetch(`${API}/api/company/ai-query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Query failed');
      }
      setHistory(prev => [...prev, { role: 'ai', ...data }]);
    } catch (e) {
      setHistory(prev => [...prev, { role: 'error', text: e.message }]);
    }
    setLoading(false);
  };

  const exportToCSV = (columns, data, title) => {
    if (!data || data.length === 0) return;
    const header = columns.map(c => c.label).join(',');
    const rows = data.map(r => columns.map(c => {
      const val = r[c.key];
      return typeof val === 'string' && val.includes(',') ? `"${val}"` : val ?? '';
    }).join(','));
    const csv = [header, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(title || 'report').replace(/\s+/g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('CSV exported');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]" data-testid="reporting-ai-page">
      {/* Header */}
      <div className="flex-shrink-0 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#00C9A7]/10 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-[#00C9A7]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">Reporting AI</h1>
            <p className="text-[#4A5B6E] text-sm">Ask anything about your business data in plain English</p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pb-4 pr-1" data-testid="report-chat-area">
        {history.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-[#152236] border border-[#1B2D42] flex items-center justify-center">
              <MessageSquare className="w-8 h-8 text-[#00C9A7]" />
            </div>
            <div className="text-center">
              <p className="text-[#E8EDF2] font-medium">Ask me anything about your ERP data</p>
              <p className="text-[#4A5B6E] text-sm mt-1">I'll query your database and show results as tables & charts</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 max-w-xl">
              {EXAMPLE_QUERIES.map((q, i) => (
                <button key={i} onClick={() => { setQuestion(q); handleQuery(q); }}
                  className="px-3 py-1.5 rounded-full text-xs bg-[#152236] border border-[#1B2D42] text-[#7A8BA0] hover:text-[#00C9A7] hover:border-[#00C9A7]/30 transition-colors"
                  data-testid={`example-query-${i}`}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i}>
            {msg.role === 'user' && (
              <div className="flex justify-end">
                <div className="bg-[#00C9A7]/10 border border-[#00C9A7]/20 rounded-xl rounded-br-sm px-4 py-2.5 max-w-lg">
                  <p className="text-sm text-[#E8EDF2]">{msg.text}</p>
                </div>
              </div>
            )}
            {msg.role === 'error' && (
              <div className="flex justify-start">
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl rounded-bl-sm px-4 py-2.5 max-w-lg">
                  <p className="text-sm text-red-400">{msg.text}</p>
                </div>
              </div>
            )}
            {msg.role === 'ai' && (
              <div className="space-y-3">
                {/* AI header */}
                <div className="flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-[#00C9A7]" />
                  <span className="text-xs font-bold text-[#00C9A7] tracking-wider uppercase">Kairos AI</span>
                </div>

                {/* Title & description */}
                <div className="bg-[#152236] border border-[#1B2D42] rounded-lg px-4 py-3">
                  <h3 className="text-sm font-bold text-[#E8EDF2]">{msg.title}</h3>
                  {msg.description && <p className="text-xs text-[#7A8BA0] mt-1">{msg.description}</p>}
                  {msg.summary_text && (
                    <div className="mt-2 px-3 py-1.5 bg-[#00C9A7]/5 border border-[#00C9A7]/10 rounded text-xs text-[#00C9A7]">
                      {msg.summary_text}
                    </div>
                  )}
                </div>

                {/* Chart */}
                <ChartView chart={msg.chart} data={msg.data} columns={msg.columns} />

                {/* Data Table */}
                <DataTable columns={msg.columns || []} data={msg.data || []} />

                {/* Export */}
                {msg.data && msg.data.length > 0 && (
                  <div className="flex items-center gap-2">
                    <button onClick={() => exportToCSV(msg.columns, msg.data, msg.title)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1B2D42] hover:bg-[#1B2D42]/70 text-[#E8EDF2] rounded-lg text-xs font-medium transition-colors"
                      data-testid="export-csv-btn">
                      <Download className="w-3 h-3" /> Export CSV
                    </button>
                    <span className="text-[10px] text-[#4A5B6E]">
                      {msg.data.length} row{msg.data.length !== 1 ? 's' : ''} • {msg.query_info?.collection}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-[#00C9A7] animate-pulse" />
            <span className="text-xs text-[#7A8BA0]">Querying your data...</span>
            <Loader2 className="w-3.5 h-3.5 animate-spin text-[#00C9A7]" />
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="flex-shrink-0 pt-3 pb-2 border-t border-[#1B2D42] relative z-[60]">
        <div className="flex items-center gap-3 bg-[#152236] border border-[#1B2D42] rounded-xl p-2">
          <input
            data-testid="reporting-ai-input"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleQuery()}
            placeholder="Ask a question about your business data..."
            className="flex-1 bg-transparent px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] outline-none"
            disabled={loading}
          />
          <button
            data-testid="reporting-ai-send"
            onClick={() => handleQuery()}
            disabled={loading || !question.trim()}
            className="px-4 py-2 bg-[#00C9A7] text-[#0D1B2A] rounded-lg font-bold text-xs hover:bg-[#00B396] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}
