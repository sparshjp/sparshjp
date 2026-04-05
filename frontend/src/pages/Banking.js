import React from 'react';
import { Landmark, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

function Banking() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="banking-title">
            Banking & Reconciliation
          </h1>
          <p className="text-slate-500 mt-2">Bank reconciliation and cash management</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#10B981]/10 rounded-sm inline-block mb-3">
              <CheckCircle className="text-[#10B981]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Matched</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#FF3B30]/10 rounded-sm inline-block mb-3">
              <XCircle className="text-[#FF3B30]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Unmatched</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#002FA7]/10 rounded-sm inline-block mb-3">
              <Landmark className="text-[#002FA7]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Bank Balance</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="bank-reconciliation">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-font text-xl font-bold text-slate-900">Bank Reconciliation</h2>
            <button className="bg-[#002FA7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium transition-colors">
              Upload Statement
            </button>
          </div>
          <p className="text-sm text-slate-600 mb-4">AI matches bank statements to ledger entries automatically</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Date</th>
                  <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Description</th>
                  <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-slate-500">Amount</th>
                  <th className="pb-2 text-center font-bold text-xs tracking-widest uppercase text-slate-500">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan="4" className="py-12 text-center text-slate-500">
                    No bank transactions to reconcile
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <div className="flex items-center space-x-2 mb-4">
            <AlertCircle className="text-[#FFCC00]" size={20} />
            <h2 className="heading-font text-xl font-bold text-slate-900">Physical Cash Reconciliation</h2>
          </div>
          <p className="text-sm text-slate-600 mb-4">System-triggered prompts to confirm physical cash counts</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-sm">
              <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-1">Book Balance</p>
              <p className="mono text-2xl font-bold text-slate-900">₹0.00</p>
            </div>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-sm">
              <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-1">Physical Count</p>
              <p className="mono text-2xl font-bold text-slate-900">₹0.00</p>
            </div>
          </div>
        </div>

        <div className="bg-[#F4F4F5] border border-slate-200 p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Reconciliation Features</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>AI-powered bank statement matching</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Unmatched items highlighted with prompt-based resolution</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Scheduled physical cash count verification</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Banking;