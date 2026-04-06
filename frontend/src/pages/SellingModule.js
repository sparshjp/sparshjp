import React, { useState, useEffect, useCallback } from 'react';
import { FileText, Truck, Receipt, CreditCard, ArrowRight, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { ModuleAIPrompt } from '../components/AISmartEntry';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (!n && n !== 0) return '--';
  return new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
}

function StatusBadge({ status }) {
  const colors = {
    'Draft': 'bg-[#1B2D42] text-[#7A8BA0]', 'Submitted': 'bg-blue-500/20 text-blue-400',
    'Delivered': 'bg-[#00C9A7]/15 text-[#00C9A7]', 'Fully Delivered': 'bg-[#00C9A7]/15 text-[#00C9A7]',
    'Partially Delivered': 'bg-[#FFB547]/15 text-[#FFB547]', 'Not Delivered': 'bg-[#1B2D42] text-[#7A8BA0]',
    'Paid': 'bg-[#00C9A7]/15 text-[#00C9A7]', 'Unpaid': 'bg-[#FF4D6A]/15 text-[#FF4D6A]',
    'Partially Paid': 'bg-[#FFB547]/15 text-[#FFB547]', 'Fully Billed': 'bg-[#00C9A7]/15 text-[#00C9A7]',
    'Not Billed': 'bg-[#1B2D42] text-[#7A8BA0]', 'To Invoice': 'bg-[#FFB547]/15 text-[#FFB547]',
    'Pending': 'bg-[#FFB547]/15 text-[#FFB547]', 'Invoiced': 'bg-[#00C9A7]/15 text-[#00C9A7]',
    'Completed': 'bg-[#00C9A7]/15 text-[#00C9A7]',
  };
  return <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${colors[status] || 'bg-[#1B2D42] text-[#7A8BA0]'}`}>{status}</span>;
}

export default function SellingModule() {
  const [activeSection, setActiveSection] = useState('sales-orders');
  const [salesOrders, setSalesOrders] = useState([]);
  const [deliveryNotes, setDeliveryNotes] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [pendingDN, setPendingDN] = useState([]);
  const [pendingInvoice, setPendingInvoice] = useState([]);
  const [outstanding, setOutstanding] = useState([]);
  const [processing, setProcessing] = useState(null);

  const loadData = useCallback(async () => {
    try {
      if (activeSection === 'sales-orders') {
        const r = await fetch(`${API}/api/selling/sales-orders`); setSalesOrders(await r.json());
      } else if (activeSection === 'delivery-notes') {
        const [pending, all] = await Promise.all([
          fetch(`${API}/api/selling/delivery-notes/pending`).then(r => r.json()),
          fetch(`${API}/api/selling/delivery-notes`).then(r => r.json())
        ]);
        setPendingDN(pending); setDeliveryNotes(all);
      } else if (activeSection === 'invoices') {
        const [pending, all] = await Promise.all([
          fetch(`${API}/api/selling/invoices/pending`).then(r => r.json()),
          fetch(`${API}/api/selling/invoices`).then(r => r.json())
        ]);
        setPendingInvoice(pending); setInvoices(all);
      } else if (activeSection === 'payments') {
        const [out, all] = await Promise.all([
          fetch(`${API}/api/selling/payments/outstanding`).then(r => r.json()),
          fetch(`${API}/api/selling/payments`).then(r => r.json())
        ]);
        setOutstanding(out); setPayments(all);
      }
    } catch (e) { console.error(e); }
  }, [activeSection]);

  useEffect(() => { loadData(); }, [loadData]);

  async function confirmDelivery(soId) {
    setProcessing(soId);
    try {
      const r = await fetch(`${API}/api/selling/delivery-notes/from-so/${soId}`, { method: 'POST' });
      if (r.ok) { const dn = await r.json(); toast.success(`DN ${dn.dn_number} created - Goods dispatched`); if (dn.warning) toast.warning(dn.warning); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
  }

  async function createInvoiceFromDN(dnId) {
    setProcessing(dnId);
    try {
      const r = await fetch(`${API}/api/selling/invoices/from-dn/${dnId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({})
      });
      if (r.ok) { const inv = await r.json(); toast.success(`Invoice ${inv.invoice_number} created - Revenue + COGS JE posted`); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
  }

  async function receivePayment(invId) {
    setProcessing(invId);
    try {
      const r = await fetch(`${API}/api/selling/payments/for-invoice/${invId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_mode: 'Bank Transfer' })
      });
      if (r.ok) { const p = await r.json(); toast.success(`Payment ${p.payment_number} received - JE posted`); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
  }

  const sections = [
    { id: 'sales-orders', label: 'Sales Orders', icon: FileText },
    { id: 'delivery-notes', label: 'Delivery Notes', icon: Truck },
    { id: 'invoices', label: 'Sales Invoices', icon: Receipt },
    { id: 'payments', label: 'Payments', icon: CreditCard },
  ];

  return (
    <div className="space-y-6" data-testid="selling-module">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Selling</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">SO &rarr; Delivery Note &rarr; Invoice &rarr; Payment (Linked Flow + Auto JE)</p>
        </div>
        {activeSection === 'sales-orders' && (
          <button data-testid="selling-new-btn" onClick={() => {}}
            className="hidden">
          </button>
        )}
      </div>

      {/* Flow Navigation */}
      <div className="flex items-center gap-2 bg-[#152236] border border-[#1B2D42] rounded-lg p-3 overflow-x-auto">
        {sections.map((s, i) => (
          <React.Fragment key={s.id}>
            <button data-testid={`selling-tab-${s.id}`} onClick={() => { setActiveSection(s.id); }}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm whitespace-nowrap transition-all ${activeSection === s.id ? 'bg-[#00C9A7]/20 text-[#00C9A7] border border-[#00C9A7]/30' : 'text-[#7A8BA0] hover:text-[#E8EDF2] hover:bg-[#1B2D42]'}`}>
              <s.icon className="w-4 h-4" />{s.label}
              {s.id === 'delivery-notes' && pendingDN.length > 0 && <span className="ml-1 bg-[#FFB547] text-[#0D1B2A] text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{pendingDN.length}</span>}
              {s.id === 'invoices' && pendingInvoice.length > 0 && <span className="ml-1 bg-[#FFB547] text-[#0D1B2A] text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{pendingInvoice.length}</span>}
              {s.id === 'payments' && outstanding.length > 0 && <span className="ml-1 bg-[#FF4D6A] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{outstanding.length}</span>}
            </button>
            {i < sections.length - 1 && <ArrowRight className="w-4 h-4 text-[#4A5B6E] flex-shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* AI Prompt — replaces old form */}
      {activeSection === 'sales-orders' && (
        <ModuleAIPrompt
          placeholder={`Describe your sale... e.g. "SO for Asian Paints - 3000 KG EP-2500 at 520/KG"`}
          defaultIntent="sales_order"
          onCreated={loadData}
        />
      )}

      {/* SALES ORDERS TABLE */}
      {activeSection === 'sales-orders' && (
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="selling-so-table">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">SO #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-left">Items</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Delivery</th><th className="py-2.5 px-4 text-center">Billing</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{salesOrders.length === 0 ? (
              <tr><td colSpan={9} className="py-12 text-center text-[#4A5B6E]">No sales orders yet. Create your first SO above.</td></tr>
            ) : salesOrders.map(so => (
              <tr key={so.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{so.so_number}</td>
                <td className="py-2.5 px-4 text-[#E8EDF2]">{so.customer}</td>
                <td className="py-2.5 px-4 text-[#7A8BA0] text-xs">{so.items?.map(i => `${i.item_code || i.item} x${i.qty}`).join(', ')}</td>
                <td className="py-2.5 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(so.subtotal)}</td>
                <td className="py-2.5 px-4 text-right font-mono text-[#4A5B6E] text-xs">{formatINR(so.gst_amount)}</td>
                <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(so.grand_total)}</td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={so.delivery_status} /></td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={so.billing_status} /></td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={so.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {/* DELIVERY NOTES - Pending Dispatch + Delivered */}
      {activeSection === 'delivery-notes' && (
        <div className="space-y-4">
          {pendingDN.length > 0 && (
            <div className="bg-[#152236] border border-[#FFB547]/30 rounded-lg p-4" data-testid="selling-pending-dn">
              <h3 className="text-sm font-bold text-[#FFB547] mb-3 flex items-center gap-2"><Clock size={14} /> Pending Dispatch ({pendingDN.length})</h3>
              {pendingDN.map(so => (
                <div key={so.id} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg p-4 mb-2 flex items-center justify-between" data-testid={`pending-dn-${so.id}`}>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-mono text-xs font-bold text-[#00C9A7]">{so.so_number}</span>
                      <span className="text-[#E8EDF2] text-sm">{so.customer}</span>
                    </div>
                    <p className="text-xs text-[#4A5B6E]">
                      Items: {so.items?.map(i => `${i.item_code || i.item} (${i.qty} x ${formatINR(i.rate)})`).join(', ')}
                      &nbsp;| Total: <span className="text-[#E8EDF2] font-mono">{formatINR(so.grand_total)}</span>
                    </p>
                  </div>
                  <button data-testid={`confirm-delivery-${so.id}`} onClick={() => confirmDelivery(so.id)} disabled={processing === so.id}
                    className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-xs font-semibold transition-colors disabled:opacity-50">
                    <Truck size={14} /> {processing === so.id ? 'Processing...' : 'Confirm Delivery'}
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="selling-dn-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">Delivered ({deliveryNotes.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">DN #</th><th className="py-2.5 px-4 text-left">SO #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Qty</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Invoice</th><th className="py-2.5 px-4 text-center">Status</th>
              </tr></thead>
              <tbody>{deliveryNotes.length === 0 ? (
                <tr><td colSpan={7} className="py-8 text-center text-[#4A5B6E]">No deliveries yet. Confirm dispatch from Pending above.</td></tr>
              ) : deliveryNotes.map(dn => (
                <tr key={dn.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{dn.dn_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{dn.so_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{dn.customer}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-[#7A8BA0]">{dn.total_qty}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(dn.grand_total)}</td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={dn.invoice_status} /></td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={dn.status} /></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </div>
      )}

      {/* INVOICES - Pending from DN + All Invoices */}
      {activeSection === 'invoices' && (
        <div className="space-y-4">
          {pendingInvoice.length > 0 && (
            <div className="bg-[#152236] border border-[#FFB547]/30 rounded-lg p-4" data-testid="selling-pending-invoice">
              <h3 className="text-sm font-bold text-[#FFB547] mb-3 flex items-center gap-2"><AlertCircle size={14} /> Pending Invoices - Create & Post ({pendingInvoice.length})</h3>
              {pendingInvoice.map(dn => (
                <div key={dn.id} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg p-4 mb-2 flex items-center justify-between" data-testid={`pending-sinv-${dn.id}`}>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-mono text-xs font-bold text-[#00C9A7]">{dn.dn_number}</span>
                      <span className="text-[#7A8BA0] text-xs">SO: {dn.so_number || '--'}</span>
                      <span className="text-[#E8EDF2] text-sm">{dn.customer}</span>
                    </div>
                    <p className="text-xs text-[#4A5B6E]">
                      Items: {dn.items?.map(i => `${i.item_code || i.item} (${i.qty} @ ${formatINR(i.rate)})`).join(', ')}
                      &nbsp;| GST: {formatINR(dn.gst_amount)} | Total: <span className="text-[#E8EDF2] font-mono font-semibold">{formatINR(dn.grand_total)}</span>
                    </p>
                  </div>
                  <button data-testid={`create-sinvoice-${dn.id}`} onClick={() => createInvoiceFromDN(dn.id)} disabled={processing === dn.id}
                    className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-xs font-semibold transition-colors disabled:opacity-50">
                    <Receipt size={14} /> {processing === dn.id ? 'Creating...' : 'Create Invoice'}
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="selling-invoices-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">All Sales Invoices ({invoices.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">Invoice #</th><th className="py-2.5 px-4 text-left">DN #</th><th className="py-2.5 px-4 text-left">SO #</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Revenue</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-right">COGS</th><th className="py-2.5 px-4 text-center">Payment</th>
              </tr></thead>
              <tbody>{invoices.length === 0 ? (
                <tr><td colSpan={9} className="py-8 text-center text-[#4A5B6E]">No invoices yet. Create from delivered DNs above.</td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{inv.invoice_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{inv.dn_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{inv.so_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{inv.customer}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(inv.subtotal)}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-[#4A5B6E] text-xs">{formatINR(inv.gst_amount)}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(inv.grand_total)}</td>
                  <td className="py-2.5 px-4 text-right font-mono text-[#FF4D6A]">{formatINR(inv.cogs_total)}</td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={inv.status} /></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </div>
      )}

      {/* PAYMENTS - Outstanding + History */}
      {activeSection === 'payments' && (
        <div className="space-y-4">
          {outstanding.length > 0 && (
            <div className="bg-[#152236] border border-[#FF4D6A]/30 rounded-lg p-4" data-testid="selling-outstanding">
              <h3 className="text-sm font-bold text-[#FF4D6A] mb-3 flex items-center gap-2"><AlertCircle size={14} /> Accounts Receivable - Sorted by Days ({outstanding.length})</h3>
              <table className="w-full text-xs">
                <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase">
                  <th className="py-2 px-3 text-left">Invoice</th><th className="py-2 px-3 text-left">SO</th><th className="py-2 px-3 text-left">DN</th><th className="py-2 px-3 text-left">Customer</th><th className="py-2 px-3 text-left">Items</th><th className="py-2 px-3 text-right">Total</th><th className="py-2 px-3 text-right">Paid</th><th className="py-2 px-3 text-right">Balance</th><th className="py-2 px-3 text-center">Days</th><th className="py-2 px-3"></th>
                </tr></thead>
                <tbody>{outstanding.map(inv => (
                  <tr key={inv.id} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20" data-testid={`outstanding-ar-${inv.id}`}>
                    <td className="py-2 px-3 text-[#00C9A7] font-mono font-semibold">{inv.invoice_number}</td>
                    <td className="py-2 px-3 text-[#7A8BA0] font-mono">{inv.so_number || '--'}</td>
                    <td className="py-2 px-3 text-[#7A8BA0] font-mono">{inv.dn_number || '--'}</td>
                    <td className="py-2 px-3 text-[#E8EDF2]">{inv.customer}</td>
                    <td className="py-2 px-3 text-[#4A5B6E]">{inv.items?.map(i => i.item_code || i.item).join(', ')}</td>
                    <td className="py-2 px-3 text-right font-mono text-[#7A8BA0]">{formatINR(inv.grand_total)}</td>
                    <td className="py-2 px-3 text-right font-mono text-[#00C9A7]">{formatINR(inv.amount_paid)}</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-[#FF4D6A]">{formatINR(inv.balance_due)}</td>
                    <td className="py-2 px-3 text-center"><span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${inv.days_outstanding > 30 ? 'bg-[#FF4D6A]/15 text-[#FF4D6A]' : inv.days_outstanding > 15 ? 'bg-[#FFB547]/15 text-[#FFB547]' : 'bg-[#00C9A7]/15 text-[#00C9A7]'}`}>{inv.days_outstanding}d</span></td>
                    <td className="py-2 px-3">
                      <button data-testid={`receive-payment-${inv.id}`} onClick={() => receivePayment(inv.id)} disabled={processing === inv.id}
                        className="px-3 py-1 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded text-[10px] font-semibold transition-colors disabled:opacity-50">
                        {processing === inv.id ? '...' : 'Receive'}
                      </button>
                    </td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="selling-payments-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">Payment History ({payments.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">Payment #</th><th className="py-2.5 px-4 text-left">Invoice</th><th className="py-2.5 px-4 text-left">Customer</th><th className="py-2.5 px-4 text-right">Amount</th><th className="py-2.5 px-4 text-left">Mode</th><th className="py-2.5 px-4 text-left">Date</th>
              </tr></thead>
              <tbody>{payments.length === 0 ? (
                <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No payments yet.</td></tr>
              ) : payments.map(p => (
                <tr key={p.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{p.payment_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{p.invoice_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{p.customer}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#00C9A7]">{formatINR(p.amount)}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0]">{p.payment_mode}</td>
                  <td className="py-2.5 px-4 text-[#4A5B6E]">{p.payment_date}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
