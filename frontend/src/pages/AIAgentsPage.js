import { useState, useEffect, useRef, useCallback } from 'react';
import { API } from '../App';
import DOMPurify from 'dompurify';
import {
  Send, Plus, Trash2, ChevronDown, ChevronRight, Copy, Check, FileText,
  Code, Loader2, FolderOpen, X, Cpu, Wrench, Terminal, Database,
  AlertCircle, CheckCircle2, ChevronUp, Zap, Settings2, Play,
  Paperclip, Globe, Image, Link2, Search, Activity, GitBranch, Package,
  Brain, Camera, Eye, Trash, ArrowRightLeft, Settings, FileCode, GitCommit,
  Bot, Layers, ImagePlus, Key
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
  read_file: FileText, write_file: Code, run_query: Database,
  restart_service: Zap, test_api: Terminal, list_files: FolderOpen,
  create_file: Code, patch_file: Code, insert_lines: Code,
  delete_lines: Code, get_schema: Database, run_command: Terminal,
  grep_search: Search, check_logs: Activity, install_package: Package,
  run_tests: Play, verify_deployment: CheckCircle2,
  web_search: Globe, take_screenshot: Camera,
  delete_file: Trash, move_file: ArrowRightLeft, manage_env: Settings,
  lint_code: FileCode, crawl_url: Globe, git_info: GitCommit,
  call_subagent: Bot, batch_operations: Layers, generate_image: ImagePlus,
};

const TOOL_COLORS = {
  read_file: '#60a5fa', write_file: '#22c55e', run_query: '#f59e0b',
  restart_service: '#ef4444', test_api: '#a78bfa', list_files: '#06b6d4',
  create_file: '#22c55e', patch_file: '#f59e0b', insert_lines: '#22c55e',
  delete_lines: '#ef4444', get_schema: '#06b6d4', run_command: '#60a5fa',
  grep_search: '#f59e0b', check_logs: '#a78bfa', install_package: '#06b6d4',
  run_tests: '#22c55e', verify_deployment: '#00d4aa',
  web_search: '#f97316', take_screenshot: '#e879f9',
  delete_file: '#ef4444', move_file: '#f59e0b', manage_env: '#06b6d4',
  lint_code: '#a78bfa', crawl_url: '#f97316', git_info: '#60a5fa',
  call_subagent: '#00d4aa', batch_operations: '#22c55e', generate_image: '#e879f9',
};

