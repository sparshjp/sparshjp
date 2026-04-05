import React from 'react';
import { Package, TrendingUp, AlertTriangle } from 'lucide-react';

function Inventory() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="inventory-title">
            Inventory Management
          </h1>
          <p className="text-slate-500 mt-2">Track stock, BOM, and valuation (FIFO/Weighted Average)</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#002FA7]/10 rounded-sm inline-block mb-3">
              <Package className="text-[#002FA7]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Total Items</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#10B981]/10 rounded-sm inline-block mb-3">
              <TrendingUp className="text-[#10B981]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Total Value</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">₹0</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm">
            <div className="p-3 bg-[#FF3B30]/10 rounded-sm inline-block mb-3">
              <AlertTriangle className="text-[#FF3B30]" size={24} />
            </div>
            <p className="text-xs tracking-widest uppercase font-bold text-slate-500">Low Stock</p>
            <p className="heading-font text-3xl font-bold text-slate-900 mono mt-2">0</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="inventory-list">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-font text-xl font-bold text-slate-900">Inventory Items</h2>
            <select className="border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#002FA7]">
              <option>FIFO Valuation</option>
              <option>Weighted Average</option>
            </select>
          </div>
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm">
            <Package className="mx-auto mb-3 text-slate-300" size={48} />
            <p className="text-slate-500">No inventory items</p>
            <p className="text-sm text-slate-400 mt-1">Use AI Prompt to add stock</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Bill of Materials (BOM)</h2>
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm">
            <p className="text-slate-500">No BOMs defined</p>
          </div>
        </div>

        <div className="bg-[#F4F4F5] border border-slate-200 p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Features (Ind AS 2)</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>Landed Cost Calculation</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>FIFO / Weighted Average Valuation</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-[#002FA7] rounded-full"></span>
              <span>BOM for Manufacturing</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Inventory;