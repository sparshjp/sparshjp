import { useState, useRef, useEffect } from 'react';
import { API } from '../App';
import { Sparkles, Loader2, X, AlertTriangle, Check, ChevronDown, Plus, Trash2 } from 'lucide-react';

/**
 * AiEntryModal — AI-first data entry for any ERP module.
 * 
 * Props:
 *   module: string — module key matching backend MODULE_SCHEMAS (e.g. 'project', 'timesheet')
 *   title: string — modal title (e.g. "New Project")
 *   placeholder: string — AI prompt placeholder
 *   onSubmit: async (parsedData) => void — called with final confirmed data
 *   onClose: () => void
 *   open: boolean
 *   fieldOverrides: object — custom render/validation for specific fields
 *   existingData: object — pre-fill for edit mode
 */
export default function AiEntryModal({ module, title, placeholder, onSubmit, onClose, open, fieldOverrides = {}, existingData = null }) {
  const [step, setStep] = useState(existingData ? 'confirm' : 'prompt');
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [parsed, setParsed] = useState(existingData || {});
  const [schema, setSchema] = useState({});
  const [missing, setMissing] = useState([]);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (open && step === 'prompt' && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open, step]);

  useEffect(() => {
    if (existingData) {
      setParsed(existingData);
      setStep('confirm');
    }
  }, [existingData]);

  const parseWithAi = async () => {
    if (!prompt.trim()) return;
    setParsing(true);
    setError('');
    try {
      const res = await fetch(`${API}/ai/parse-entry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module, prompt: prompt.trim() }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'AI parsing failed');
      }
      const data = await res.json();
      setParsed(data.parsed || {});
      setSchema(data.schema || {});
      setMissing(data.missing_fields || []);
      setStep('confirm');
    } catch (e) {
      setError(e.message || 'Failed to parse. Try again or enter manually.');
    }
    setParsing(false);
  };

  const handleConfirm = async () => {
    // Check required fields
    const stillMissing = Object.entries(schema).filter(
      ([k, v]) => v.required && (parsed[k] === null || parsed[k] === undefined || parsed[k] === '')
    ).map(([k, v]) => v.label || k);
    if (stillMissing.length > 0) {
      setError(`Required fields still missing: ${stillMissing.join(', ')}`);
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await onSubmit(parsed);
      resetAndClose();
    } catch (e) {
      setError(e.message || 'Failed to save');
    }
    setSubmitting(false);
  };

  const resetAndClose = () => {
    setStep('prompt');
    setPrompt('');
    setParsed({});
    setSchema({});
    setMissing([]);
    setError('');
    onClose();
  };

  const updateField = (field, value) => {
    setParsed(prev => ({ ...prev, [field]: value }));
    setMissing(prev => prev.filter(m => m.field !== field));
  };

  const goBackToPrompt = () => {
    setStep('prompt');
    setError('');
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" onClick={resetAndClose} data-testid="ai-entry-modal">
      <div onClick={e => e.stopPropagation()} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[#1B2D42] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-[#00C9A7]" />
            <h2 className="text-lg font-bold text-[#E8EDF2]">{title}</h2>
            {step === 'confirm' && <span className="px-2 py-0.5 rounded-full text-[10px] bg-[#00C9A7]/15 text-[#00C9A7] font-bold uppercase">Review & Confirm</span>}
          </div>
          <button onClick={resetAndClose} className="text-[#4A5B6E] hover:text-[#E8EDF2] transition-colors" data-testid="ai-entry-close"><X size={18} /></button>
        </div>

        {/* Step 1: AI Prompt */}
        {step === 'prompt' && (
          <div className="p-6 space-y-4">
            <div className="bg-[#152236] rounded-lg p-4 border border-[#1B2D42]">
              <p className="text-xs text-[#4A5B6E] mb-3 uppercase tracking-wider">Describe what you want to create</p>
              <textarea
                ref={inputRef}
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); parseWithAi(); } }}
                placeholder={placeholder || `Describe the ${module} in natural language...`}
                className="w-full bg-[#0A1628] border border-[#1B2D42] rounded-lg px-4 py-3 text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7] resize-none h-24 placeholder:text-[#4A5B6E]/60"
                data-testid="ai-entry-prompt"
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-[10px] text-[#4A5B6E]">Press Enter to parse, Shift+Enter for new line</p>
                <div className="flex gap-2">
                  <button onClick={() => { setParsed({}); setSchema({}); setStep('confirm'); }} className="px-3 py-1.5 text-xs text-[#4A5B6E] hover:text-[#7A8BA0] border border-[#1B2D42] rounded-lg" data-testid="manual-entry-btn">Manual Entry</button>
                  <button onClick={parseWithAi} disabled={parsing || !prompt.trim()} className="px-4 py-1.5 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1.5 transition-all" data-testid="ai-parse-btn">
                    {parsing ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                    {parsing ? 'Parsing...' : 'Parse with AI'}
                  </button>
                </div>
              </div>
            </div>
            {error && <div className="flex items-center gap-2 text-sm text-[#ef4444] bg-[#ef4444]/10 rounded-lg px-4 py-2"><AlertTriangle size={14} />{error}</div>}
          </div>
        )}

        {/* Step 2: Confirm / Edit */}
        {step === 'confirm' && (
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {/* Missing fields alert */}
            {missing.length > 0 && (
              <div className="flex items-start gap-2 text-sm bg-[#f59e0b]/10 border border-[#f59e0b]/30 rounded-lg px-4 py-3">
                <AlertTriangle size={16} className="text-[#f59e0b] shrink-0 mt-0.5" />
                <div>
                  <p className="text-[#f59e0b] font-bold text-xs">Missing Required Fields</p>
                  <p className="text-[#f59e0b]/80 text-xs mt-0.5">{missing.map(m => m.label).join(', ')} — please fill them below</p>
                </div>
              </div>
            )}

            {error && <div className="flex items-center gap-2 text-sm text-[#ef4444] bg-[#ef4444]/10 rounded-lg px-4 py-2"><AlertTriangle size={14} />{error}</div>}

            {/* Field Grid */}
            <div className="space-y-3">
              {Object.entries(schema).length > 0 ? (
                Object.entries(schema).map(([field, def]) => {
                  const isMissing = missing.some(m => m.field === field);
                  const value = parsed[field];
                  const override = fieldOverrides[field];

                  // Custom render
                  if (override?.render) return override.render(value, v => updateField(field, v), def);

                  // Array of objects (milestones, entries, line_items, steps)
                  if (def.type === 'array_of_objects') {
                    return <ArrayField key={field} field={field} def={def} value={value} onChange={v => updateField(field, v)} />;
                  }

                  // Simple array (team_names)
                  if (def.type === 'array') {
                    const arrVal = Array.isArray(value) ? value.join(', ') : (value || '');
                    return (
                      <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                        <input value={arrVal} onChange={e => updateField(field, e.target.value.split(',').map(s => s.trim()).filter(Boolean))} placeholder="Comma-separated values" className="flex-1 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7]" data-testid={`field-${field}`} />
                      </FieldRow>
                    );
                  }

                  // Enum / select
                  if (def.type === 'enum' && def.options) {
                    return (
                      <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                        <select value={value ?? def.default ?? ''} onChange={e => updateField(field, e.target.value)} className="flex-1 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid={`field-${field}`}>
                          <option value="">Select...</option>
                          {def.options.map(o => <option key={o} value={o}>{o}</option>)}
                        </select>
                      </FieldRow>
                    );
                  }

                  // Boolean
                  if (def.type === 'boolean') {
                    return (
                      <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                        <label className="flex items-center gap-2 text-sm text-[#E8EDF2]">
                          <input type="checkbox" checked={value ?? def.default ?? false} onChange={e => updateField(field, e.target.checked)} className="rounded" data-testid={`field-${field}`} />
                          {value ? 'Yes' : 'No'}
                        </label>
                      </FieldRow>
                    );
                  }

                  // Number
                  if (def.type === 'number') {
                    return (
                      <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                        <input type="number" value={value ?? ''} onChange={e => updateField(field, Number(e.target.value) || 0)} placeholder={def.label} className="flex-1 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7]" data-testid={`field-${field}`} />
                      </FieldRow>
                    );
                  }

                  // Date
                  if (def.type === 'date') {
                    return (
                      <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                        <input type="date" value={value ?? ''} onChange={e => updateField(field, e.target.value)} className="flex-1 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7]" data-testid={`field-${field}`} />
                      </FieldRow>
                    );
                  }

                  // Default: text input
                  return (
                    <FieldRow key={field} label={def.label} required={def.required} missing={isMissing}>
                      <input value={value ?? ''} onChange={e => updateField(field, e.target.value)} placeholder={def.label} className="flex-1 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none focus:border-[#00C9A7]" data-testid={`field-${field}`} />
                    </FieldRow>
                  );
                })
              ) : (
                // Manual mode without schema — show raw JSON editor
                <div>
                  <p className="text-xs text-[#4A5B6E] mb-2">No schema loaded. Go back and use AI parse, or enter JSON manually:</p>
                  <textarea value={JSON.stringify(parsed, null, 2)} onChange={e => { try { setParsed(JSON.parse(e.target.value)); } catch {} }} className="w-full h-40 px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] font-mono outline-none" />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        {step === 'confirm' && (
          <div className="p-4 border-t border-[#1B2D42] flex items-center justify-between shrink-0">
            <button onClick={goBackToPrompt} className="px-4 py-2 text-sm text-[#4A5B6E] hover:text-[#7A8BA0] flex items-center gap-1" data-testid="ai-back-btn">
              <Sparkles size={14} /> Re-prompt with AI
            </button>
            <div className="flex gap-2">
              <button onClick={resetAndClose} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button onClick={handleConfirm} disabled={submitting} className="px-5 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1.5 transition-all" data-testid="ai-confirm-btn">
                {submitting ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
                {submitting ? 'Saving...' : 'Confirm & Save'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


function FieldRow({ label, required, missing, children }) {
  return (
    <div className={`flex items-center gap-3 ${missing ? 'bg-[#f59e0b]/5 rounded-lg p-2 -mx-2 border border-[#f59e0b]/20' : ''}`}>
      <label className="w-36 shrink-0 text-xs text-[#7A8BA0] text-right">
        {label}{required && <span className="text-[#ef4444] ml-0.5">*</span>}
      </label>
      {children}
    </div>
  );
}


function ArrayField({ field, def, value, onChange }) {
  const items = Array.isArray(value) ? value : [];

  const addItem = () => {
    const template = {};
    if (def.fields) {
      Object.entries(def.fields).forEach(([k, type]) => {
        template[k] = type === 'number' ? 0 : type === 'boolean' ? false : '';
      });
    }
    onChange([...items, template]);
  };

  const updateItem = (idx, key, val) => {
    const updated = [...items];
    updated[idx] = { ...updated[idx], [key]: val };
    onChange(updated);
  };

  const removeItem = (idx) => onChange(items.filter((_, i) => i !== idx));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs text-[#7A8BA0]">{def.label}{def.required && <span className="text-[#ef4444] ml-0.5">*</span>}</label>
        <button type="button" onClick={addItem} className="text-xs text-[#00C9A7] hover:underline flex items-center gap-0.5"><Plus size={12} /> Add</button>
      </div>
      {items.map((item, idx) => (
        <div key={idx} className="flex gap-2 items-start bg-[#152236] rounded-lg p-2">
          <span className="text-[10px] text-[#4A5B6E] mt-2 w-4">{idx + 1}</span>
          <div className="flex-1 flex gap-2 flex-wrap">
            {def.fields && Object.entries(def.fields).map(([k, type]) => (
              <input key={k} type={type === 'number' ? 'number' : type === 'date' ? 'date' : 'text'} placeholder={k} value={item[k] ?? ''} onChange={e => updateItem(idx, k, type === 'number' ? Number(e.target.value) : e.target.value)} className="px-2 py-1 bg-[#0A1628] border border-[#1B2D42] rounded text-xs text-[#E8EDF2] outline-none flex-1 min-w-[100px]" data-testid={`${field}-${idx}-${k}`} />
            ))}
          </div>
          <button type="button" onClick={() => removeItem(idx)} className="text-[#ef4444] hover:bg-[#ef4444]/10 p-1 rounded shrink-0"><Trash2 size={12} /></button>
        </div>
      ))}
      {items.length === 0 && <p className="text-[10px] text-[#4A5B6E] italic pl-4">No items. Click + Add to create one.</p>}
    </div>
  );
}
