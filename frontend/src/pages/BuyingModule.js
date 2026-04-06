import React, { useState, useEffect } from 'react';
import { Plus, FileText, Package, Receipt, CreditCard, ArrowRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (!n) return '0';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

function StatusBadge({ status }) {
  const colors = {
    'Draft': 'bg-zinc-700 text-[#7A8BA0]',
    'Submitted': 'bg-blue-500/20 text-blue-400',
    'Received': 'bg-[#00C9A7]/20 text-[#00C9A7]',
    'To Invoice': 'bg-[#00C9A7]/20 text-[#00C9A7]',
    'Completed': 'bg-[#00C9A7]/20 text-[#00C9A7]',
    'Paid': 'bg-[#00C9A7]/20 text-[#00C9A7]',
    'Unpaid': 'bg-[#FF4D6A]/20 text-[#FF4D6A]',
    'Partially Paid': 'bg-[#00C9A7]/20 text-[#00C9A7]',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-zinc-700 text-[#7A8BA0]'}`}>{status}</span>;
}

export default function BuyingModule() {
  const [activeSection, setActiveSection] = useState('purchase-orders');
  const [orders, setOrders] = useState([]);
  const [grns, setGrns] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => { loadData(); }, [activeSection]);

  async function loadData() {
    try {
      if (activeSection === 'purchase-orders') {
        const r = await fetch(`${API}/api/purchase/orders`); setOrders(await r.json());
      } else if (activeSection === 'grn') {
        const r = await fetch(`${API}/api/purchase/grn`); setGrns(await r.json());
      } else if (activeSection === 'invoices') {
        const r = await fetch(`${API}/api/purchase/invoices`); setInvoices(await r.json());
      } else if (activeSection === 'payments') {
        const r = await fetch(`${API}/api/purchase/payments`); setPayments(await r.json());
      }
    } catch (e) { console.error(e); }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      let endpoint = '';
      let body = {};
      if (activeSection === 'purchase-orders') {
        endpoint = '/api/purchase/orders';
        body = {
          vendor: formData.vendor,
          transaction_date: formData.date || new Date().toISOString().split('T')[0],
          delivery_date: formData.delivery_date,
          items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
          gst_rate: parseFloat(formData.gst_rate) || 18,
          cost_center: formData.cost_center || 'Manufacturing'
        };
      } else if (activeSection === 'grn') {
        endpoint = '/api/purchase/grn';
        body = {
          vendor: formData.vendor,
          posting_date: formData.date || new Date().toISOString().split('T')[0],
          purchase_order_ref: formData.po_ref,
          items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
          gst_rate: parseFloat(formData.gst_rate) || 18,
          cost_center: formData.cost_center || 'Manufacturing'
        };
      } else if (activeSection === 'invoices') {
        endpoint = '/api/purchase/invoices';
        body = {
          vendor: formData.vendor,
          posting_date: formData.date || new Date().toISOString().split('T')[0],
          items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
          gst_rate: parseFloat(formData.gst_rate) || 18,
        };
      } else if (activeSection === 'payments') {
        endpoint = '/api/purchase/payments';
        body = {
          vendor: formData.vendor,
          amount: parseFloat(formData.amount) || 0,
          payment_date: formData.date || new Date().toISOString().split('T')[0],
          payment_mode: formData.payment_mode || 'Bank Transfer',
        };
      }
      const r = await fetch(`${API}${endpoint}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      if (r.ok) { setShowForm(false); setFormData({}); loadData(); }
    } catch (e) { console.error(e); }
  }

  const sections = [
    { id: 'purchase-orders', label: 'Purchase Orders', icon: FileText },
    { id: 'grn', label: 'Goods Receipt', icon: Package },
    { id: 'invoices', label: 'Purchase Invoices', icon: Receipt },
    { id: 'payments', label: 'Vendor Payments', icon: CreditCard },
  ];

  return (
    <div className="space-y-6" data-testid="buying-module">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Buying</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Purchase Order > Goods Receipt > Invoice > Payment (Auto JE)</p>
        </div>
        <button data-testid="buying-new-btn" onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-amber-600 text-[#0D1B2A] rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> New
        </button>
      </div>

      {/* Flow */}
      <div className="flex items-center gap-2 bg-[#152236] border border-[#1B2D42] rounded-lg p-3 overflow-x-auto">
        {sections.map((s, i) => (
          <React.Fragment key={s.id}>
            <button data-testid={`buying-tab-${s.id}`} onClick={() => { setActiveSection(s.id); setShowForm(false); }}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm whitespace-nowrap transition-all ${activeSection === s.id ? 'bg-[#00C9A7]/20 text-[#00C9A7] border border-[#00C9A7]/30' : 'text-[#7A8BA0] hover:text-[#E8EDF2] hover:bg-[#1B2D42]'}`}>
              <s.icon className="w-4 h-4" />{s.label}
            </button>
            {i < sections.length - 1 && <ArrowRight className="w-4 h-4 text-[#4A5B6E] flex-shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-[#152236] border border-[#00C9A7]/30 rounded-lg p-6">
          <h3 className="text-sm font-bold text-[#00C9A7] mb-4">New {sections.find(s => s.id === activeSection)?.label}</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <input data-testid="buying-form-vendor" placeholder="Vendor" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.vendor || ''} onChange={e => setFormData({...formData, vendor: e.target.value})} required />
            <input data-testid="buying-form-date" type="date" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.date || ''} onChange={e => setFormData({...formData, date: e.target.value})} />
            {activeSection !== 'payments' && <>
              <input data-testid="buying-form-item" placeholder="Item Code" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.item || ''} onChange={e => setFormData({...formData, item: e.target.value})} />
              <input data-testid="buying-form-qty" placeholder="Qty" type="number" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.qty || ''} onChange={e => setFormData({...formData, qty: e.target.value})} />
              <input data-testid="buying-form-rate" placeholder="Rate" type="number" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.rate || ''} onChange={e => setFormData({...formData, rate: e.target.value})} />
            </>}
            {activeSection === 'payments' && (
              <input data-testid="buying-form-amount" placeholder="Amount" type="number" className="bg-[#1B2D42] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2]" value={formData.amount || ''} onChange={e => setFormData({...formData, amount: e.target.value})} required />
            )}
            <button data-testid="buying-form-submit" type="submit" className="px-4 py-2 bg-[#00C9A7] text-[#0D1B2A] rounded font-medium text-sm hover:bg-amber-600">Create</button>
          </form>
        </div>
      )}

      {/* Tables */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        {activeSection === 'purchase-orders' && (
          <table className="w-full text-sm" data-testid="buying-po-table">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">PO #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">GRN</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{orders.map(po => (
              <tr key={po.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{po.po_number}</td>
                <td className="py-2 px-4 text-[#E8EDF2]">{po.vendor}</td>
                <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(po.subtotal)}</td>
                <td className="py-2 px-4 text-right font-mono text-[#4A5B6E]">{formatINR(po.gst_amount)}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(po.grand_total)}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={po.grn_status} /></td>
                <td className="py-2 px-4 text-center"><StatusBadge status={po.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}
        {activeSection === 'grn' && (
          <table className="w-full text-sm" data-testid="buying-grn-table">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">GRN #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-left">Warehouse</th><th className="py-2.5 px-4 text-center">QC</th>
            </tr></thead>
            <tbody>{grns.map(g => (
              <tr key={g.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{g.grn_number}</td>
                <td className="py-2 px-4 text-[#E8EDF2]">{g.vendor}</td>
                <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(g.subtotal)}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(g.grand_total)}</td>
                <td className="py-2 px-4 text-[#7A8BA0]">{g.warehouse}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={g.qc_status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}
        {activeSection === 'invoices' && (
          <table className="w-full text-sm" data-testid="buying-invoices-table">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">Invoice #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{invoices.map(inv => (
              <tr key={inv.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{inv.invoice_number}</td>
                <td className="py-2 px-4 text-[#E8EDF2]">{inv.vendor}</td>
                <td className="py-2 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(inv.subtotal)}</td>
                <td className="py-2 px-4 text-right font-mono text-[#4A5B6E]">{formatINR(inv.gst_amount)}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(inv.grand_total)}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={inv.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}
        {activeSection === 'payments' && (
          <table className="w-full text-sm" data-testid="buying-payments-table">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-xs bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">Payment #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Amount</th><th className="py-2.5 px-4 text-left">Mode</th><th className="py-2.5 px-4 text-left">Date</th>
            </tr></thead>
            <tbody>{payments.map(p => (
              <tr key={p.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2 px-4 text-[#00C9A7] font-mono text-xs">{p.payment_number}</td>
                <td className="py-2 px-4 text-[#E8EDF2]">{p.vendor}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-[#FF4D6A]">{formatINR(p.amount)}</td>
                <td className="py-2 px-4 text-[#7A8BA0]">{p.payment_mode}</td>
                <td className="py-2 px-4 text-[#4A5B6E]">{p.payment_date}</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </div>
    </div>
  );
}
