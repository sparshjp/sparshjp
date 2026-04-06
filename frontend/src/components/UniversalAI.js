import React, { useState, useEffect } from 'react';
import { MessageSquare, X, Send, Loader2, ChevronDown, Zap, FileText, ShoppingCart, Package } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const MODULE_FIELDS = {
  sales: {
    label: 'Sales Entry',
    icon: '📊',
    required: [
      { key: 'customer', label: 'Customer Name', type: 'text', placeholder: 'e.g. AutoDrive Systems Ltd.' },
      { key: 'customer_gstin', label: 'Customer GSTIN', type: 'text', placeholder: 'e.g. 27AABCA4567G1Z9' },
      { key: 'item', label: 'Item / Product', type: 'text', placeholder: 'e.g. MCU-X1' },
      { key: 'qty', label: 'Quantity', type: 'number', placeholder: '0' },
      { key: 'rate', label: 'Rate (INR)', type: 'number', placeholder: '0' },
    ],
    optional: [
      { key: 'gst_rate', label: 'GST Rate %', type: 'number', placeholder: '18' },
      { key: 'cost_center', label: 'Cost Center', type: 'text', placeholder: 'Sales & Marketing' },
    ],
  },
  purchase: {
    label: 'Purchase Entry',
    icon: '🛒',
    required: [
      { key: 'vendor', label: 'Vendor Name', type: 'text', placeholder: 'e.g. SiliconCore Supplies' },
      { key: 'vendor_gstin', label: 'Vendor GSTIN', type: 'text', placeholder: 'e.g. 27AABCS5678B1Z3' },
      { key: 'item', label: 'Item / Material', type: 'text', placeholder: 'e.g. RM-WAFER-6' },
      { key: 'qty', label: 'Quantity', type: 'number', placeholder: '0' },
      { key: 'rate', label: 'Rate (INR)', type: 'number', placeholder: '0' },
    ],
    optional: [
      { key: 'gst_rate', label: 'GST Rate %', type: 'number', placeholder: '18' },
      { key: 'cost_center', label: 'Cost Center', type: 'text', placeholder: 'Manufacturing' },
    ],
  },
  inventory: {
    label: 'Stock Entry',
    icon: '📦',
    required: [
      { key: 'item', label: 'Item Code', type: 'text', placeholder: 'e.g. MCU-X1' },
      { key: 'qty', label: 'Quantity', type: 'number', placeholder: '0' },
      { key: 'warehouse', label: 'Warehouse', type: 'text', placeholder: 'e.g. Main Warehouse' },
    ],
    optional: [
      { key: 'entry_type', label: 'Type', type: 'select', options: ['Material Receipt', 'Material Issue', 'Transfer'] },
      { key: 'rate', label: 'Valuation Rate', type: 'number', placeholder: '0' },
    ],
  },
  general: {
    label: 'General / Journal',
    icon: '📝',
    required: [],
    optional: [],
  }
};

