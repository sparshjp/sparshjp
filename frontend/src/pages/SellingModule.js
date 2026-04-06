import React, { useState, useEffect } from 'react';
import { Plus, FileText, Truck, Receipt, CreditCard, ChevronDown, ChevronRight, ArrowRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (!n) return '0';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

function StatusBadge({ status }) {
  const colors = {
    'Draft': 'bg-zinc-700 text-zinc-300',
    'Submitted': 'bg-blue-500/20 text-blue-400',
    'Delivered': 'bg-emerald-500/20 text-emerald-400',
    'Fully Delivered': 'bg-emerald-500/20 text-emerald-400',
    'Partially Delivered': 'bg-amber-500/20 text-amber-400',
    'Paid': 'bg-emerald-500/20 text-emerald-400',
    'Unpaid': 'bg-red-500/20 text-red-400',
    'Partially Paid': 'bg-amber-500/20 text-amber-400',
    'Fully Billed': 'bg-emerald-500/20 text-emerald-400',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-zinc-700 text-zinc-300'}`}>{status}</span>;
}

export default function SellingModule() {
  const [activeSection, setActiveSection] = useState('sales-orders');
  const [salesOrders, setSalesOrders] = useState([]);
  const [deliveryNotes, setDeliveryNotes] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => { loadData(); }, [activeSection]);

  async function loadData() {
    try {
      if (activeSection === 'sales-orders') {
        const r = await fetch(`${API}/api/selling/sales-orders`);
        setSalesOrders(await r.json());
      } else if (activeSection === 'delivery-notes') {
        const r = await fetch(`${API}/api/selling/delivery-notes`);
        setDeliveryNotes(await r.json());
      } else if (activeSection === 'invoices') {
        const r = await fetch(`${API}/api/selling/invoices`);
        setInvoices(await r.json());
      } else if (activeSection === 'payments') {
        const r = await fetch(`${API}/api/selling/payments`);
        setPayments(await r.json());
      }
    } catch (e) { console.error(e); }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      let endpoint = '';
      let body = {};

      if (activeSection === 'sales-orders') {
        endpoint = '/api/selling/sales-orders';
        body = {
          customer: formData.customer,
          transaction_date: formData.date || new Date().toISOString().split('T')[0],
          delivery_date: formData.delivery_date,
          items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
          gst_rate: parseFloat(formData.gst_rate) || 18,
          cost_center: formData.cost_center || 'Sales & Marketing'
        };
      } else if (activeSection === 'invoices') {
        endpoint = '/api/selling/invoices';
        body = {
          customer: formData.customer,
          posting_date: formData.date || new Date().toISOString().split('T')[0],
          sales_order_ref: formData.so_ref,
          items: [{ item_code: formData.item, qty: parseFloat(formData.qty) || 0, rate: parseFloat(formData.rate) || 0, amount: (parseFloat(formData.qty) || 0) * (parseFloat(formData.rate) || 0) }],
          gst_rate: parseFloat(formData.gst_rate) || 18,
        };
      } else if (activeSection === 'payments') {
        endpoint = '/api/selling/payments';
        body = {
          customer: formData.customer,
          amount: parseFloat(formData.amount) || 0,
          payment_date: formData.date || new Date().toISOString().split('T')[0],
          payment_mode: formData.payment_mode || 'Bank Transfer',
          is_advance: formData.is_advance === 'true',
        };
      }

      const r = await fetch(`${API}${endpoint}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      if (r.ok) {
        setShowForm(false);
        setFormData({});
        loadData();
      }
    } catch (e) { console.error(e); }
  }

  const sections = [
    { id: 'sales-orders', label: 'Sales Orders', icon: FileText, count: salesOrders.length },
    { id: 'delivery-notes', label: 'Delivery Notes', icon: Truck, count: deliveryNotes.length },
    { id: 'invoices', label: 'Sales Invoices', icon: Receipt, count: invoices.length },
    { id: 'payments', label: 'Payments', icon: CreditCard, count: payments.length },
  ];

  return (
    <div className="space-y-6" data-testid="selling-module">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Selling</h1>
          <p className="text-zinc-500 text-sm mt-1">Quotation > Sales Order > Delivery > Invoice > Payment</p>
        </div>
        {['sales-orders', 'invoices', 'payments'].includes(activeSection) && (
          <button data-testid="selling-new-btn" onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-zinc-900 rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> New {activeSection === 'sales-orders' ? 'Sales Order' : activeSection === 'invoices' ? 'Invoice' : 'Payment'}
          </button>
        )}
      </div>

      {/* Flow diagram */}
      <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-lg p-3 overflow-x-auto">
        {sections.map((s, i) => (
          <React.Fragment key={s.id}>
            <button
              data-testid={`selling-tab-${s.id}`}
              onClick={() => { setActiveSection(s.id); setShowForm(false); }}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm whitespace-nowrap transition-all ${
                activeSection === s.id ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'
              }`}
            >
              <s.icon className="w-4 h-4" />
              {s.label}
            </button>
            {i < sections.length - 1 && <ArrowRight className="w-4 h-4 text-zinc-600 flex-shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-zinc-900 border border-amber-500/30 rounded-lg p-6">
          <h3 className="text-sm font-bold text-amber-400 mb-4">New {activeSection === 'sales-orders' ? 'Sales Order' : activeSection === 'invoices' ? 'Sales Invoice' : 'Payment'}</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <input data-testid="selling-form-customer" placeholder="Customer" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.customer || ''} onChange={e => setFormData({...formData, customer: e.target.value})} required />
            <input data-testid="selling-form-date" type="date" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.date || ''} onChange={e => setFormData({...formData, date: e.target.value})} />
            {activeSection !== 'payments' && <>
              <input data-testid="selling-form-item" placeholder="Item Code" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.item || ''} onChange={e => setFormData({...formData, item: e.target.value})} />
              <input data-testid="selling-form-qty" placeholder="Qty" type="number" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.qty || ''} onChange={e => setFormData({...formData, qty: e.target.value})} />
              <input data-testid="selling-form-rate" placeholder="Rate" type="number" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.rate || ''} onChange={e => setFormData({...formData, rate: e.target.value})} />
            </>}
            {activeSection === 'payments' && <>
              <input data-testid="selling-form-amount" placeholder="Amount" type="number" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.amount || ''} onChange={e => setFormData({...formData, amount: e.target.value})} required />
              <select data-testid="selling-form-mode" className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-200" value={formData.payment_mode || 'Bank Transfer'} onChange={e => setFormData({...formData, payment_mode: e.target.value})}>
                <option>Bank Transfer</option><option>Cash</option><option>Cheque</option><option>UPI</option>
              </select>
            </>}
            <button data-testid="selling-form-submit" type="submit" className="px-4 py-2 bg-amber-500 text-zinc-900 rounded font-medium text-sm hover:bg-amber-600">Create</button>
          </form>
        </div>
      )}

      {/* Data tables */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
        {activeSection === 'sales-orders' && (
          <table className="w-full text-sm" data-testid="selling-so-table">
            <thead><tr className="border-b border-zinc-700 text-zinc-500 text-xs bg-zinc-800/50">
              <th className="py-2.5 px-4 text-left">SO #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Delivery</th><th className="py-2.5 px-4 text-center">Billing</th>
            </tr></thead>
            <tbody>{salesOrders.map(so => (
              <tr key={so.id} className="border-b border-zinc-800/40 hover:bg-zinc-800/20">
                <td className="py-2 px-4 text-amber-400 font-mono text-xs">{so.so_number}</td>
                <td className="py-2 px-4 text-zinc-200">{so.customer}</td>
                <td className="py-2 px-4 text-right font-mono text-zinc-300">{formatINR(so.subtotal)}</td>
                <td className="py-2 px-4 text-right font-mono text-zinc-500">{formatINR(so.gst_amount)}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-zinc-100">{formatINR(so.grand_total)}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={so.delivery_status} /></td>
                <td className="py-2 px-4 text-center"><StatusBadge status={so.billing_status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}

        {activeSection === 'invoices' && (
          <table className="w-full text-sm" data-testid="selling-invoices-table">
            <thead><tr className="border-b border-zinc-700 text-zinc-500 text-xs bg-zinc-800/50">
              <th className="py-2.5 px-4 text-left">Invoice #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-right">COGS</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{invoices.map(inv => (
              <tr key={inv.id} className="border-b border-zinc-800/40 hover:bg-zinc-800/20">
                <td className="py-2 px-4 text-amber-400 font-mono text-xs">{inv.invoice_number}</td>
                <td className="py-2 px-4 text-zinc-200">{inv.customer}</td>
                <td className="py-2 px-4 text-right font-mono text-zinc-300">{formatINR(inv.subtotal)}</td>
                <td className="py-2 px-4 text-right font-mono text-zinc-500">{formatINR(inv.gst_amount)}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-zinc-100">{formatINR(inv.grand_total)}</td>
                <td className="py-2 px-4 text-right font-mono text-red-400">{formatINR(inv.cogs_total)}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={inv.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}

        {activeSection === 'payments' && (
          <table className="w-full text-sm" data-testid="selling-payments-table">
            <thead><tr className="border-b border-zinc-700 text-zinc-500 text-xs bg-zinc-800/50">
              <th className="py-2.5 px-4 text-left">Payment #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Amount</th><th className="py-2.5 px-4 text-left">Mode</th><th className="py-2.5 px-4 text-left">Date</th>
            </tr></thead>
            <tbody>{payments.map(p => (
              <tr key={p.id} className="border-b border-zinc-800/40 hover:bg-zinc-800/20">
                <td className="py-2 px-4 text-amber-400 font-mono text-xs">{p.payment_number}</td>
                <td className="py-2 px-4 text-zinc-200">{p.customer}</td>
                <td className="py-2 px-4 text-right font-mono font-semibold text-emerald-400">{formatINR(p.amount)}</td>
                <td className="py-2 px-4 text-zinc-400">{p.payment_mode}</td>
                <td className="py-2 px-4 text-zinc-500">{p.payment_date}</td>
              </tr>
            ))}</tbody>
          </table>
        )}

        {activeSection === 'delivery-notes' && (
          <table className="w-full text-sm" data-testid="selling-dn-table">
            <thead><tr className="border-b border-zinc-700 text-zinc-500 text-xs bg-zinc-800/50">
              <th className="py-2.5 px-4 text-left">DN #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Qty</th><th className="py-2.5 px-4 text-left">Warehouse</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{deliveryNotes.map(dn => (
              <tr key={dn.id} className="border-b border-zinc-800/40 hover:bg-zinc-800/20">
                <td className="py-2 px-4 text-amber-400 font-mono text-xs">{dn.dn_number}</td>
                <td className="py-2 px-4 text-zinc-200">{dn.customer}</td>
                <td className="py-2 px-4 text-right font-mono text-zinc-300">{dn.total_qty}</td>
                <td className="py-2 px-4 text-zinc-400">{dn.warehouse}</td>
                <td className="py-2 px-4 text-center"><StatusBadge status={dn.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </div>
    </div>
  );
}
