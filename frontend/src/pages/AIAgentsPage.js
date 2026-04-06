import { useState, useEffect, useRef, useCallback } from 'react';
import { API } from '../App';
import { Bot, Send, Plus, Trash2, ChevronDown, Copy, Check, FileText, Database, Code, Loader2, FolderOpen, X } from 'lucide-react';

const AGENTS = {
  business: {
    id: 'business',
    name: 'Business Agent',
    short: 'BA',
    description: 'Understands Ind AS, GST, TDS, IT services workflows. Translates business requirements into technical specs.',
    color: '#a78bfa',
    gradient: 'from-violet-500/20 to-purple-600/20',
    icon: '📊',
  },
  coding: {
    id: 'coding',
    name: 'Coding Agent',
    short: 'DEV',
    description: 'Expert in FastAPI, React, MongoDB, Tailwind. Generates production-ready code. Can read & write project files.',
    color: '#22c55e',
    gradient: 'from-green-500/20 to-emerald-600/20',
    icon: '💻',
  },
  testing: {
    id: 'testing',
    name: 'Testing Agent',
    short: 'QA',
    description: 'Runs live queries against MongoDB. Validates TB balance, GST, revenue recognition, data integrity.',
    color: '#f59e0b',
    gradient: 'from-amber-500/20 to-orange-600/20',
    icon: '🔍',
  },
};

const TEST_QUERIES = [
  { id: 'full_health_check', label: 'Full Health Check' },
  { id: 'tb_balance', label: 'Trial Balance' },
  { id: 'entity_validation', label: 'Entity Validation' },
  { id: 'project_health', label: 'Project Health' },
  { id: 'timesheet_integrity', label: 'Timesheet Integrity' },
  { id: 'revenue_schedule', label: 'Revenue Schedule' },
  { id: 'transaction_coverage', label: 'Transaction Coverage' },
  { id: 'gst_compliance', label: 'GST Compliance' },
  { id: 'collection_stats', label: 'Collection Stats' },
];

export default function AIAgentsPage() {
  const [activeAgent, setActiveAgent] = useState('business');
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [fileExplorer, setFileExplorer] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [copied, setCopied] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/agents/sessions`).then(r => r.json()).then(setSessions);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createSession = async () => {
    const res = await fetch(`${API}/agents/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_type: activeAgent, title: 'New Session' }),
    });
    const session = await res.json();
    setSessions(prev => [session, ...prev]);
    setActiveSession(session.id);
    setMessages([]);
    inputRef.current?.focus();
    return session.id;
  };

  const loadSession = async (sid) => {
    const res = await fetch(`${API}/agents/sessions/${sid}`);
    const session = await res.json();
    setActiveSession(sid);
    setActiveAgent(session.agent_type || 'business');
    setMessages(session.messages || []);
  };

  const deleteSession = async (sid, e) => {
    e.stopPropagation();
    await fetch(`${API}/agents/sessions/${sid}`, { method: 'DELETE' });
    setSessions(prev => prev.filter(s => s.id !== sid));
    if (activeSession === sid) {
      setActiveSession(null);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    let sessionId = activeSession;
    if (!sessionId) {
      sessionId = await createSession();
    }

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      let context = '';
      if (activeAgent === 'coding' && selectedFile && fileContent) {
        context = `File: ${selectedFile}\n\`\`\`\n${fileContent}\n\`\`\``;
      }

      const res = await fetch(`${API}/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: activeAgent,
          message: userMsg,
          session_id: sessionId,
          context,
        }),
      });

      if (!res.ok) throw new Error(`Agent error: ${res.status}`);
      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        agent_type: activeAgent,
        timestamp: data.timestamp,
      }]);

      // Refresh session title
      setSessions(prev => prev.map(s =>
        s.id === sessionId ? { ...s, title: userMsg.slice(0, 80), updated_at: data.timestamp } : s
      ));
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}. Please try again.`,
        agent_type: activeAgent,
        timestamp: new Date().toISOString(),
        error: true,
      }]);
    }
    setLoading(false);
  };

  const runTestQuery = async (queryType) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/agents/testing/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query_type: queryType }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `**Test Query: ${queryType}**\n\`\`\`json\n${JSON.stringify(data.results, null, 2)}\n\`\`\``,
        agent_type: 'testing',
        timestamp: data.timestamp,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Query failed: ${err.message}`, agent_type: 'testing', error: true }]);
    }
    setLoading(false);
  };

  const loadFiles = async (dir = '/app/backend') => {
    const res = await fetch(`${API}/agents/coding/files?directory=${encodeURIComponent(dir)}`);
    setFiles(await res.json());
    setFileExplorer(true);
  };

  const readFile = async (path) => {
    const res = await fetch(`${API}/agents/coding/read-file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
    });
    const data = await res.json();
    setSelectedFile(path);
    setFileContent(data.content);
    setFileExplorer(false);
  };

  const copyText = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const agent = AGENTS[activeAgent];

  const renderMarkdown = (text) => {
    if (!text) return '';
    return text
      .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
        `<div class="relative my-3"><div class="bg-[#0A1628] rounded-lg border border-[#1B2D42] overflow-hidden"><div class="flex items-center justify-between px-3 py-1.5 bg-[#1B2D42]/50 border-b border-[#1B2D42]"><span class="text-[9px] font-mono text-[#4A5B6E]">${lang || 'code'}</span></div><pre class="p-3 overflow-x-auto text-[11px] leading-relaxed"><code class="text-[#E8EDF2] font-mono">${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre></div></div>`)
      .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 bg-[#1B2D42] rounded text-[#00d4aa] text-[10px] font-mono">$1</code>')
      .replace(/^### (.+)$/gm, '<h3 class="text-sm font-bold text-[#E8EDF2] mt-4 mb-1">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-base font-bold text-[#E8EDF2] mt-4 mb-2">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-lg font-bold text-[#E8EDF2] mt-4 mb-2">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong class="text-[#E8EDF2] font-bold">$1</strong>')
      .replace(/^\- (.+)$/gm, '<li class="ml-4 text-[#c8d4e0] list-disc">$1</li>')
      .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 text-[#c8d4e0] list-decimal">$2</li>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="flex h-[calc(100vh-56px)]" data-testid="ai-agents-page">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-[#060e1a] border-r border-[#1B2D42] transition-all overflow-hidden flex flex-col shrink-0`}>
        <div className="p-3 border-b border-[#1B2D42]">
          <button onClick={createSession} data-testid="new-session-btn"
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-[#152236] border border-[#1B2D42] text-xs font-bold text-[#E8EDF2] hover:border-[#00d4aa]/50 transition-colors">
            <Plus size={14} /> New Session
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {sessions.map(s => (
            <div key={s.id} onClick={() => loadSession(s.id)} data-testid={`session-${s.id}`}
              className={`group flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer text-[11px] transition-colors ${activeSession === s.id ? 'bg-[#152236] text-[#E8EDF2]' : 'text-[#4A5B6E] hover:bg-[#152236]/50 hover:text-[#E8EDF2]'}`}>
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <span className="w-5 h-5 rounded flex items-center justify-center text-[8px] font-bold shrink-0"
                  style={{ background: `${AGENTS[s.agent_type]?.color || '#6b7280'}20`, color: AGENTS[s.agent_type]?.color || '#6b7280' }}>
                  {AGENTS[s.agent_type]?.short || '?'}
                </span>
                <span className="truncate">{s.title || 'New Session'}</span>
              </div>
              <button onClick={(e) => deleteSession(s.id, e)} className="opacity-0 group-hover:opacity-100 text-[#4A5B6E] hover:text-[#ef4444] transition-all">
                <Trash2 size={12} />
              </button>
            </div>
          ))}
          {sessions.length === 0 && <p className="text-[10px] text-[#4A5B6E] text-center p-4">No sessions yet. Start a new one!</p>}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Agent Selector Header */}
        <div className="p-3 border-b border-[#1B2D42] bg-[#0A1628]">
          <div className="flex items-center gap-2">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-[#4A5B6E] hover:text-[#E8EDF2] transition-colors p-1" data-testid="toggle-sidebar">
              <ChevronDown size={16} className={`transition-transform ${sidebarOpen ? 'rotate-90' : '-rotate-90'}`} />
            </button>
            <div className="flex gap-1.5">
              {Object.values(AGENTS).map(a => (
                <button key={a.id} onClick={() => { setActiveAgent(a.id); }} data-testid={`agent-tab-${a.id}`}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold border transition-all flex items-center gap-1.5 ${activeAgent === a.id ? '' : 'border-[#1B2D42] text-[#4A5B6E] hover:text-[#E8EDF2] bg-transparent'}`}
                  style={activeAgent === a.id ? { background: `${a.color}15`, color: a.color, borderColor: a.color } : {}}>
                  <span>{a.icon}</span> {a.name}
                </button>
              ))}
            </div>
            <div className="flex-1" />
            {activeAgent === 'coding' && (
              <div className="flex gap-1.5">
                <button onClick={() => loadFiles('/app/backend')} className="px-2.5 py-1 rounded text-[9px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#22c55e] hover:border-[#22c55e]/30 transition-colors" data-testid="browse-backend">
                  <FolderOpen size={12} className="inline mr-1" />Backend
                </button>
                <button onClick={() => loadFiles('/app/frontend/src')} className="px-2.5 py-1 rounded text-[9px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#22c55e] hover:border-[#22c55e]/30 transition-colors" data-testid="browse-frontend">
                  <FolderOpen size={12} className="inline mr-1" />Frontend
                </button>
                {selectedFile && (
                  <span className="px-2 py-1 rounded text-[9px] font-mono bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20 flex items-center gap-1">
                    <FileText size={10} />{selectedFile.split('/').pop()}
                    <button onClick={() => { setSelectedFile(null); setFileContent(''); }} className="hover:text-white"><X size={10} /></button>
                  </span>
                )}
              </div>
            )}
            {activeAgent === 'testing' && (
              <div className="flex gap-1 flex-wrap">
                {TEST_QUERIES.slice(0, 5).map(q => (
                  <button key={q.id} onClick={() => runTestQuery(q.id)} disabled={loading} data-testid={`test-query-${q.id}`}
                    className="px-2 py-1 rounded text-[8px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#f59e0b] hover:border-[#f59e0b]/30 transition-colors disabled:opacity-50">
                    {q.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          <p className="text-[10px] text-[#4A5B6E] mt-1.5 ml-8">{agent.description}</p>
        </div>

        {/* File Explorer Modal */}
        {fileExplorer && (
          <div className="absolute inset-0 z-50 bg-black/50 flex items-center justify-center" onClick={() => setFileExplorer(false)}>
            <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg w-[600px] max-h-[500px] overflow-hidden" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between p-3 border-b border-[#1B2D42]">
                <h3 className="text-sm font-bold text-[#E8EDF2]">File Explorer</h3>
                <button onClick={() => setFileExplorer(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={16} /></button>
              </div>
              <div className="overflow-y-auto max-h-[430px] p-2">
                {files.map(f => (
                  <button key={f.path} onClick={() => readFile(f.path)} data-testid={`file-${f.relative}`}
                    className="w-full flex items-center gap-2 px-3 py-1.5 rounded hover:bg-[#152236] text-left transition-colors">
                    <Code size={12} className="text-[#22c55e] shrink-0" />
                    <span className="text-[11px] font-mono text-[#E8EDF2] truncate">{f.relative}</span>
                    <span className="text-[9px] text-[#4A5B6E] ml-auto">{(f.size / 1024).toFixed(1)}KB</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl mb-4" style={{ background: `${agent.color}15` }}>{agent.icon}</div>
              <h2 className="text-lg font-bold text-[#E8EDF2] mb-1">{agent.name}</h2>
              <p className="text-xs text-[#4A5B6E] max-w-md">{agent.description}</p>
              <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-lg">
                {activeAgent === 'business' && ['Explain Ind AS 115 revenue recognition for our T&M projects', 'What GST implications for our RetailCo GBP invoices?', 'Draft tech spec for a Bank Reconciliation module'].map((s, i) => (
                  <button key={i} onClick={() => { setInput(s); }} className="px-3 py-1.5 rounded-lg text-[10px] bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#a78bfa] hover:border-[#a78bfa]/30 transition-colors">{s}</button>
                ))}
                {activeAgent === 'coding' && ['Show me the routes_projects.py file structure', 'Generate an API endpoint for project profitability report', 'Create a React component for weekly timesheet entry form'].map((s, i) => (
                  <button key={i} onClick={() => { setInput(s); }} className="px-3 py-1.5 rounded-lg text-[10px] bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#22c55e] hover:border-[#22c55e]/30 transition-colors">{s}</button>
                ))}
                {activeAgent === 'testing' && ['Run a full health check on the ERP', 'Validate all vendor GSTINs and state codes', 'Check if the revenue schedule balances with project milestones'].map((s, i) => (
                  <button key={i} onClick={() => { setInput(s); }} className="px-3 py-1.5 rounded-lg text-[10px] bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#f59e0b] hover:border-[#f59e0b]/30 transition-colors">{s}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold shrink-0 mt-1"
                  style={{ background: `${AGENTS[msg.agent_type]?.color || agent.color}20`, color: AGENTS[msg.agent_type]?.color || agent.color }}>
                  {AGENTS[msg.agent_type]?.short || agent.short}
                </div>
              )}
              <div className={`max-w-[75%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-[#152236] border border-[#1B2D42]' : msg.error ? 'bg-[#ef4444]/5 border border-[#ef4444]/20' : 'bg-[#0A1628] border border-[#1B2D42]'}`}>
                {msg.role === 'user' ? (
                  <p className="text-xs text-[#E8EDF2] whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div className="relative group">
                    <button onClick={() => copyText(msg.content, i)} data-testid={`copy-msg-${i}`}
                      className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 px-1.5 py-0.5 rounded text-[8px] font-bold border transition-all"
                      style={{ background: copied === i ? '#065f46' : '#152236', color: copied === i ? '#34d399' : '#4A5B6E', borderColor: copied === i ? '#34d399' : '#1B2D42' }}>
                      {copied === i ? <><Check size={10} className="inline" /> Copied</> : <><Copy size={10} className="inline" /> Copy</>}
                    </button>
                    <div className="text-xs text-[#c8d4e0] leading-relaxed prose-dark" dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                  </div>
                )}
                <p className="text-[8px] text-[#4A5B6E] mt-1.5">{new Date(msg.timestamp).toLocaleTimeString()}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-[#152236] border border-[#1B2D42] flex items-center justify-center text-[10px] font-bold text-[#4A5B6E] shrink-0 mt-1">U</div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${agent.color}20` }}>
                <Loader2 size={14} className="animate-spin" style={{ color: agent.color }} />
              </div>
              <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-3">
                <div className="flex items-center gap-2 text-xs text-[#4A5B6E]">
                  <span className="animate-pulse">{agent.name} is thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 border-t border-[#1B2D42] bg-[#0A1628]">
          {selectedFile && activeAgent === 'coding' && (
            <div className="mb-2 px-3 py-1.5 rounded bg-[#22c55e]/5 border border-[#22c55e]/20 text-[9px] text-[#22c55e]">
              <FileText size={10} className="inline mr-1" /> Context: <span className="font-mono">{selectedFile}</span> ({(fileContent.length / 1024).toFixed(1)}KB loaded)
            </div>
          )}
          <div className="flex gap-2">
            <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder={`Ask ${agent.name}...`}
              disabled={loading}
              data-testid="agent-input"
              className="flex-1 px-4 py-2.5 bg-[#152236] border border-[#1B2D42] rounded-lg text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/50 disabled:opacity-50 transition-colors" />
            <button onClick={sendMessage} disabled={loading || !input.trim()} data-testid="agent-send-btn"
              className="px-4 py-2.5 rounded-lg text-xs font-bold transition-all disabled:opacity-30"
              style={{ background: `${agent.color}20`, color: agent.color, border: `1px solid ${agent.color}40` }}>
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
