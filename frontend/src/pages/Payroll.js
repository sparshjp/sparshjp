import React from 'react';
import { Users, FileText, AlertCircle } from 'lucide-react';

function Payroll() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="payroll-title">
            Payroll & TDS
          </h1>
          <p className="text-slate-500 mt-2">Manage salaries, TDS calculation, and compliance</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#002FA7]/10 rounded-sm inline-block mb-3">
              <Users className="text-[#002FA7]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Employees</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#10B981]/10 rounded-sm inline-block mb-3">
              <FileText className="text-[#10B981]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Monthly Payroll</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#FF3B30]/10 rounded-sm inline-block mb-3">
              <AlertCircle className="text-[#FF3B30]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">TDS Payable</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="employee-list">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Employee Register</h2>
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm">
            <Users className="mx-auto mb-3 text-slate-300" size={48} />
            <p className="text-slate-500">No employees registered</p>
            <p className="text-sm text-slate-400 mt-1">Use AI Prompt to add employees</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">TDS Calculation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-sm">
              <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2">Old Tax Regime</p>
              <p className="text-sm text-slate-600">Slab-based with deductions (80C, 80D, etc.)</p>
              <p className="mono text-lg font-bold text-slate-900 mt-2">₹0</p>
            </div>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-sm">
              <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2">New Tax Regime</p>
              <p className="text-sm text-slate-600">Lower rates, no deductions</p>
              <p className="mono text-lg font-bold text-slate-900 mt-2">₹0</p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Compliance Reports</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Form 24Q
            </button>
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              Form 16
            </button>
            <button className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-900 px-4 py-3 rounded-sm text-sm font-medium transition-colors text-left">
              EPF/ESI Returns
            </button>
          </div>
        </div>

        <div className="bg-[#F4F4F5] border border-slate-200 p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Features</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Automated TDS calculation (Old vs. New Regime comparison)</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Form 24Q, Form 16, EPF/ESI compliance reports</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Employee-wise salary and deduction tracking</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Payroll;