export default function UniversalAI() {
  const [isOpen, setIsOpen] = useState(false);
  const [module, setModule] = useState('general');
  const [formData, setFormData] = useState({});
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [showModuleSelector, setShowModuleSelector] = useState(false);

  function buildPromptFromForm() {
    const fields = MODULE_FIELDS[module];
    let parts = [];
    if (module === 'sales') {
      parts.push(`Create Sales Invoice for customer ${formData.customer || '___'} (GSTIN: ${formData.customer_gstin || '___'})`);
      parts.push(`Item: ${formData.item || '___'}, Qty: ${formData.qty || 0}, Rate: Rs ${formData.rate || 0}`);
      if (formData.gst_rate) parts.push(`GST: ${formData.gst_rate}%`);
      if (formData.cost_center) parts.push(`Cost Center: ${formData.cost_center}`);
    } else if (module === 'purchase') {
      parts.push(`Create Purchase from vendor ${formData.vendor || '___'} (GSTIN: ${formData.vendor_gstin || '___'})`);
      parts.push(`Item: ${formData.item || '___'}, Qty: ${formData.qty || 0}, Rate: Rs ${formData.rate || 0}`);
      if (formData.gst_rate) parts.push(`GST: ${formData.gst_rate}%`);
      if (formData.cost_center) parts.push(`Cost Center: ${formData.cost_center}`);
    } else if (module === 'inventory') {
      parts.push(`${formData.entry_type || 'Stock Entry'}: ${formData.item || '___'}, Qty: ${formData.qty || 0}`);
      parts.push(`Warehouse: ${formData.warehouse || 'Main Warehouse'}`);
      if (formData.rate) parts.push(`Rate: Rs ${formData.rate}`);
    }
    return parts.join('. ');
  }

  function validateForm() {
    const fields = MODULE_FIELDS[module];
    for (const f of fields.required) {
      if (!formData[f.key] || formData[f.key] === '' || formData[f.key] === '0') return false;
    }
    return true;
  }

  async function handleSend() {
    const finalPrompt = module === 'general' ? prompt : (prompt || buildPromptFromForm());
    if (!finalPrompt.trim()) return;

    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: finalPrompt, module }]);

    try {
      if (module === 'general') {
        const r = await fetch(`${API}/api/ai/universal-prompt`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: finalPrompt, context: {} })
        });
        const data = await r.json();
        setMessages(prev => [...prev, { role: 'ai', content: JSON.stringify(data, null, 2), module: data.module || 'unknown' }]);
      } else if (module === 'sales') {
        const r = await fetch(`${API}/api/selling/invoices`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer: formData.customer,
            customer_gstin: formData.customer_gstin,
            items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
            gst_rate: parseFloat(formData.gst_rate) || 18,
            cost_center: formData.cost_center || 'Sales & Marketing',
          })
        });
        const data = await r.json();
        setMessages(prev => [...prev, {
          role: 'ai',
          content: `Sales Invoice ${data.invoice_number} created!\nCustomer: ${data.customer}\nSubtotal: Rs ${data.subtotal?.toLocaleString('en-IN')}\nGST: Rs ${data.gst_amount?.toLocaleString('en-IN')}\nTotal: Rs ${data.grand_total?.toLocaleString('en-IN')}\nCOGS: Rs ${data.cogs_total?.toLocaleString('en-IN')}\n\nJournal Entry auto-posted.`,
          module: 'sales'
        }]);
      } else if (module === 'purchase') {
        const r = await fetch(`${API}/api/purchase/grn`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            vendor: formData.vendor,
            items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
            gst_rate: parseFloat(formData.gst_rate) || 18,
            cost_center: formData.cost_center || 'Manufacturing',
          })
        });
        const data = await r.json();
        setMessages(prev => [...prev, {
          role: 'ai',
          content: `GRN ${data.grn_number} created!\nVendor: ${data.vendor}\nSubtotal: Rs ${data.subtotal?.toLocaleString('en-IN')}\nGST: Rs ${data.gst_amount?.toLocaleString('en-IN')}\nTotal: Rs ${data.grand_total?.toLocaleString('en-IN')}\n\nInventory updated + Journal Entry auto-posted.`,
          module: 'purchase'
        }]);
      } else if (module === 'inventory') {
        const r = await fetch(`${API}/api/stock/stock-entries`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stock_entry_type: formData.entry_type || 'Material Receipt',
            posting_date: new Date().toISOString().split('T')[0],
            to_warehouse: formData.warehouse || 'Main Warehouse',
            items: [{ item: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0 }]
          })
        });
        const data = await r.json();
        setMessages(prev => [...prev, { role: 'ai', content: `Stock entry created for ${formData.item} (${formData.qty} units).`, module: 'inventory' }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', content: `Error: ${e.message}`, module: 'error' }]);
    }

    setLoading(false);
    setPrompt('');
    setFormData({});
  }

  const fields = MODULE_FIELDS[module];

  return (
    <>
      {/* FAB Button */}
      {!isOpen && (
        <button
          data-testid="ai-fab-button"
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-24 w-14 h-14 bg-[#00C9A7] text-[#0D1B2A] rounded-full shadow-lg shadow-[#00C9A7]/30 flex items-center justify-center hover:bg-[#00B396] transition-all hover:scale-105 z-50"
        >
          <Zap className="w-6 h-6" />
        </button>
      )}

      {/* AI Panel */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 w-[420px] max-h-[80vh] bg-[#0D1B2A] border border-[#1B2D42] rounded-xl shadow-2xl shadow-black/40 z-50 flex flex-col" data-testid="ai-panel">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#1B2D42]">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#00C9A7] animate-pulse" />
              <span className="text-sm font-semibold text-[#E8EDF2]">Kairos AI</span>
              <span className="text-[10px] text-[#4A5B6E] bg-[#152236] px-2 py-0.5 rounded-full">{fields.label}</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-[#152236] rounded text-[#7A8BA0]"><X className="w-4 h-4" /></button>
          </div>

          {/* Module Selector */}
          <div className="flex gap-1 px-3 py-2 border-b border-[#1B2D42] bg-[#152236]/50">
            {Object.entries(MODULE_FIELDS).map(([key, val]) => (
              <button
                key={key}
                data-testid={`ai-module-${key}`}
                onClick={() => { setModule(key); setFormData({}); }}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                  module === key ? 'bg-[#00C9A7]/15 text-[#00C9A7] border border-[#00C9A7]/30' : 'text-[#4A5B6E] hover:text-[#7A8BA0] hover:bg-[#1B2D42]'
                }`}
              >
                {val.icon} {val.label.split(' ')[0]}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-[100px] max-h-[300px]">
            {messages.length === 0 && (
              <div className="text-center text-[#4A5B6E] text-xs py-4">
                {module === 'general'
                  ? 'Type anything — AI will route to the right module.'
                  : `Fill the required fields below to create a ${fields.label.toLowerCase()}.`}
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${
                  msg.role === 'user' ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'bg-[#152236] text-[#E8EDF2]'
                }`}>
                  <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[#152236] rounded-lg px-3 py-2 flex items-center gap-2">
                  <Loader2 className="w-3 h-3 animate-spin text-[#00C9A7]" />
                  <span className="text-xs text-[#4A5B6E]">Processing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Smart Form (for non-general modules) */}
          {module !== 'general' && fields.required.length > 0 && (
            <div className="px-3 py-2 border-t border-[#1B2D42] bg-[#152236]/30 space-y-2 max-h-[250px] overflow-y-auto">
              <p className="text-[10px] text-[#00C9A7] font-semibold tracking-wider uppercase">Required Fields</p>
              {fields.required.map(f => (
                <div key={f.key} className="flex items-center gap-2">
                  <label className="text-[10px] text-[#7A8BA0] w-24 flex-shrink-0">{f.label} *</label>
                  <input
                    data-testid={`ai-field-${f.key}`}
                    type={f.type}
                    placeholder={f.placeholder}
                    value={formData[f.key] || ''}
                    onChange={e => setFormData({...formData, [f.key]: e.target.value})}
                    className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-xs text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7] focus:ring-1 focus:ring-[#00C9A7]/20"
                  />
                </div>
              ))}
              {fields.optional.length > 0 && (
                <>
                  <p className="text-[10px] text-[#4A5B6E] tracking-wider uppercase mt-2">Optional</p>
                  {fields.optional.map(f => (
                    <div key={f.key} className="flex items-center gap-2">
                      <label className="text-[10px] text-[#4A5B6E] w-24 flex-shrink-0">{f.label}</label>
                      {f.type === 'select' ? (
                        <select
                          data-testid={`ai-field-${f.key}`}
                          value={formData[f.key] || ''}
                          onChange={e => setFormData({...formData, [f.key]: e.target.value})}
                          className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-xs text-[#E8EDF2]"
                        >
                          <option value="">Select</option>
                          {f.options?.map(o => <option key={o} value={o}>{o}</option>)}
                        </select>
                      ) : (
                        <input
                          data-testid={`ai-field-${f.key}`}
                          type={f.type}
                          placeholder={f.placeholder}
                          value={formData[f.key] || ''}
                          onChange={e => setFormData({...formData, [f.key]: e.target.value})}
                          className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-xs text-[#E8EDF2] placeholder-[#4A5B6E]"
                        />
                      )}
                    </div>
                  ))}
                </>
              )}
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t border-[#1B2D42]">
            <div className="flex gap-2">
              <input
                data-testid="ai-prompt-input"
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !loading && handleSend()}
                placeholder={module === 'general' ? 'Type anything...' : 'Add notes or just click Send'}
                className="flex-1 bg-[#152236] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] placeholder-[#4A5B6E] focus:border-[#00C9A7]"
                disabled={loading}
              />
              <button
                data-testid="ai-send-btn"
                onClick={handleSend}
                disabled={loading || (module !== 'general' && !validateForm())}
                className="px-3 py-2 bg-[#00C9A7] text-[#0D1B2A] rounded-lg font-semibold text-sm hover:bg-[#00B396] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
