import { useState, useEffect, useRef } from 'react';
import { API } from '../App';
import {
  Send, Plus, Trash2, ChevronDown, ChevronRight, Copy, Check, FileText,
  Code, Loader2, FolderOpen, X, Cpu, Wrench, Terminal, Database,
  AlertCircle, CheckCircle2, ChevronUp, Zap, Settings2, Play
} from 'lucide-react';

const MODES = [
  { id: 'auto', label: 'Auto', desc: 'Full pipeline — Analyze, Code, Test, Deploy', color: '#00d4aa' },
  { id: 'ba', label: 'Business', desc: 'Requirements & compliance analysis only', color: '#a78bfa' },
  { id: 'dev', label: 'Coding', desc: 'File operations & code generation', color: '#22c55e' },
  { id: 'qa', label: 'Testing', desc: 'Database validation & API testing', color: '#f59e0b' },
];

const TEST_QUERIES = [
  { id: 'full_health_check', label: 'Health Check' },
  { id: 'tb_balance', label: 'Trial Balance' },
  { id: 'collection_stats', label: 'Collection Stats' },
  { id: 'entity_validation', label: 'Entity Validation' },
  { id: 'project_health', label: 'Project Health' },
];

const TOOL_ICONS = {
  read_file: FileText,
  write_file: Code,
  run_query: Database,
  restart_service: Zap,
  test_api: Terminal,
  list_files: FolderOpen,
};

const TOOL_COLORS = {
  read_file: '#60a5fa',
  write_file: '#22c55e',
  run_query: '#f59e0b',
  restart_service: '#ef4444',
  test_api: '#a78bfa',
  list_files: '#06b6d4',
};

function ToolResultCard({ result, index }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = TOOL_ICONS[result.tool] || Wrench;
  const color = TOOL_COLORS[result.tool] || '#4A5B6E';
  const ok = result.result?.status === 'ok';

  let summary = '';
  if (result.tool === 'read_file') summary = result.args?.path?.split('/').pop() || '';
  else if (result.tool === 'write_file') summary = `${result.args?.path?.split('/').pop()} (${result.result?.size || 0} chars)`;
  else if (result.tool === 'run_query') summary = result.args?.query_type || '';
  else if (result.tool === 'restart_service') summary = result.args?.service || '';
  else if (result.tool === 'test_api') summary = `${result.args?.method} ${result.args?.url}`;
  else if (result.tool === 'list_files') summary = `${result.result?.count || 0} files`;

  return (
    <div className="border border-[#1B2D42] rounded-lg overflow-hidden bg-[#0D1B2A]" data-testid={`tool-result-${index}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-[#152236] transition-colors text-left"
      >
        <Icon size={13} style={{ color }} className="shrink-0" />
        <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color }}>{result.tool.replace('_', ' ')}</span>
        <span className="text-[10px] text-[#7A8BA0] truncate flex-1">{summary}</span>
        {ok ? <CheckCircle2 size={12} className="text-emerald-500 shrink-0" /> : <AlertCircle size={12} className="text-red-400 shrink-0" />}
        {expanded ? <ChevronUp size={12} className="text-[#4A5B6E] shrink-0" /> : <ChevronDown size={12} className="text-[#4A5B6E] shrink-0" />}
      </button>
      {expanded && (
        <div className="px-3 pb-2 border-t border-[#1B2D42]">
          <pre className="text-[10px] text-[#c8d4e0] font-mono overflow-x-auto mt-2 max-h-48 overflow-y-auto whitespace-pre-wrap">
            {JSON.stringify(result.result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function QuestionBlock({ question }) {
  return (
    <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-[#a78bfa]/10 border border-[#a78bfa]/20" data-testid="ai-question-block">
      <AlertCircle size={14} className="text-[#a78bfa] shrink-0 mt-0.5" />
      <p className="text-xs text-[#c8d4e0]">{question}</p>
    </div>
  );
}

export default function AIAgentsPage() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState('auto');
  const [modeOpen, setModeOpen] = useState(false);
  const [fileExplorer, setFileExplorer] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [copied, setCopied] = useState(null);
  const [toolbarOpen, setToolbarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/agents/sessions`).then(r => r.json()).then(setSessions).catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createSession = async () => {
    const res = await fetch(`${API}/agents/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_type: mode, title: 'New Session' }),
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
    setMessages(session.messages || []);
  };

  const deleteSession = async (sid, e) => {
    e.stopPropagation();
    await fetch(`${API}/agents/sessions/${sid}`, { method: 'DELETE' });
    setSessions(prev => prev.filter(s => s.id !== sid));
    if (activeSession === sid) { setActiveSession(null); setMessages([]); }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    let sessionId = activeSession;
    if (!sessionId) sessionId = await createSession();

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      let context = '';
      if (selectedFile && fileContent) {
        context = `File: ${selectedFile}\n\`\`\`\n${fileContent.slice(0, 8000)}\n\`\`\``;
      }

      const res = await fetch(`${API}/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_type: mode, message: userMsg, session_id: sessionId, context }),
      });

      if (!res.ok) throw new Error(`Engine error: ${res.status}`);
      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        tool_calls_executed: data.tool_calls_executed || 0,
        files_modified: data.files_modified || [],
        questions: data.questions || [],
        tool_results: data.tool_results || [],
        agent_type: data.agent_type,
      }]);

      setSessions(prev => prev.map(s =>
        s.id === sessionId ? { ...s, title: userMsg.slice(0, 80), updated_at: data.timestamp } : s
      ));
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}`,
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
        content: `**DB Query: ${queryType}**\n\`\`\`json\n${JSON.stringify(data.results, null, 2)}\n\`\`\``,
        timestamp: new Date().toISOString(),
        tool_results: [{ tool: 'run_query', args: { query_type: queryType }, result: data }],
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Query failed: ${err.message}`, error: true, timestamp: new Date().toISOString() }]);
    }
    setLoading(false);
    setToolbarOpen(false);
  };

  const loadFiles = async (dir = '/app/backend') => {
    try {
      const res = await fetch(`${API}/agents/coding/files?directory=${encodeURIComponent(dir)}`);
      const data = await res.json();
      setFiles(data.files || data || []);
      setFileExplorer(true);
    } catch {}
  };

  const readFile = async (path) => {
    try {
      const res = await fetch(`${API}/agents/coding/read-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path }),
      });
      const data = await res.json();
      setSelectedFile(path);
      setFileContent(data.content || '');
      setFileExplorer(false);
    } catch {}
  };

  const copyText = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const currentMode = MODES.find(m => m.id === mode);

  const renderMarkdown = (text) => {
    if (!text) return '';
    return text
      .replace(/```TOOL_CALL[\s\S]*?```/g, '')
      .replace(/```QUESTION[\s\S]*?```/g, '')
      .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
        `<div class="my-2"><div class="bg-[#0A1628] rounded-lg border border-[#1B2D42] overflow-hidden"><div class="flex items-center px-3 py-1 bg-[#1B2D42]/50 border-b border-[#1B2D42]"><span class="text-[9px] font-mono text-[#4A5B6E]">${lang || 'code'}</span></div><pre class="p-3 overflow-x-auto text-[10px] leading-relaxed"><code class="text-[#E8EDF2] font-mono">${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre></div></div>`)
      .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-[#1B2D42] rounded text-[#00d4aa] text-[10px] font-mono">$1</code>')
      .replace(/^### (.+)$/gm, '<h3 class="text-xs font-bold text-[#E8EDF2] mt-3 mb-1">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-sm font-bold text-[#E8EDF2] mt-3 mb-1">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-base font-bold text-[#E8EDF2] mt-3 mb-1">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong class="text-[#E8EDF2]">$1</strong>')
      .replace(/^\- (.+)$/gm, '<li class="ml-4 text-[#c8d4e0] list-disc text-xs">$1</li>')
      .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 text-[#c8d4e0] list-decimal text-xs">$2</li>')
      .replace(/\n{2,}/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  };

  const starters = [
    'Run a full health check on the ERP database',
    'Show me the routes_projects.py file and suggest improvements',
    'Create a new API endpoint for project profitability report',
    'Explain Ind AS 115 revenue recognition for our T&M projects',
    'Validate all vendor GSTINs and check for compliance issues',
  ];

  return (
    <div className="flex h-[calc(100vh-56px)]" data-testid="ai-engine-page">
      {/* Sessions Sidebar */}
      <div className={`${sidebarOpen ? 'w-60' : 'w-0'} bg-[#060e1a] border-r border-[#1B2D42] transition-all overflow-hidden flex flex-col shrink-0`}>
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
                <Cpu size={12} className="text-[#00d4aa] shrink-0" />
                <span className="truncate">{s.title || 'New Session'}</span>
              </div>
              <button onClick={(e) => deleteSession(s.id, e)} className="opacity-0 group-hover:opacity-100 text-[#4A5B6E] hover:text-[#ef4444] transition-all">
                <Trash2 size={12} />
              </button>
            </div>
          ))}
          {sessions.length === 0 && <p className="text-[10px] text-[#4A5B6E] text-center p-4">No sessions yet</p>}
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="px-3 py-2.5 border-b border-[#1B2D42] bg-[#0A1628] flex items-center gap-3">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-[#4A5B6E] hover:text-[#E8EDF2] transition-colors p-1" data-testid="toggle-sidebar">
            {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>

          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d4aa]/20 to-[#00d4aa]/5 border border-[#00d4aa]/30 flex items-center justify-center">
              <Cpu size={14} className="text-[#00d4aa]" />
            </div>
            <div>
              <h1 className="text-xs font-bold text-[#E8EDF2] leading-none">Kairos AI Engine</h1>
              <p className="text-[9px] text-[#4A5B6E] leading-none mt-0.5">Analyze · Code · Test · Deploy</p>
            </div>
          </div>

          {/* Mode Selector */}
          <div className="relative ml-3">
            <button
              onClick={() => setModeOpen(!modeOpen)}
              data-testid="mode-selector"
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-bold border transition-all"
              style={{ background: `${currentMode.color}10`, color: currentMode.color, borderColor: `${currentMode.color}40` }}
            >
              <Settings2 size={11} />
              {currentMode.label}
              <ChevronDown size={10} className={`transition-transform ${modeOpen ? 'rotate-180' : ''}`} />
            </button>
            {modeOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setModeOpen(false)} />
                <div className="absolute top-full left-0 mt-1 w-56 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg shadow-xl z-50 overflow-hidden">
                  {MODES.map(m => (
                    <button key={m.id} data-testid={`mode-${m.id}`}
                      onClick={() => { setMode(m.id); setModeOpen(false); }}
                      className={`w-full flex items-start gap-2 px-3 py-2.5 text-left transition-colors ${mode === m.id ? 'bg-[#152236]' : 'hover:bg-[#152236]/50'}`}
                    >
                      <div className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ background: m.color }} />
                      <div>
                        <p className="text-[11px] font-bold" style={{ color: mode === m.id ? m.color : '#E8EDF2' }}>{m.label}</p>
                        <p className="text-[9px] text-[#4A5B6E]">{m.desc}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="flex-1" />

          {/* Toolbar Buttons */}
          <div className="flex items-center gap-1.5">
            <button onClick={() => loadFiles('/app/backend')} data-testid="browse-backend-btn"
              className="px-2 py-1.5 rounded text-[9px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#22c55e] hover:border-[#22c55e]/30 transition-colors flex items-center gap-1">
              <FolderOpen size={11} />Backend
            </button>
            <button onClick={() => loadFiles('/app/frontend/src')} data-testid="browse-frontend-btn"
              className="px-2 py-1.5 rounded text-[9px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#22c55e] hover:border-[#22c55e]/30 transition-colors flex items-center gap-1">
              <FolderOpen size={11} />Frontend
            </button>
            <div className="relative">
              <button onClick={() => setToolbarOpen(!toolbarOpen)} data-testid="quick-tests-btn"
                className="px-2 py-1.5 rounded text-[9px] font-bold bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#f59e0b] hover:border-[#f59e0b]/30 transition-colors flex items-center gap-1">
                <Play size={11} />Tests
              </button>
              {toolbarOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setToolbarOpen(false)} />
                  <div className="absolute top-full right-0 mt-1 w-44 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg shadow-xl z-50 overflow-hidden p-1.5">
                    {TEST_QUERIES.map(q => (
                      <button key={q.id} onClick={() => runTestQuery(q.id)} disabled={loading} data-testid={`test-query-${q.id}`}
                        className="w-full text-left px-2.5 py-1.5 rounded text-[10px] text-[#7A8BA0] hover:bg-[#152236] hover:text-[#f59e0b] transition-colors disabled:opacity-50">
                        {q.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Attached File Indicator */}
        {selectedFile && (
          <div className="px-3 py-1.5 bg-[#22c55e]/5 border-b border-[#22c55e]/20 flex items-center gap-2">
            <FileText size={11} className="text-[#22c55e]" />
            <span className="text-[10px] font-mono text-[#22c55e]">{selectedFile}</span>
            <span className="text-[9px] text-[#4A5B6E]">({(fileContent.length / 1024).toFixed(1)}KB attached as context)</span>
            <button onClick={() => { setSelectedFile(null); setFileContent(''); }} className="ml-auto text-[#4A5B6E] hover:text-[#ef4444] transition-colors"><X size={12} /></button>
          </div>
        )}

        {/* File Explorer Modal */}
        {fileExplorer && (
          <div className="absolute inset-0 z-50 bg-black/60 flex items-center justify-center" onClick={() => setFileExplorer(false)}>
            <div className="bg-[#0A1628] border border-[#1B2D42] rounded-xl w-[560px] max-h-[480px] overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between px-4 py-3 border-b border-[#1B2D42]">
                <h3 className="text-sm font-bold text-[#E8EDF2]">File Explorer</h3>
                <button onClick={() => setFileExplorer(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={16} /></button>
              </div>
              <div className="overflow-y-auto max-h-[420px] p-2">
                {(Array.isArray(files) ? files : []).map((f, i) => (
                  <button key={f.path || i} onClick={() => readFile(f.path)} data-testid={`file-${f.relative || f.path}`}
                    className="w-full flex items-center gap-2 px-3 py-1.5 rounded hover:bg-[#152236] text-left transition-colors">
                    <Code size={12} className="text-[#22c55e] shrink-0" />
                    <span className="text-[11px] font-mono text-[#E8EDF2] truncate">{f.relative || f.path}</span>
                    <span className="text-[9px] text-[#4A5B6E] ml-auto shrink-0">{((f.size || 0) / 1024).toFixed(1)}KB</span>
                  </button>
                ))}
                {(!files || files.length === 0) && <p className="text-[10px] text-[#4A5B6E] text-center p-6">No files found</p>}
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#00d4aa]/15 to-[#00d4aa]/5 border border-[#00d4aa]/20 flex items-center justify-center mb-4">
                <Cpu size={28} className="text-[#00d4aa]" />
              </div>
              <h2 className="text-lg font-bold text-[#E8EDF2] mb-1">Kairos AI Engine</h2>
              <p className="text-xs text-[#4A5B6E] max-w-md mb-6">
                Your unified AI developer. I can analyze requirements, write and modify code, run database validations, and deploy changes — all in one conversation.
              </p>
              <div className="flex flex-wrap gap-2 justify-center max-w-xl">
                {starters.map((s, i) => (
                  <button key={i} onClick={() => setInput(s)} data-testid={`starter-${i}`}
                    className="px-3 py-1.5 rounded-lg text-[10px] bg-[#152236] border border-[#1B2D42] text-[#4A5B6E] hover:text-[#00d4aa] hover:border-[#00d4aa]/30 transition-colors text-left">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`} data-testid={`message-${i}`}>
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d4aa]/20 to-[#00d4aa]/5 border border-[#00d4aa]/20 flex items-center justify-center shrink-0 mt-1">
                  <Cpu size={13} className="text-[#00d4aa]" />
                </div>
              )}
              <div className={`max-w-[78%] ${msg.role === 'user' ? '' : 'flex-1 max-w-[78%]'}`}>
                <div className={`rounded-lg p-3 ${msg.role === 'user'
                  ? 'bg-[#152236] border border-[#1B2D42]'
                  : msg.error
                    ? 'bg-[#ef4444]/5 border border-[#ef4444]/20'
                    : 'bg-[#0A1628] border border-[#1B2D42]'
                  }`}>
                  {msg.role === 'user' ? (
                    <p className="text-xs text-[#E8EDF2] whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <div className="relative group">
                      <button onClick={() => copyText(msg.content, i)} data-testid={`copy-msg-${i}`}
                        className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 px-1.5 py-0.5 rounded text-[8px] font-bold border transition-all z-10"
                        style={{ background: copied === i ? '#065f46' : '#152236', color: copied === i ? '#34d399' : '#4A5B6E', borderColor: copied === i ? '#34d399' : '#1B2D42' }}>
                        {copied === i ? <><Check size={10} className="inline" /> Copied</> : <><Copy size={10} className="inline" /> Copy</>}
                      </button>
                      <div className="text-xs text-[#c8d4e0] leading-relaxed" dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                    </div>
                  )}
                  <p className="text-[8px] text-[#4A5B6E] mt-1.5">{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}</p>
                </div>

                {/* Questions */}
                {msg.questions && msg.questions.length > 0 && (
                  <div className="mt-2 space-y-1.5">
                    {msg.questions.map((q, qi) => <QuestionBlock key={qi} question={q} />)}
                  </div>
                )}

                {/* Tool Execution Results */}
                {msg.tool_results && msg.tool_results.length > 0 && (
                  <div className="mt-2 space-y-1" data-testid="tool-results-section">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Wrench size={11} className="text-[#4A5B6E]" />
                      <span className="text-[9px] font-bold uppercase tracking-wider text-[#4A5B6E]">
                        {msg.tool_results.length} tool{msg.tool_results.length > 1 ? 's' : ''} executed
                      </span>
                    </div>
                    {msg.tool_results.map((tr, ti) => <ToolResultCard key={ti} result={tr} index={ti} />)}
                  </div>
                )}

                {/* Files Modified Badge */}
                {msg.files_modified && msg.files_modified.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5" data-testid="files-modified-section">
                    {msg.files_modified.map((f, fi) => (
                      <span key={fi} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-mono bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20">
                        <CheckCircle2 size={9} /> {f.split('/').pop()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-[#152236] border border-[#1B2D42] flex items-center justify-center text-[10px] font-bold text-[#4A5B6E] shrink-0 mt-1">U</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d4aa]/20 to-[#00d4aa]/5 border border-[#00d4aa]/20 flex items-center justify-center shrink-0">
                <Loader2 size={13} className="animate-spin text-[#00d4aa]" />
              </div>
              <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-3">
                <div className="flex items-center gap-2 text-xs text-[#4A5B6E]">
                  <span className="animate-pulse">Engine processing</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#152236] border border-[#1B2D42]" style={{ color: currentMode.color }}>
                    {currentMode.label}
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 border-t border-[#1B2D42] bg-[#0A1628]">
          <div className="flex gap-2">
            <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Describe what you need — analysis, code changes, tests, or deployments..."
              disabled={loading}
              data-testid="engine-input"
              className="flex-1 px-4 py-2.5 bg-[#152236] border border-[#1B2D42] rounded-lg text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none focus:border-[#00d4aa]/50 disabled:opacity-50 transition-colors" />
            <button onClick={sendMessage} disabled={loading || !input.trim()} data-testid="engine-send-btn"
              className="px-4 py-2.5 rounded-lg text-xs font-bold bg-[#00d4aa]/15 text-[#00d4aa] border border-[#00d4aa]/30 hover:bg-[#00d4aa]/25 transition-all disabled:opacity-30">
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChevronLeft(props) {
  return <ChevronRight {...props} style={{ transform: 'rotate(180deg)', ...props.style }} />;
}
