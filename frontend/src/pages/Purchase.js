import React from 'react';
import { ShoppingCart } from 'lucide-react';

function Purchase() {
  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl font-black tracking-tighter text-slate-900">Purchase</h1>
        <div className="bg-white border border-slate-200 rounded-sm p-12 text-center">
          <ShoppingCart className="mx-auto mb-4 text-slate-300" size={64} />
          <p className="text-slate-600">Purchase module coming soon</p>
          <p className="text-sm text-slate-400 mt-2">Use AI: "Create PO for 100 units from Vendor X"</p>
        </div>
      </div>
    </div>
  );
}

export default Purchase;