function ToolResultCard({ result, index }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = TOOL_ICONS[result.tool] || Wrench;
  const color = TOOL_COLORS[result.tool] || '#4A5B6E';
  const ok = result.result?.status === 'ok';

  let summary = '';
  if (result.tool === 'read_file') summary = result.args?.path?.split('/').pop() || '';
  else if (result.tool === 'write_file' || result.tool === 'create_file') summary = `${result.args?.path?.split('/').pop()} (${result.result?.size || 0} chars)`;
  else if (result.tool === 'patch_file') summary = result.args?.path?.split('/').pop() || '';
  else if (result.tool === 'run_query') summary = result.args?.query_type || '';
  else if (result.tool === 'restart_service') summary = result.args?.service || '';
  else if (result.tool === 'test_api') summary = `${result.args?.method} ${result.args?.url}`;
  else if (result.tool === 'list_files') summary = `${result.result?.count || 0} files`;
  else if (result.tool === 'grep_search') summary = `"${result.args?.pattern}" (${result.result?.count || 0} matches)`;
  else if (result.tool === 'check_logs') summary = result.args?.service || 'backend';
  else if (result.tool === 'install_package') summary = result.args?.package || '';
  else if (result.tool === 'run_tests') summary = result.args?.test_path || 'tests';
  else if (result.tool === 'scaffold_module') summary = `${result.args?.module_name} (${result.result?.endpoints_created || 0} endpoints)`;
  else if (result.tool === 'create_page') summary = result.args?.page_name || '';
  else if (result.tool === '_auto_restart') summary = result.result?.startup_ok ? 'OK' : 'Failed';
  else if (result.tool === 'verify_deployment') summary = result.result?.summary || `${result.result?.checks?.length || 0} checks`;
  else if (result.tool === 'web_search') summary = `"${result.args?.query?.slice(0, 40) || ''}" (${result.result?.count || 0} results)`;
  else if (result.tool === 'take_screenshot') summary = result.args?.url || 'screenshot';
  else if (result.tool === 'delete_file') summary = result.args?.path?.split('/').pop() || '';
  else if (result.tool === 'move_file') summary = `${result.args?.source?.split('/').pop() || ''} → ${result.args?.destination?.split('/').pop() || ''}`;
  else if (result.tool === 'manage_env') summary = `${result.args?.action || ''} ${result.args?.key || result.args?.file || ''}`;
  else if (result.tool === 'lint_code') summary = result.args?.path?.split('/').pop() || '';
  else if (result.tool === 'crawl_url') summary = result.args?.url?.slice(0, 50) || '';
  else if (result.tool === 'git_info') summary = result.args?.action || 'log';
  else if (result.tool === 'run_query') summary = `${result.args?.operation || result.args?.query_type || 'query'} on ${result.args?.collection || '?'}`;
  else if (result.tool === 'call_subagent') summary = `${result.args?.agent_type || '?'}: ${result.args?.task?.slice(0, 50) || ''}`;
  else if (result.tool === 'batch_operations') summary = `${result.result?.succeeded || 0}/${result.result?.total || 0} ops succeeded`;
  else if (result.tool === 'generate_image') summary = result.args?.prompt?.slice(0, 50) || 'image';

  return (
    <div className="border border-[#1B2D42] rounded-lg overflow-hidden bg-[#0D1B2A]" data-testid={`tool-result-${index}`}>
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center gap-2 px-3 py-2 hover:bg-[#152236] transition-colors text-left">
        <Icon size={13} style={{ color }} className="shrink-0" />
        <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color }}>{result.tool.replace(/_/g, ' ')}</span>
        <span className="text-[10px] text-[#7A8BA0] truncate flex-1">{summary}</span>
        {ok ? <CheckCircle2 size={12} className="text-emerald-500 shrink-0" /> : <AlertCircle size={12} className="text-red-400 shrink-0" />}
        {expanded ? <ChevronUp size={12} className="text-[#4A5B6E] shrink-0" /> : <ChevronDown size={12} className="text-[#4A5B6E] shrink-0" />}
      </button>
      {expanded && (
        <div className="px-3 pb-2 border-t border-[#1B2D42]">
          {result.tool === 'take_screenshot' && result.result?.path && (
            <div className="mt-2 mb-2">
              <img src={`${window.location.origin}/api/agents/screenshots/${result.result.path.split('/').pop()}`}
                alt="Screenshot" className="rounded border border-[#1B2D42] max-h-64 w-auto" loading="lazy"
                onError={(e) => { e.target.style.display = 'none'; }} />
            </div>
          )}
          {result.tool === 'generate_image' && result.result?.serve_url && (
            <div className="mt-2 mb-2">
              <img src={`${window.location.origin}${result.result.serve_url}`}
                alt={result.args?.prompt || 'Generated image'} className="rounded border border-[#1B2D42] max-h-64 w-auto" loading="lazy" />
              <p className="text-[9px] text-[#4A5B6E] mt-1">{result.result?.file_size_kb}KB · {result.args?.prompt?.slice(0, 60)}</p>
            </div>
          )}
          {result.tool === 'call_subagent' && result.result?.response && (
            <div className="mt-2 bg-[#0D1B2A] rounded p-2.5 border border-[#00d4aa]/20">
              <div className="flex items-center gap-1.5 mb-1.5">
                <Bot size={11} className="text-[#00d4aa]" />
                <span className="text-[9px] font-bold uppercase tracking-wider text-[#00d4aa]">{result.args?.agent_type} subagent</span>
              </div>
              <p className="text-[10px] text-[#c8d4e0] whitespace-pre-wrap" style={{ maxHeight: '300px', overflow: 'auto' }}>
                {result.result.response}
              </p>
            </div>
          )}
          {result.tool === 'web_search' && result.result?.results?.length > 0 && (
            <div className="mt-2 space-y-1.5">
              {result.result.results.map((r, ri) => (
                <div key={ri} className="text-[10px]">
                  <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-[#60a5fa] hover:underline font-medium">{r.title}</a>
                  <p className="text-[#7A8BA0] mt-0.5">{r.snippet}</p>
                </div>
              ))}
            </div>
          )}
          <pre className="text-[10px] text-[#c8d4e0] font-mono overflow-x-auto mt-2 max-h-48 overflow-y-auto whitespace-pre-wrap">
            {JSON.stringify(result.result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function StepCard({ step, index, isLast }) {
  const [expanded, setExpanded] = useState(false);
  const typeColors = {
    thinking: '#60a5fa', executing: '#f59e0b', answer: '#00d4aa',
    complete: '#22c55e', validating: '#a78bfa', planning: '#f97316',
    question: '#ef4444',
  };
  const typeLabels = {
    thinking: 'Analyzing', executing: 'Executing', answer: 'Responding',
    complete: 'Complete', validating: 'Validating', planning: 'Planning (auto-continuing)',
    question: 'Needs Input',
  };
  const color = typeColors[step.type] || '#4A5B6E';
  const label = typeLabels[step.type] || step.type;

  return (
    <div className="relative" data-testid={`step-card-${index}`}>
      {/* Connector line */}
      {!isLast && <div className="absolute left-[15px] top-[30px] bottom-[-8px] w-[2px] bg-[#1B2D42]" />}
      <div className="flex items-start gap-3">
        {/* Step indicator */}
        <div
          className="w-[30px] h-[30px] rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 border-2"
          style={{ borderColor: color, color: color, background: `${color}10` }}
        >
          {step.step}
        </div>
        {/* Step content */}
        <div className="flex-1 min-w-0 pb-3">
          <button onClick={() => setExpanded(!expanded)} className="w-full text-left">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color }}>{label}</span>
              {step.provider && (
                <span className="text-[8px] px-1.5 py-0.5 rounded-full border border-[#1B2D42] text-[#4A5B6E]">{step.provider}</span>
              )}
              {step.tool_count > 0 && (
                <span className="text-[8px] px-1.5 py-0.5 rounded bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/20">
                  {step.tool_count} tool{step.tool_count > 1 ? 's' : ''}
                </span>
              )}
              {step.files_modified?.length > 0 && (
                <span className="text-[8px] px-1.5 py-0.5 rounded bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20">
                  {step.files_modified.length} file{step.files_modified.length > 1 ? 's' : ''} modified
                </span>
              )}
              {expanded ? <ChevronUp size={10} className="text-[#4A5B6E]" /> : <ChevronDown size={10} className="text-[#4A5B6E]" />}
            </div>
            {step.summary && <p className="text-[10px] text-[#7A8BA0] mt-1 line-clamp-2">{step.summary}</p>}
          </button>
          {expanded && step.thinking && (
            <div className="mt-2 rounded-md bg-[#152236]/60 border border-[#1B2D42] p-2.5" data-testid={`step-thinking-${index}`}>
              <div className="flex items-center gap-1.5 mb-1">
                <Brain size={10} className="text-[#a78bfa]" />
                <span className="text-[8px] font-bold uppercase tracking-wider text-[#a78bfa]">Reasoning</span>
              </div>
              <p className="text-[10px] text-[#8a9bb5] leading-relaxed whitespace-pre-wrap" style={{ maxHeight: '200px', overflow: 'auto' }}>
                {step.thinking}
              </p>
            </div>
          )}
          {expanded && step.tool_results?.length > 0 && (
            <div className="mt-2 space-y-1">
              {step.tool_results.map((tr, ti) => <ToolResultCard key={ti} result={tr} index={ti} />)}
            </div>
          )}
          {expanded && step.files_modified?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {step.files_modified.map((f, fi) => (
                <span key={fi} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-mono bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20">
                  <CheckCircle2 size={9} /> {f.split('/').pop()}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
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

const PROVIDERS = [
  { id: 'auto', label: 'Auto (Best Available)', color: '#00d4aa' },
  { id: 'groq', label: 'Groq / Llama 3.3 (Free)', color: '#f97316' },
  { id: 'cerebras', label: 'Cerebras / Llama 3.3 (Free)', color: '#22d3ee' },
  { id: 'huggingface', label: 'HuggingFace / Qwen Coder (Free)', color: '#fbbf24' },
  { id: 'claude', label: 'Claude Sonnet 4.5', color: '#a78bfa' },
  { id: 'gemini', label: 'Gemini 3 Flash', color: '#4285f4' },
  { id: 'gpt5', label: 'GPT-5', color: '#10a37f' },
  { id: 'openrouter', label: 'OpenRouter', color: '#06b6d4' },
];

export default function AIAgentsPage() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState('auto');
  const [modeOpen, setModeOpen] = useState(false);
  const [preferredProvider, setPreferredProvider] = useState('auto');
  const [providerOpen, setProviderOpen] = useState(false);
  const [fileExplorer, setFileExplorer] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [copied, setCopied] = useState(null);
  const [toolbarOpen, setToolbarOpen] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [urlInput, setUrlInput] = useState('');
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [urlLoading, setUrlLoading] = useState(false);
  const [taskProgress, setTaskProgress] = useState('');
  const [liveSteps, setLiveSteps] = useState([]);
  const [thinkingText, setThinkingText] = useState('');
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [apiKeys, setApiKeys] = useState({});
  const [keyInputs, setKeyInputs] = useState({ groq: '', cerebras: '', huggingface: '', openrouter: '', anthropic: '', openai: '' });
  const [keySaving, setKeySaving] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const pollingRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/agents/sessions`).then(r => r.ok ? r.json() : []).then(setSessions).catch(() => {});
    fetch(`${API}/agents/api-keys`).then(r => r.ok ? r.json() : {}).then(setApiKeys).catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, liveSteps]);

  const createSession = async () => {
    const res = await fetch(`${API}/agents/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_type: mode, title: 'New Session' }),
    });
    if (!res.ok) throw new Error(`Session creation failed: ${res.status}`);
    const session = await res.json();
    setSessions(prev => [session, ...prev]);
    setActiveSession(session.id);
    setMessages([]);
    inputRef.current?.focus();
    return session.id;
  };

  const loadSession = async (sid) => {
    const res = await fetch(`${API}/agents/sessions/${sid}`);
    if (!res.ok) return;
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

  const saveApiKey = async (provider) => {
    const key = keyInputs[provider];
    setKeySaving(provider);
    try {
      const res = await fetch(`${API}/agents/api-keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, key }),
      });
      if (res.ok) {
        const updated = await fetch(`${API}/agents/api-keys`).then(r => r.json());
        setApiKeys(updated);
        setKeyInputs(prev => ({ ...prev, [provider]: '' }));
      }
    } catch (e) { console.error(e); }
    setKeySaving(null);
  };

  const removeApiKey = async (provider) => {
    setKeySaving(provider);
    try {
      const res = await fetch(`${API}/agents/api-keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, key: '' }),
      });
      if (res.ok) {
        const updated = await fetch(`${API}/agents/api-keys`).then(r => r.json());
        setApiKeys(updated);
      }
    } catch (e) { console.error(e); }
    setKeySaving(null);
  };

  const pollTask = useCallback(async (taskId, sessionId, userMsg, currentAttachments) => {
    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/agents/tasks/${taskId}`);
        if (!res.ok) return;
        const data = await res.json();

        setTaskProgress(data.progress || '');
        if (data.steps) setLiveSteps(data.steps);
        if (data.thinking_text !== undefined) setThinkingText(data.thinking_text || '');

        if (data.status === 'complete' || data.status === 'error') {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
          setTaskProgress('');
          setLiveSteps([]);
          setThinkingText('');
          setLoading(false);

          setMessages(prev => [...prev, {
            role: 'assistant',
            content: data.response || `Error: ${data.progress}`,
            timestamp: data.timestamp || new Date().toISOString(),
            tool_calls_executed: data.tool_calls_executed || 0,
            files_modified: data.files_modified || [],
            questions: data.questions || [],
            tool_results: data.tool_results || [],
            steps: data.steps || [],
            agent_type: data.agent_type,
            provider: data.provider,
            iterations: data.iterations || 1,
            error: data.status === 'error',
          }]);

          setSessions(prev => prev.map(s =>
            s.id === sessionId ? { ...s, title: (userMsg || currentAttachments?.[0]?.name || '').slice(0, 80), updated_at: data.timestamp } : s
          ));
        }
      } catch {}
    }, 1200);
  }, []);

  useEffect(() => () => { if (pollingRef.current) clearInterval(pollingRef.current); }, []);

  const sendMessage = async () => {
    if ((!input.trim() && attachments.length === 0) || loading) return;
    let sessionId = activeSession;
    if (!sessionId) sessionId = await createSession();

    const userMsg = input.trim();
    const currentAttachments = [...attachments];
    setInput('');
    setAttachments([]);
    if (textareaRef.current) { textareaRef.current.style.height = 'auto'; }
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMsg,
      timestamp: new Date().toISOString(),
      attachments: currentAttachments.map(a => ({ name: a.name, type: a.type, size_kb: a.size_kb })),
    }]);
    setLoading(true);
    setTaskProgress('Starting...');
    setLiveSteps([]);
    setThinkingText('');

    try {
      let contextParts = [];
      if (selectedFile && fileContent) {
        contextParts.push(`[Code File: ${selectedFile}]\n\`\`\`\n${fileContent.slice(0, 8000)}\n\`\`\``);
      }
      for (const att of currentAttachments) {
        if (att.content) {
          contextParts.push(`[${att.type === 'url' ? 'URL' : 'File'}: ${att.name} (${att.size_kb}KB)]\n${att.content.slice(0, 15000)}`);
        }
      }
      const context = contextParts.join('\n\n---\n\n');

      const res = await fetch(`${API}/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_type: mode, message: userMsg || 'Analyze the attached content.', session_id: sessionId, context, preferred_provider: preferredProvider }),
      });

      if (!res.ok) throw new Error(`Engine error: ${res.status}`);
      const { task_id } = await res.json();
      pollTask(task_id, sessionId, userMsg, currentAttachments);
    } catch (err) {
      setLoading(false);
      setTaskProgress('');
      setLiveSteps([]);
      setThinkingText('');
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Error: ${err.message}`, timestamp: new Date().toISOString(), error: true,
      }]);
    }
  };

  const handleFileUpload = async (e) => {
    const fileList = Array.from(e.target.files || []);
    if (!fileList.length) return;
    for (const file of fileList) {
      const tempId = Math.random().toString(36).slice(2, 8);
      setAttachments(prev => [...prev, { id: tempId, name: file.name, type: 'uploading', content: '', size_kb: 0, uploading: true }]);
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API}/agents/upload`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
        const data = await res.json();
        setAttachments(prev => prev.map(a => a.id === tempId ? {
          id: data.id, name: data.filename, type: data.type, content: data.content, size_kb: data.size_kb, ext: data.ext, uploading: false,
        } : a));
      } catch (err) {
        setAttachments(prev => prev.map(a => a.id === tempId ? { ...a, uploading: false, type: 'error', content: err.message } : a));
      }
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleUrlSubmit = async () => {
    if (!urlInput.trim() || urlLoading) return;
    const url = urlInput.trim();
    setUrlLoading(true);
    const tempId = Math.random().toString(36).slice(2, 8);
    setAttachments(prev => [...prev, { id: tempId, name: url, type: 'uploading', content: '', size_kb: 0, uploading: true }]);
    setShowUrlInput(false);
    setUrlInput('');
    try {
      const res = await fetch(`${API}/agents/crawl-url`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (data.status === 'error') throw new Error(data.error);
      setAttachments(prev => prev.map(a => a.id === tempId ? {
        id: tempId, name: data.title || url, type: 'url', content: data.content, size_kb: data.size_kb, url: data.url, uploading: false,
      } : a));
    } catch (err) {
      setAttachments(prev => prev.map(a => a.id === tempId ? { ...a, uploading: false, type: 'error', content: err.message } : a));
    }
    setUrlLoading(false);
  };

  const removeAttachment = (id) => setAttachments(prev => prev.filter(a => a.id !== id));

  const autoResize = useCallback((el) => {
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }, []);

  const runTestQuery = async (queryType) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/agents/testing/query`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query_type: queryType }),
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
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path }),
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
      .replace(/```DONE[\s\S]*?```/g, '')
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
    'Show me routes_projects.py and suggest improvements',
    'Create a new API endpoint for project profitability report',
    'Explain Ind AS 115 revenue recognition for T&M projects',
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
              <div className="flex items-center gap-1.5">
                <h1 className="text-xs font-bold text-[#E8EDF2] leading-none">Kairos AI Engine</h1>
                <span className="text-[8px] px-1.5 py-0.5 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20 font-bold">v4</span>
              </div>
              <p className="text-[9px] text-[#4A5B6E] leading-none mt-0.5 flex items-center gap-1">
                <GitBranch size={8} /> 30 Tools &middot; 4 Subagents &middot; Image Gen &middot; 5 Providers
              </p>
            </div>
          </div>

          {/* Mode Selector */}
          <div className="relative ml-3">
            <button onClick={() => setModeOpen(!modeOpen)} data-testid="mode-selector"
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-bold border transition-all"
              style={{ background: `${currentMode.color}10`, color: currentMode.color, borderColor: `${currentMode.color}40` }}>
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
                      className={`w-full flex items-start gap-2 px-3 py-2.5 text-left transition-colors ${mode === m.id ? 'bg-[#152236]' : 'hover:bg-[#152236]/50'}`}>
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

          {/* Provider Selector */}
          <div className="relative ml-2">
            {(() => { const currentProvider = PROVIDERS.find(p => p.id === preferredProvider); return (
              <>
                <button onClick={() => setProviderOpen(!providerOpen)} data-testid="provider-selector"
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-bold border transition-all"
                  style={{ background: `${currentProvider.color}10`, color: currentProvider.color, borderColor: `${currentProvider.color}40` }}>
                  <Cpu size={11} />
                  {currentProvider.label}
                  <ChevronDown size={10} className={`transition-transform ${providerOpen ? 'rotate-180' : ''}`} />
                </button>
                {providerOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setProviderOpen(false)} />
                    <div className="absolute top-full left-0 mt-1 w-52 bg-[#0D1B2A] border border-[#1B2D42] rounded-lg shadow-xl z-50 overflow-hidden">
                      {PROVIDERS.map(p => (
                        <button key={p.id} data-testid={`provider-${p.id}`}
                          onClick={() => { setPreferredProvider(p.id); setProviderOpen(false); }}
                          className={`w-full flex items-center gap-2 px-3 py-2 text-left transition-colors ${preferredProvider === p.id ? 'bg-[#152236]' : 'hover:bg-[#152236]/50'}`}>
                          <div className="w-2 h-2 rounded-full shrink-0" style={{ background: p.color }} />
                          <p className="text-[11px] font-bold" style={{ color: preferredProvider === p.id ? p.color : '#E8EDF2' }}>{p.label}</p>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </>
            ); })()}
          </div>

          <div className="flex-1" />
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
            <button onClick={() => setShowApiKeys(!showApiKeys)} data-testid="api-keys-btn"
              className={`px-2 py-1.5 rounded text-[9px] font-bold border transition-colors flex items-center gap-1 ${
                Object.values(apiKeys).some(v => v?.configured)
                  ? 'bg-[#00d4aa]/10 border-[#00d4aa]/30 text-[#00d4aa]'
                  : 'bg-[#152236] border-[#1B2D42] text-[#4A5B6E] hover:text-[#a78bfa] hover:border-[#a78bfa]/30'
              }`}>
              <Key size={11} />API Keys
            </button>
          </div>
        </div>

        {/* Attached File Indicator */}
        {selectedFile && (
          <div className="px-3 py-1.5 bg-[#22c55e]/5 border-b border-[#22c55e]/20 flex items-center gap-2">
            <FileText size={11} className="text-[#22c55e]" />
            <span className="text-[10px] font-mono text-[#22c55e]">{selectedFile}</span>
            <span className="text-[9px] text-[#4A5B6E]">({(fileContent.length / 1024).toFixed(1)}KB attached)</span>
            <button onClick={() => { setSelectedFile(null); setFileContent(''); }} className="ml-auto text-[#4A5B6E] hover:text-[#ef4444] transition-colors"><X size={12} /></button>
          </div>
        )}

        {/* API Keys Settings Panel */}
        {showApiKeys && (
          <div className="border-b border-[#1B2D42] bg-[#060e1a] p-4" data-testid="api-keys-panel">
            <div className="max-w-2xl mx-auto space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-[#E8EDF2] flex items-center gap-2"><Key size={14} className="text-[#a78bfa]" /> Your API Keys</h3>
                  <p className="text-[10px] text-[#4A5B6E] mt-0.5">Add free API keys to run Kairos without any credits. Free providers are used first.</p>
                </div>
                <button onClick={() => setShowApiKeys(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={14} /></button>
              </div>
              <p className="text-[9px] text-[#00d4aa] bg-[#00d4aa]/5 border border-[#00d4aa]/15 rounded-lg px-3 py-1.5">Free tier providers — sign up and get an API key, no credit card required</p>
              {[
                { id: 'groq', label: 'Groq (Llama 3.3 70B)', placeholder: 'gsk_...', color: '#f97316', free: true, signup: 'console.groq.com' },
                { id: 'cerebras', label: 'Cerebras (Llama 3.3 70B)', placeholder: 'csk-...', color: '#22d3ee', free: true, signup: 'cloud.cerebras.ai' },
                { id: 'huggingface', label: 'HuggingFace (Qwen Coder 32B)', placeholder: 'hf_...', color: '#fbbf24', free: true, signup: 'huggingface.co/settings/tokens' },
                { id: 'openrouter', label: 'OpenRouter', placeholder: 'sk-or-v1-...', color: '#06b6d4', free: false },
                { id: 'anthropic', label: 'Anthropic (Claude)', placeholder: 'sk-ant-api03-...', color: '#a78bfa', free: false },
                { id: 'openai', label: 'OpenAI (GPT-4o)', placeholder: 'sk-proj-...', color: '#10a37f', free: false },
              ].map(p => (
                <div key={p.id} className="flex items-center gap-2" data-testid={`api-key-${p.id}`}>
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: apiKeys[p.id]?.configured ? p.color : '#1B2D42' }} />
                  <span className="text-[10px] font-bold text-[#7A8BA0] w-40 shrink-0 flex items-center gap-1.5">
                    {p.label}
                    {p.free && <span className="text-[8px] px-1 py-0 rounded bg-[#00d4aa]/15 text-[#00d4aa] border border-[#00d4aa]/20 font-bold">FREE</span>}
                  </span>
                  {apiKeys[p.id]?.configured ? (
                    <div className="flex-1 flex items-center gap-2">
                      <span className="text-[10px] font-mono text-[#00d4aa]">{apiKeys[p.id].masked}</span>
                      <span className="text-[8px] px-1.5 py-0.5 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20">active</span>
                      <button onClick={() => removeApiKey(p.id)} disabled={keySaving === p.id}
                        className="text-[9px] text-[#ef4444]/60 hover:text-[#ef4444] transition-colors ml-auto">
                        {keySaving === p.id ? <Loader2 size={10} className="animate-spin" /> : 'Remove'}
                      </button>
                    </div>
                  ) : (
                    <div className="flex-1 flex items-center gap-1.5">
                      <input
                        type="password"
                        placeholder={p.placeholder}
                        value={keyInputs[p.id]}
                        onChange={e => setKeyInputs(prev => ({ ...prev, [p.id]: e.target.value }))}
                        className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1 text-[10px] font-mono text-[#E8EDF2] placeholder-[#2A3F56] focus:border-[#00d4aa]/50 focus:outline-none"
                        data-testid={`api-key-input-${p.id}`}
                      />
                      <button onClick={() => saveApiKey(p.id)} disabled={!keyInputs[p.id] || keySaving === p.id}
                        className="px-2 py-1 rounded text-[9px] font-bold bg-[#00d4aa]/10 border border-[#00d4aa]/30 text-[#00d4aa] hover:bg-[#00d4aa]/20 transition-colors disabled:opacity-30"
                        data-testid={`api-key-save-${p.id}`}>
                        {keySaving === p.id ? <Loader2 size={10} className="animate-spin" /> : 'Save'}
                      </button>
                    </div>
                  )}
                </div>
              ))}
              <p className="text-[9px] text-[#2A3F56] mt-2">Keys are stored in your backend .env file. Free providers (Groq, Cerebras, HuggingFace) are prioritized first so you won't use any credits.</p>
            </div>
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
              <h2 className="text-lg font-bold text-[#E8EDF2] mb-1">Kairos AI Engine v4</h2>
              <p className="text-xs text-[#4A5B6E] max-w-md mb-2">
                Agentic AI developer with multi-step autonomous execution.
              </p>
              <div className="flex items-center gap-3 mb-6">
                <span className="text-[9px] px-2 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20">Subagents</span>
                <span className="text-[9px] px-2 py-1 rounded-full bg-[#a78bfa]/10 text-[#a78bfa] border border-[#a78bfa]/20">Live Thought Process</span>
                <span className="text-[9px] px-2 py-1 rounded-full bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/20">30 Tools + Image Gen</span>
              </div>
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
                  : msg.error ? 'bg-[#ef4444]/5 border border-[#ef4444]/20'
                  : 'bg-[#0A1628] border border-[#1B2D42]'
                }`}>
                  {msg.role === 'user' ? (
                    <div>
                      {msg.attachments && msg.attachments.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mb-2">
                          {msg.attachments.map((att, ai) => (
                            <span key={ai} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-mono bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20">
                              {att.type === 'url' ? <Globe size={9} /> : att.type === 'image' ? <Image size={9} /> : <FileText size={9} />}
                              {att.name?.length > 30 ? att.name.slice(0, 30) + '...' : att.name}
                            </span>
                          ))}
                        </div>
                      )}
                      {msg.content && <p className="text-xs text-[#E8EDF2] whitespace-pre-wrap">{msg.content}</p>}
                    </div>
                  ) : (
                    <div className="relative group">
                      <button onClick={() => copyText(msg.content, i)} data-testid={`copy-msg-${i}`}
                        className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 px-1.5 py-0.5 rounded text-[8px] font-bold border transition-all z-10"
                        style={{ background: copied === i ? '#065f46' : '#152236', color: copied === i ? '#34d399' : '#4A5B6E', borderColor: copied === i ? '#34d399' : '#1B2D42' }}>
                        {copied === i ? <><Check size={10} className="inline" /> Copied</> : <><Copy size={10} className="inline" /> Copy</>}
                      </button>
                      <div className="text-xs text-[#c8d4e0] leading-relaxed" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(renderMarkdown(msg.content)) }} />
                    </div>
                  )}
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <p className="text-[8px] text-[#4A5B6E]">{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}</p>
                    {msg.provider && (
                      <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded-full border ${
                        msg.provider === 'groq' ? 'text-[#f97316] bg-[#f97316]/10 border-[#f97316]/20'
                        : msg.provider === 'openrouter' ? 'text-[#06b6d4] bg-[#06b6d4]/10 border-[#06b6d4]/20'
                        : msg.provider === 'gemini' ? 'text-[#4285f4] bg-[#4285f4]/10 border-[#4285f4]/20'
                        : msg.provider === 'gpt5' ? 'text-[#10a37f] bg-[#10a37f]/10 border-[#10a37f]/20'
                        : 'text-[#a78bfa] bg-[#a78bfa]/10 border-[#a78bfa]/20'
                      }`}>
                        {msg.provider === 'groq' ? 'Groq / Llama 3.3' : msg.provider === 'openrouter' ? 'OpenRouter' : msg.provider === 'gemini' ? 'Gemini 3 Flash' : msg.provider === 'gpt5' ? 'GPT-5' : 'Claude'}
                      </span>
                    )}
                    {msg.iterations > 1 && (
                      <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20">
                        {msg.iterations} steps
                      </span>
                    )}
                  </div>
                </div>

                {/* Questions */}
                {msg.questions && msg.questions.length > 0 && (
                  <div className="mt-2 space-y-1.5">
                    {msg.questions.map((q, qi) => <QuestionBlock key={qi} question={q} />)}
                  </div>
                )}

                {/* Step-by-step execution trail */}
                {msg.steps && msg.steps.length > 1 && (
                  <StepTrail steps={msg.steps} />
                )}

                {/* Tool Results (for single-step or legacy messages) */}
                {msg.tool_results && msg.tool_results.length > 0 && (!msg.steps || msg.steps.length <= 1) && (
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

                {/* Files Modified */}
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

          {/* Live execution indicator */}
          {loading && (
            <div className="flex gap-3" data-testid="live-execution-indicator">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00d4aa]/20 to-[#00d4aa]/5 border border-[#00d4aa]/20 flex items-center justify-center shrink-0">
                <Loader2 size={13} className="animate-spin text-[#00d4aa]" />
              </div>
              <div className="flex-1 max-w-[78%]">
                <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-3">
                  <div className="flex items-center gap-2 text-xs text-[#4A5B6E] mb-2">
                    <span className="animate-pulse">{taskProgress || 'Engine processing...'}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#152236] border border-[#1B2D42]" style={{ color: currentMode.color }}>
                      {currentMode.label}
                    </span>
                  </div>
                  {/* Live Thought Process Panel */}
                  {thinkingText && (
                    <div className="mt-1 rounded-md bg-[#152236]/60 border border-[#1B2D42] p-2.5" data-testid="live-thinking-panel">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <Brain size={11} className="text-[#a78bfa]" />
                        <span className="text-[9px] font-bold uppercase tracking-wider text-[#a78bfa]">Kairos is reasoning</span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[#a78bfa] animate-pulse" />
                      </div>
                      <p className="text-[10px] text-[#8a9bb5] leading-relaxed whitespace-pre-wrap font-mono"
                         style={{ maxHeight: '120px', overflow: 'auto' }}>
                        {thinkingText}
                      </p>
                    </div>
                  )}
                </div>
                {/* Live steps */}
                {liveSteps.length > 0 && (
                  <div className="mt-2 space-y-1 ml-1">
                    {liveSteps.map((step, si) => (
                      <StepCard key={si} step={step} index={si} isLast={si === liveSteps.length - 1} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-[#1B2D42] bg-[#0A1628]">
          {attachments.length > 0 && (
            <div className="px-3 pt-2.5 flex flex-wrap gap-1.5" data-testid="attachment-chips">
              {attachments.map(att => (
                <div key={att.id} className={`inline-flex items-center gap-1.5 pl-2 pr-1 py-1 rounded-lg text-[10px] border transition-all ${
                  att.uploading ? 'bg-[#152236] border-[#1B2D42] text-[#4A5B6E]'
                  : att.type === 'error' ? 'bg-[#ef4444]/10 border-[#ef4444]/30 text-[#ef4444]'
                  : att.type === 'url' ? 'bg-[#60a5fa]/10 border-[#60a5fa]/25 text-[#60a5fa]'
                  : att.type === 'image' ? 'bg-[#a78bfa]/10 border-[#a78bfa]/25 text-[#a78bfa]'
                  : 'bg-[#22c55e]/10 border-[#22c55e]/25 text-[#22c55e]'
                }`}>
                  {att.uploading ? <Loader2 size={10} className="animate-spin" />
                   : att.type === 'url' ? <Globe size={10} />
                   : att.type === 'image' ? <Image size={10} />
                   : att.type === 'error' ? <AlertCircle size={10} />
                   : <FileText size={10} />}
                  <span className="font-medium max-w-[180px] truncate">{att.name}</span>
                  {!att.uploading && att.size_kb > 0 && <span className="text-[8px] opacity-60">{att.size_kb}KB</span>}
                  <button onClick={() => removeAttachment(att.id)} className="p-0.5 rounded hover:bg-white/10 transition-colors" data-testid={`remove-attachment-${att.id}`}>
                    <X size={10} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {showUrlInput && (
            <div className="px-3 pt-2" data-testid="url-input-bar">
              <div className="flex gap-2 items-center bg-[#152236] border border-[#60a5fa]/30 rounded-lg px-3 py-2">
                <Link2 size={13} className="text-[#60a5fa] shrink-0" />
                <input autoFocus value={urlInput} onChange={e => setUrlInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') handleUrlSubmit(); if (e.key === 'Escape') { setShowUrlInput(false); setUrlInput(''); } }}
                  placeholder="Paste any URL — website, article, docs..."
                  data-testid="url-input-field"
                  className="flex-1 bg-transparent text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none" />
                <button onClick={handleUrlSubmit} disabled={!urlInput.trim() || urlLoading} data-testid="url-submit-btn"
                  className="px-2.5 py-1 rounded text-[10px] font-bold bg-[#60a5fa]/15 text-[#60a5fa] border border-[#60a5fa]/30 hover:bg-[#60a5fa]/25 transition-all disabled:opacity-30">
                  {urlLoading ? <Loader2 size={11} className="animate-spin" /> : 'Fetch'}
                </button>
                <button onClick={() => { setShowUrlInput(false); setUrlInput(''); }} className="text-[#4A5B6E] hover:text-[#E8EDF2] transition-colors"><X size={13} /></button>
              </div>
            </div>
          )}

          <div className="p-3">
            <div className="flex items-end gap-2 bg-[#152236] border border-[#1B2D42] rounded-xl px-1 py-1 focus-within:border-[#00d4aa]/40 transition-colors">
              <div className="flex items-center gap-0.5 pl-1 pb-1">
                <input type="file" ref={fileInputRef} onChange={handleFileUpload} multiple className="hidden"
                  accept=".pdf,.docx,.doc,.xlsx,.xls,.pptx,.ppt,.csv,.txt,.md,.json,.xml,.py,.js,.jsx,.ts,.tsx,.html,.css,.png,.jpg,.jpeg,.gif,.webp,.svg" />
                <button onClick={() => fileInputRef.current?.click()} disabled={loading} data-testid="attach-file-btn"
                  title="Attach files" className="p-1.5 rounded-lg text-[#4A5B6E] hover:text-[#22c55e] hover:bg-[#22c55e]/10 transition-all disabled:opacity-30">
                  <Paperclip size={16} />
                </button>
                <button onClick={() => setShowUrlInput(!showUrlInput)} disabled={loading} data-testid="attach-url-btn"
                  title="Paste URL" className={`p-1.5 rounded-lg transition-all disabled:opacity-30 ${showUrlInput ? 'text-[#60a5fa] bg-[#60a5fa]/10' : 'text-[#4A5B6E] hover:text-[#60a5fa] hover:bg-[#60a5fa]/10'}`}>
                  <Globe size={16} />
                </button>
              </div>
              <textarea ref={el => { textareaRef.current = el; inputRef.current = el; }}
                value={input} onChange={e => { setInput(e.target.value); autoResize(e.target); }}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                placeholder="Describe what you need — I'll plan, execute, and verify autonomously..."
                disabled={loading} rows={1} data-testid="engine-input"
                className="flex-1 px-2 py-2 bg-transparent text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:outline-none disabled:opacity-50 resize-none max-h-40 leading-relaxed" />
              <div className="pb-1 pr-1">
                <button onClick={sendMessage} disabled={loading || (!input.trim() && attachments.length === 0)} data-testid="engine-send-btn"
                  className="p-2 rounded-lg bg-[#00d4aa]/15 text-[#00d4aa] border border-[#00d4aa]/30 hover:bg-[#00d4aa]/25 transition-all disabled:opacity-20">
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>
            </div>
            <p className="text-[9px] text-[#4A5B6E] mt-1.5 text-center">
              30 tools &middot; 4 subagents &middot; 5 LLM providers &middot; Batch ops &middot; Image gen &middot; Expanded context
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StepTrail({ steps }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="mt-2" data-testid="step-trail">
      <button onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider text-[#4A5B6E] hover:text-[#00d4aa] transition-colors">
        <GitBranch size={11} />
        {steps.length} execution step{steps.length > 1 ? 's' : ''}
        {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>
      {expanded && (
        <div className="mt-2 ml-1 space-y-1">
          {steps.map((step, si) => (
            <StepCard key={si} step={step} index={si} isLast={si === steps.length - 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function ChevronLeft(props) {
  return <ChevronRight {...props} style={{ transform: 'rotate(180deg)', ...props.style }} />;
}
