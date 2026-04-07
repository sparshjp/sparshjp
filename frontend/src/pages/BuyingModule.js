import React, { useState, useEffect, useCallback } from 'react';
import { FileText, Package, Receipt, CreditCard, ArrowRight, CheckCircle, Clock, AlertCircle } from 'lucide-react';
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
    'Received': 'bg-[#00C9A7]/15 text-[#00C9A7]', 'To Invoice': 'bg-[#FFB547]/15 text-[#FFB547]',
    'Completed': 'bg-[#00C9A7]/15 text-[#00C9A7]', 'Paid': 'bg-[#00C9A7]/15 text-[#00C9A7]',
    'Unpaid': 'bg-[#FF4D6A]/15 text-[#FF4D6A]', 'Partially Paid': 'bg-[#FFB547]/15 text-[#FFB547]',
    'Pending': 'bg-[#FFB547]/15 text-[#FFB547]', 'Invoiced': 'bg-[#00C9A7]/15 text-[#00C9A7]',
    'Accepted': 'bg-[#00C9A7]/15 text-[#00C9A7]',
  };
  return <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${colors[status] || 'bg-[#1B2D42] text-[#7A8BA0]'}`}>{status}</span>;
}

export default function BuyingModule() {
  const [activeSection, setActiveSection] = useState('purchase-orders');
  const [orders, setOrders] = useState([]);
  const [grns, setGrns] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [pendingGRN, setPendingGRN] = useState([]);
  const [pendingInvoice, setPendingInvoice] = useState([]);
  const [outstanding, setOutstanding] = useState([]);
  const [processing, setProcessing] = useState(null);

  const loadData = useCallback(async () => {
    try {
      if (activeSection === 'purchase-orders') {
        const r = await fetch(`${API}/purchase/orders`); setOrders(await r.json());
      } else if (activeSection === 'grn') {
        const [pending, all] = await Promise.all([
          fetch(`${API}/purchase/grn/pending`).then(r => r.json()),
          fetch(`${API}/purchase/grn`).then(r => r.json())
        ]);
        setPendingGRN(pending); setGrns(all);
      } else if (activeSection === 'invoices') {
        const [pending, all] = await Promise.all([
          fetch(`${API}/purchase/invoices/pending`).then(r => r.json()),
          fetch(`${API}/purchase/invoices`).then(r => r.json())
        ]);
        setPendingInvoice(pending); setInvoices(all);
      } else if (activeSection === 'payments') {
        const [out, all] = await Promise.all([
          fetch(`${API}/purchase/payments/outstanding`).then(r => r.json()),
          fetch(`${API}/purchase/payments`).then(r => r.json())
        ]);
        setOutstanding(out); setPayments(all);
      }
    } catch (e) { console.error(e); }
  }, [activeSection]);

  useEffect(() => { loadData(); }, [loadData]);

  async function confirmReceipt(poId) {
    setProcessing(poId);
    try {
      const r = await fetch(`${API}/purchase/grn/from-po/${poId}`, { method: 'POST' });
      if (r.ok) { const grn = await r.json(); toast.success(`GRN ${grn.grn_number} created - Goods received, JE posted`); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
  }

  async function createInvoiceFromGRN(grnId) {
    setProcessing(grnId);
    try {
      const r = await fetch(`${API}/purchase/invoices/from-grn/${grnId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vendor_invoice_no: formData[`vinv_${grnId}`] || '' })
      });
      if (r.ok) { const inv = await r.json(); toast.success(`Invoice ${inv.invoice_number} created from GRN`); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
  }

  async function payInvoice(invId) {
    setProcessing(invId);
    try {
      const r = await fetch(`${API}/purchase/payments/for-invoice/${invId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_mode: 'Bank Transfer' })
      });
      if (r.ok) { const p = await r.json(); toast.success(`Payment ${p.payment_number} recorded - JE posted`); loadData(); }
      else { const err = await r.json(); toast.error(err.detail || 'Failed'); }
    } catch (e) { toast.error('Network error'); }
    finally { setProcessing(null); }
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
          <p className="text-[#4A5B6E] text-sm mt-1">PO &rarr; Goods Receipt &rarr; Invoice &rarr; Payment (Linked Flow + Auto JE)</p>
        </div>
      </div>

      {/* AI Prompt — replaces old form */}
      {activeSection === 'purchase-orders' && (
        <ModuleAIPrompt
          placeholder={`Describe your purchase... e.g. "PO for 5000 KG EP-1000 from Aditya Birla at 195/KG"`}
          defaultIntent="purchase_order"
          onCreated={loadData}
        />
      )}

      {/* Flow Navigation */}
      <div className="flex items-center gap-2 bg-[#152236] border border-[#1B2D42] rounded-lg p-3 overflow-x-auto">
        {sections.map((s, i) => (
          <React.Fragment key={s.id}>
            <button data-testid={`buying-tab-${s.id}`} onClick={() => { setActiveSection(s.id); }}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm whitespace-nowrap transition-all ${activeSection === s.id ? 'bg-[#00C9A7]/20 text-[#00C9A7] border border-[#00C9A7]/30' : 'text-[#7A8BA0] hover:text-[#E8EDF2] hover:bg-[#1B2D42]'}`}>
              <s.icon className="w-4 h-4" />{s.label}
              {s.id === 'grn' && pendingGRN.length > 0 && <span className="ml-1 bg-[#FFB547] text-[#0D1B2A] text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{pendingGRN.length}</span>}
              {s.id === 'invoices' && pendingInvoice.length > 0 && <span className="ml-1 bg-[#FFB547] text-[#0D1B2A] text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{pendingInvoice.length}</span>}
              {s.id === 'payments' && outstanding.length > 0 && <span className="ml-1 bg-[#FF4D6A] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{outstanding.length}</span>}
            </button>
            {i < sections.length - 1 && <ArrowRight className="w-4 h-4 text-[#4A5B6E] flex-shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* PURCHASE ORDERS TABLE */}
      {activeSection === 'purchase-orders' && (
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="buying-po-table">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
              <th className="py-2.5 px-4 text-left">PO #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-left">Items</th><th className="py-2.5 px-4 text-right">Subtotal</th><th className="py-2.5 px-4 text-right">GST</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">GRN</th><th className="py-2.5 px-4 text-center">Invoice</th><th className="py-2.5 px-4 text-center">Status</th>
            </tr></thead>
            <tbody>{orders.length === 0 ? (
              <tr><td colSpan={9} className="py-12 text-center text-[#4A5B6E]">No purchase orders yet. Create your first PO above.</td></tr>
            ) : orders.map(po => (
              <tr key={po.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{po.po_number}</td>
                <td className="py-2.5 px-4 text-[#E8EDF2]">{po.vendor}</td>
                <td className="py-2.5 px-4 text-[#7A8BA0] text-xs">{po.items?.map(i => `${i.item_code || i.item} x${i.qty}`).join(', ')}</td>
                <td className="py-2.5 px-4 text-right font-mono text-[#7A8BA0]">{formatINR(po.subtotal)}</td>
                <td className="py-2.5 px-4 text-right font-mono text-[#4A5B6E] text-xs">{formatINR(po.gst_amount)}</td>
                <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(po.grand_total)}</td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={po.grn_status} /></td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={po.invoice_status} /></td>
                <td className="py-2.5 px-4 text-center"><StatusBadge status={po.status} /></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {/* GRN - Pending Deliveries + Received */}
      {activeSection === 'grn' && (
        <div className="space-y-4">
          {pendingGRN.length > 0 && (
            <div className="bg-[#152236] border border-[#FFB547]/30 rounded-lg p-4" data-testid="buying-pending-grn">
              <h3 className="text-sm font-bold text-[#FFB547] mb-3 flex items-center gap-2"><Clock size={14} /> Pending Deliveries ({pendingGRN.length})</h3>
              {pendingGRN.map(po => (
                <div key={po.id} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg p-4 mb-2 flex items-center justify-between" data-testid={`pending-grn-${po.id}`}>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-mono text-xs font-bold text-[#00C9A7]">{po.po_number}</span>
                      <span className="text-[#E8EDF2] text-sm">{po.vendor}</span>
                    </div>
                    <p className="text-xs text-[#4A5B6E]">
                      Items: {po.items?.map(i => `${i.item_code || i.item} (${i.qty} x ${formatINR(i.rate)})`).join(', ')}
                      &nbsp;| Total: <span className="text-[#E8EDF2] font-mono">{formatINR(po.grand_total)}</span>
                    </p>
                  </div>
                  <button data-testid={`confirm-receipt-${po.id}`} onClick={() => confirmReceipt(po.id)} disabled={processing === po.id}
                    className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-xs font-semibold transition-colors disabled:opacity-50">
                    <CheckCircle size={14} /> {processing === po.id ? 'Processing...' : 'Confirm Receipt'}
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="buying-grn-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">Goods Received ({grns.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">GRN #</th><th className="py-2.5 px-4 text-left">PO #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Invoice</th><th className="py-2.5 px-4 text-center">QC</th>
              </tr></thead>
              <tbody>{grns.length === 0 ? (
                <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No goods received yet. Confirm receipt from Pending Deliveries above.</td></tr>
              ) : grns.map(g => (
                <tr key={g.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{g.grn_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{g.po_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{g.vendor}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(g.grand_total)}</td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={g.invoice_status} /></td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={g.qc_status} /></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </div>
      )}

      {/* INVOICES - Pending from GRN + All Invoices */}
      {activeSection === 'invoices' && (
        <div className="space-y-4">
          {pendingInvoice.length > 0 && (
            <div className="bg-[#152236] border border-[#FFB547]/30 rounded-lg p-4" data-testid="buying-pending-invoice">
              <h3 className="text-sm font-bold text-[#FFB547] mb-3 flex items-center gap-2"><AlertCircle size={14} /> Pending Invoices - Attach & Post ({pendingInvoice.length})</h3>
              {pendingInvoice.map(grn => (
                <div key={grn.id} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-lg p-4 mb-2" data-testid={`pending-inv-${grn.id}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-mono text-xs font-bold text-[#00C9A7]">{grn.grn_number}</span>
                        <span className="text-[#7A8BA0] text-xs">PO: {grn.po_number || '--'}</span>
                        <span className="text-[#E8EDF2] text-sm">{grn.vendor}</span>
                      </div>
                      <p className="text-xs text-[#4A5B6E]">
                        Items: {grn.items?.map(i => `${i.item_code || i.item} (${i.qty} @ ${formatINR(i.rate)})`).join(', ')}
                        &nbsp;| GST: {formatINR(grn.gst_amount)} | Total: <span className="text-[#E8EDF2] font-mono font-semibold">{formatINR(grn.grand_total)}</span>
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <input placeholder="Vendor Inv #" className="bg-[#152236] border border-[#1B2D42] rounded px-2 py-1.5 text-xs text-[#E8EDF2] w-32 placeholder:text-[#4A5B6E]"
                        value={formData[`vinv_${grn.id}`] || ''} onChange={e => setFormData({...formData, [`vinv_${grn.id}`]: e.target.value})} />
                      <button data-testid={`create-invoice-${grn.id}`} onClick={() => createInvoiceFromGRN(grn.id)} disabled={processing === grn.id}
                        className="flex items-center gap-1 px-3 py-1.5 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded text-xs font-semibold transition-colors disabled:opacity-50">
                        <Receipt size={12} /> {processing === grn.id ? 'Creating...' : 'Create Invoice'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="buying-invoices-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">All Purchase Invoices ({invoices.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">Invoice #</th><th className="py-2.5 px-4 text-left">GRN #</th><th className="py-2.5 px-4 text-left">PO #</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Total</th><th className="py-2.5 px-4 text-center">Payment</th>
              </tr></thead>
              <tbody>{invoices.length === 0 ? (
                <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No invoices yet. Create from pending GRNs above.</td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{inv.invoice_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{inv.grn_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{inv.po_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{inv.vendor}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#E8EDF2]">{formatINR(inv.grand_total)}</td>
                  <td className="py-2.5 px-4 text-center"><StatusBadge status={inv.status} /></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </div>
      )}

      {/* VENDOR PAYMENTS - Outstanding + History */}
      {activeSection === 'payments' && (
        <div className="space-y-4">
          {outstanding.length > 0 && (
            <div className="bg-[#152236] border border-[#FF4D6A]/30 rounded-lg p-4" data-testid="buying-outstanding">
              <h3 className="text-sm font-bold text-[#FF4D6A] mb-3 flex items-center gap-2"><AlertCircle size={14} /> Outstanding Invoices - Sorted by Days ({outstanding.length})</h3>
              <table className="w-full text-xs">
                <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase">
                  <th className="py-2 px-3 text-left">Invoice</th><th className="py-2 px-3 text-left">PO</th><th className="py-2 px-3 text-left">GRN</th><th className="py-2 px-3 text-left">Vendor</th><th className="py-2 px-3 text-left">Items</th><th className="py-2 px-3 text-right">Total</th><th className="py-2 px-3 text-right">Paid</th><th className="py-2 px-3 text-right">Balance</th><th className="py-2 px-3 text-center">Days</th><th className="py-2 px-3"></th>
                </tr></thead>
                <tbody>{outstanding.map(inv => (
                  <tr key={inv.id} className="border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/20" data-testid={`outstanding-${inv.id}`}>
                    <td className="py-2 px-3 text-[#00C9A7] font-mono font-semibold">{inv.invoice_number}</td>
                    <td className="py-2 px-3 text-[#7A8BA0] font-mono">{inv.po_number || '--'}</td>
                    <td className="py-2 px-3 text-[#7A8BA0] font-mono">{inv.grn_number || '--'}</td>
                    <td className="py-2 px-3 text-[#E8EDF2]">{inv.vendor}</td>
                    <td className="py-2 px-3 text-[#4A5B6E]">{inv.items?.map(i => i.item_code || i.item).join(', ')}</td>
                    <td className="py-2 px-3 text-right font-mono text-[#7A8BA0]">{formatINR(inv.grand_total)}</td>
                    <td className="py-2 px-3 text-right font-mono text-[#00C9A7]">{formatINR(inv.amount_paid)}</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-[#FF4D6A]">{formatINR(inv.balance_due)}</td>
                    <td className="py-2 px-3 text-center"><span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${inv.days_outstanding > 30 ? 'bg-[#FF4D6A]/15 text-[#FF4D6A]' : inv.days_outstanding > 15 ? 'bg-[#FFB547]/15 text-[#FFB547]' : 'bg-[#00C9A7]/15 text-[#00C9A7]'}`}>{inv.days_outstanding}d</span></td>
                    <td className="py-2 px-3">
                      <button data-testid={`pay-invoice-${inv.id}`} onClick={() => payInvoice(inv.id)} disabled={processing === inv.id}
                        className="px-3 py-1 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded text-[10px] font-semibold transition-colors disabled:opacity-50">
                        {processing === inv.id ? '...' : 'Pay'}
                      </button>
                    </td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          )}
          <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden" data-testid="buying-payments-table">
            <div className="px-4 py-3 border-b border-[#1B2D42]"><h3 className="text-sm font-bold text-[#E8EDF2]">Payment History ({payments.length})</h3></div>
            <table className="w-full text-sm">
              <thead><tr className="border-b border-[#1B2D42] text-[#4A5B6E] text-[10px] tracking-wider uppercase bg-[#1B2D42]/50">
                <th className="py-2.5 px-4 text-left">Payment #</th><th className="py-2.5 px-4 text-left">Invoice</th><th className="py-2.5 px-4 text-left">Vendor</th><th className="py-2.5 px-4 text-right">Amount</th><th className="py-2.5 px-4 text-left">Mode</th><th className="py-2.5 px-4 text-left">Date</th>
              </tr></thead>
              <tbody>{payments.length === 0 ? (
                <tr><td colSpan={6} className="py-8 text-center text-[#4A5B6E]">No payments yet.</td></tr>
              ) : payments.map(p => (
                <tr key={p.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/20">
                  <td className="py-2.5 px-4 text-[#00C9A7] font-mono text-xs font-semibold">{p.payment_number}</td>
                  <td className="py-2.5 px-4 text-[#7A8BA0] font-mono text-xs">{p.invoice_number || '--'}</td>
                  <td className="py-2.5 px-4 text-[#E8EDF2]">{p.vendor}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-semibold text-[#FF4D6A]">{formatINR(p.amount)}</td>
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
