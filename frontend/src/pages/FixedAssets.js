import React from 'react';
import { Building, Calendar, TrendingDown } from 'lucide-react';

function FixedAssets() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="fixed-assets-title">
            Fixed Assets
          </h1>
          <p className="text-slate-500 mt-2">Track assets, depreciation (Schedule II), and deployment</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#002FA7]/10 rounded-sm inline-block mb-3">
              <Building className="text-[#002FA7]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Total Assets</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#10B981]/10 rounded-sm inline-block mb-3">
              <TrendingDown className="text-[#10B981]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Gross Value</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#FF3B30]/10 rounded-sm inline-block mb-3">
              <TrendingDown className="text-[#FF3B30]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Depreciation</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="assets-list">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Asset Register</h2>
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm">
            <Building className="mx-auto mb-3 text-slate-300" size={48} />
            <p className="text-slate-500">No fixed assets registered</p>
            <p className="text-sm text-slate-400 mt-1">Use AI Prompt to add assets</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4 flex items-center space-x-2">
            <Calendar size={20} />
            <span>Depreciation Schedule</span>
          </h2>
          <p className="text-sm text-slate-600 mb-4">Automated calculation per Schedule II (Companies Act, 2013)</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Asset</th>
                  <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Category</th>
                  <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Deploy Date</th>
                  <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-slate-500">Rate</th>
                  <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-slate-500">Annual Dep.</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-500">No depreciation entries</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-[#F4F4F5] border border-slate-200 p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Key Requirements</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Mandatory Deployment Date for depreciation start</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Automated depreciation as per Schedule II</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Separate tracking of gross value and accumulated depreciation</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default FixedAssets;