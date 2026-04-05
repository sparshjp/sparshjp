import React from 'react';
import { TrendingUp, FileText, AlertCircle } from 'lucide-react';

function OrderToCash() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="o2c-title">
            Order-to-Cash
          </h1>
          <p className="text-slate-500 mt-2">Manage invoicing, revenue recognition, and receivables</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-[#002FA7]/10 rounded-sm">
                <FileText className="text-[#002FA7]" size={24} />
              </div>
              <h2 className="heading-font text-xl font-bold text-slate-900">Invoicing</h2>
            </div>
            <p className="text-sm text-slate-600 mb-4">Create proforma and GST tax invoices using AI prompts</p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between p-2 bg-slate-50 rounded-sm">
                <span className="text-slate-700">Proforma Invoices</span>
                <span className="mono text-slate-900 font-medium">0</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-50 rounded-sm">
                <span className="text-slate-700">GST Tax Invoices</span>
                <span className="mono text-slate-900 font-medium">0</span>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-[#10B981]/10 rounded-sm">
                <TrendingUp className="text-[#10B981]" size={24} />
              </div>
              <h2 className="heading-font text-xl font-bold text-slate-900">Revenue Recognition</h2>
            </div>
            <p className="text-sm text-slate-600 mb-4">Track unbilled revenue and accruals</p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between p-2 bg-slate-50 rounded-sm">
                <span className="text-slate-700">Unbilled Revenue</span>
                <span className="mono text-slate-900 font-medium">₹0.00</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-50 rounded-sm">
                <span className="text-slate-700">Accrued Revenue</span>
                <span className="mono text-slate-900 font-medium">₹0.00</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="accounts-receivable">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Accounts Receivable</h2>
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm">
            <AlertCircle className="mx-auto mb-3 text-slate-300" size={48} />
            <p className="text-slate-500">No outstanding invoices</p>
            <p className="text-sm text-slate-400 mt-1">Use AI Prompt to create invoices</p>
          </div>
        </div>

        <div className="bg-[#F4F4F5] border border-slate-200 p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Create Proforma Invoice
            </button>
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Generate GST Invoice
            </button>
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Record Unbilled Revenue
            </button>
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Match Payment to Invoice
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrderToCash;