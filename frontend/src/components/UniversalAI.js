import React, { useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Send, Loader2, Check, AlertCircle } from 'lucide-react';
import { SmartFormPopup } from './AISmartEntry';

const API = process.env.REACT_APP_BACKEND_URL;

const HIDDEN_ROUTES = ['/reporting-ai'];

const INTENT_CONFIG = {
  purchase_order: { label: 'Purchase Order', color: '#F59E0B' },
  sales_order: { label: 'Sales Order', color: '#10B981' },
  work_order: { label: 'Work Order', color: '#8B5CF6' },
  journal_entry: { label: 'Journal Entry', color: '#EC4899' },
  goods_receipt: { label: 'GRN', color: '#F97316' },
  delivery_note: { label: 'Delivery Note', color: '#06B6D4' },
  crm_lead: { label: 'CRM Lead', color: '#3B82F6' },
};


export default function UniversalAI() {
  const location = useLocation();
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsed, setParsed] = useState(null);
  const [masterData, setMasterData] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState(null);
  const [history, setHistory] = useState([]);
  const inputRef = useRef(null);

  // Hide on routes that have their own AI input
  if (HIDDEN_ROUTES.includes(location.pathname)) return null;

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleParse = async () => {
    if (!prompt.trim() || parsing) return;
    setParsing(true);
    try {
      const res = await fetch(`${API}/api/ai/parse-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Parse failed');
      const data = await res.json();
      setParsed(data);
      setMasterData(data.master_data || {});
    } catch (e) {
      showToast(e.message, 'error');
    }
    setParsing(false);
  };

  const handleConfirm = async (intent, payload) => {
    setSubmitting(true);
    try {
      let url = '', body = payload;

      switch (intent) {
        case 'purchase_order': url = `${API}/api/purchase/orders`; break;
        case 'sales_order': url = `${API}/api/selling/sales-orders`; break;
        case 'work_order':
          url = `${API}/api/manufacturing/work-orders`;
          body = { ...payload, bom_items: payload.bom_items || [] }; break;
        case 'journal_entry':
          url = `${API}/api/journal-entries/manual`;
          body = { posting_date: payload.posting_date || new Date().toISOString().split('T')[0], cost_center: payload.cost_center || 'General', journal_entries: payload.entries, narration: payload.narration }; break;
        case 'goods_receipt':
          url = `${API}/api/purchase/grn/from-po/${payload.po_id}`;
          body = {}; break;
        case 'delivery_note':
          url = `${API}/api/selling/delivery-notes/from-so/${payload.so_id}`;
          body = {}; break;
        case 'crm_lead':
          url = `${API}/api/crm/leads`;
          body = { lead_name: payload.contact_name, company_name: payload.company, ...payload }; break;
        default: throw new Error(`Unsupported intent: ${intent}`);
      }

      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail || JSON.stringify(err)); }
      const result = await res.json();

      const docId = result.po_number || result.so_number || result.wo_number || result.grn_number || result.id || 'Created';
      showToast(`${INTENT_CONFIG[intent]?.label || intent} ${docId} created!`, 'success');
      setHistory(prev => [{ prompt, intent, result: docId, time: new Date().toLocaleTimeString() }, ...prev.slice(0, 9)]);
      setParsed(null);
      setPrompt('');
    } catch (e) {
      showToast(e.message, 'error');
    }
    setSubmitting(false);
  };

  return (
    <>
      {/* Prompt Bar — fixed at bottom center */}
      <div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 w-full max-w-2xl px-4" data-testid="ai-prompt-bar">
        <div className="relative group">
          <div className="absolute -inset-[1px] bg-gradient-to-r from-[#00C9A7]/40 via-transparent to-[#00C9A7]/40 rounded-2xl opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity" />
          <div className="relative flex items-center bg-[#0D1B2A]/95 backdrop-blur-xl border border-[#1B2D42] rounded-2xl shadow-2xl shadow-black/40">
            <div className="flex items-center pl-4 pr-2">
              <span className="text-[#00C9A7] font-black text-sm leading-none tracking-tight select-none">K.</span>
            </div>
            <input
              ref={inputRef}
              data-testid="ai-prompt-input"
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleParse()}
              placeholder='Type a command... e.g. "Create PO for 5000 KG Epoxy Resin from Aditya Birla at 195/KG"'
              className="flex-1 bg-transparent py-3.5 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] outline-none"
              disabled={parsing}
            />
            <button
              data-testid="ai-send-btn"
              onClick={handleParse}
              disabled={parsing || !prompt.trim()}
              className="mr-2 px-4 py-2 bg-[#00C9A7] text-[#0D1B2A] rounded-xl font-bold text-xs hover:bg-[#00B396] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
            >
              {parsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              {parsing ? 'Parsing...' : 'Go'}
            </button>
          </div>
        </div>

        {/* Recent history chips */}
        {history.length > 0 && !parsed && (
          <div className="flex gap-2 mt-2 overflow-x-auto pb-1 scrollbar-hide">
            {history.slice(0, 4).map((h, i) => (
              <button key={i} onClick={() => setPrompt(h.prompt)}
                className="flex-shrink-0 px-3 py-1 rounded-full text-[10px] bg-[#152236]/80 border border-[#1B2D42] text-[#7A8BA0] hover:text-[#00C9A7] hover:border-[#00C9A7]/30 transition-colors">
                <span style={{ color: INTENT_CONFIG[h.intent]?.color }}>{INTENT_CONFIG[h.intent]?.label?.split(' ')[0]}</span> — {h.result}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Smart Popup */}
      {parsed && <SmartFormPopup parsed={parsed} masterData={masterData} onConfirm={handleConfirm} onCancel={() => setParsed(null)} loading={submitting} />}

      {/* Toast */}
      {toast && (
        <div className={`fixed top-5 right-5 z-[200] px-4 py-3 rounded-xl shadow-lg text-sm font-medium flex items-center gap-2 ${
          toast.type === 'success' ? 'bg-[#00C9A7] text-[#0D1B2A]' : 'bg-red-500 text-white'
        }`} data-testid="ai-toast">
          {toast.type === 'success' ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {toast.msg}
        </div>
      )}
    </>
  );
}
