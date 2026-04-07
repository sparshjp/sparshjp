import React, { useState, useEffect } from 'react';
import { Download, FileText, Copy, QrCode, ExternalLink, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

function formatINR(n) {
  if (n === undefined || n === null) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);
}

function SupplyBadge({ type }) {
  if (!type) return null;
  const isIGST = type.includes('IGST');
  return (
    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider ${isIGST ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>
      {isIGST ? 'IGST' : 'CGST+SGST'}
    </span>
  );
}

function StatusBadge({ status }) {
  return (
    <span className="px-2 py-0.5 rounded text-[9px] font-bold tracking-wider bg-[#00C9A7]/10 text-[#00C9A7] border border-[#00C9A7]/20">
      {status}
    </span>
  );
}

export default function EInvoicePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedInv, setSelectedInv] = useState(null);
  const [irnJson, setIrnJson] = useState(null);
  const [loadingJson, setLoadingJson] = useState(false);

  useEffect(() => {
    fetch(`${API}/statutory/e-invoices`).then(r => r.json()).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  async function viewIRN(invoiceNumber) {
    setLoadingJson(true);
    setSelectedInv(invoiceNumber);
    try {
      const r = await fetch(`${API}/statutory/e-invoice/${encodeURIComponent(invoiceNumber)}/json`);
      const d = await r.json();
      setIrnJson(d);
    } catch { toast.error('Failed to load IRN JSON'); }
    setLoadingJson(false);
  }

  function copyIRN() {
    if (irnJson) {
      navigator.clipboard.writeText(JSON.stringify(irnJson, null, 2));
      toast.success('IRN JSON copied to clipboard');
    }
  }

  if (loading) return <div className="text-[#4A5B6E] py-12 text-center">Loading E-Invoice data...</div>;

  return (
    <div className="space-y-5" data-testid="einvoice-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <QrCode className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#E8EDF2]">E-Invoicing</h1>
            <p className="text-[#4A5B6E] text-sm">IRN Generation for B2B Invoices — {data?.company?.legal_name}</p>
          </div>
        </div>
        <span className="text-xs text-[#4A5B6E] bg-[#152236] border border-[#1B2D42] px-3 py-1.5 rounded-lg">
          {data?.total || 0} eligible invoices
        </span>
      </div>

      {/* Info banner */}
      <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-4 flex items-start gap-3">
        <ExternalLink className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-[#7A8BA0] space-y-1">
          <p className="text-amber-400 font-medium">E-Invoice / IRN Compliance</p>
          <p>Businesses with aggregate turnover exceeding 5 Cr must generate e-invoices via the NIC portal. The JSON below follows the e-invoice schema v1.1 for direct upload.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Invoice list */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-[#1B2D42]">
            <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">B2B Invoices (IRN Eligible)</h3>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            {(data?.e_invoices || []).length === 0 ? (
              <div className="py-12 text-center text-[#4A5B6E] text-xs">
                <QrCode className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>No B2B invoices eligible for e-invoicing.</p>
                <p className="mt-1">Create sales invoices to customers with valid GSTINs to generate IRNs.</p>
              </div>
            ) : (data.e_invoices || []).map((inv, i) => (
              <button key={i} onClick={() => viewIRN(inv.invoice_number)}
                className={`w-full text-left px-4 py-3 border-b border-[#1B2D42]/30 hover:bg-[#1B2D42]/30 transition-colors ${selectedInv === inv.invoice_number ? 'bg-[#1B2D42]/40 border-l-2 border-l-[#00C9A7]' : ''}`}
                data-testid={`einvoice-row-${i}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[#00C9A7] font-mono text-xs font-bold">{inv.invoice_number}</span>
                      <SupplyBadge type={inv.supply_type} />
                      <StatusBadge status={inv.status} />
                    </div>
                    <p className="text-xs text-[#E8EDF2] mt-1">{inv.customer}</p>
                    <p className="text-[10px] text-[#4A5B6E] font-mono">{inv.customer_gstin}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-mono font-bold text-[#E8EDF2]">{formatINR(inv.grand_total)}</p>
                    <p className="text-[10px] text-[#4A5B6E]">{inv.invoice_date}</p>
                  </div>
                </div>
                <p className="text-[10px] text-[#4A5B6E] mt-1 font-mono truncate">IRN: {inv.irn}</p>
              </button>
            ))}
          </div>
        </div>

        {/* IRN JSON viewer */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-[#1B2D42] flex items-center justify-between">
            <h3 className="text-xs font-semibold text-[#00C9A7] tracking-wider uppercase">
              {selectedInv ? `IRN JSON — ${selectedInv}` : 'Select an invoice'}
            </h3>
            {irnJson && (
              <button onClick={copyIRN} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#00C9A7]/10 border border-[#00C9A7]/20 rounded text-xs text-[#00C9A7] hover:bg-[#00C9A7]/20 transition-colors">
                <Copy className="w-3 h-3" /> Copy JSON
              </button>
            )}
          </div>
          <div className="p-4 max-h-[500px] overflow-y-auto">
            {loadingJson ? (
              <p className="text-[#4A5B6E] text-xs text-center py-8">Loading IRN JSON...</p>
            ) : irnJson ? (
              <pre className="text-[11px] text-[#7A8BA0] font-mono whitespace-pre-wrap break-all" data-testid="irn-json">
                {JSON.stringify(irnJson, null, 2)}
              </pre>
            ) : (
              <div className="text-center py-12 text-[#4A5B6E]">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-xs">Click an invoice to view its IRN-ready JSON</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
