import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Package, ArrowUpDown, ClipboardList } from 'lucide-react';
import { toast } from 'sonner';

function Stock() {
  const [activeTab, setActiveTab] = useState('items');
  const [items, setItems] = useState([]);
  const [stockEntries, setStockEntries] = useState([]);
  const [reorderItems, setReorderItems] = useState([]);

  const fetchItems = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/stock/items`);
      setItems(res.data);
    } catch (error) {
      toast.error('Failed to fetch items');
    }
  }, []);

  const fetchStockEntries = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/stock/stock-entries`);
      setStockEntries(res.data);
    } catch (error) {
      toast.error('Failed to fetch stock entries');
    }
  }, []);

  const checkReorder = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/stock/items/check-reorder`);
      setReorderItems(res.data.items || []);
    } catch (error) {
      toast.error('Failed to check reorder');
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'items') fetchItems();
    else if (activeTab === 'stock-entries') fetchStockEntries();
    else if (activeTab === 'reorder') checkReorder();
  }, [activeTab, fetchItems, fetchStockEntries, checkReorder]);

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl font-black tracking-tighter text-[#E8EDF2]">Stock & Inventory</h1>
        
        <div className="flex space-x-1 border-b border-[#1B2D42]">
          <button onClick={() => setActiveTab('items')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'items' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <Package size={16} /><span>Items</span><span className="mono text-xs px-2 py-0.5 rounded bg-[#1B2D42]">{items.length}</span>
          </button>
          <button onClick={() => setActiveTab('stock-entries')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'stock-entries' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <ArrowUpDown size={16} /><span>Stock Entries</span>
          </button>
          <button onClick={() => setActiveTab('reorder')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'reorder' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <ClipboardList size={16} /><span>Reorder</span><span className="mono text-xs px-2 py-0.5 rounded bg-red-100 text-red-700">{reorderItems.length}</span>
          </button>
        </div>

        <div className="bg-[#152236] border border-[#1B2D42] rounded-sm p-6">
          {activeTab === 'items' && (
            items.length === 0 ? (
              <div className="text-center py-12"><Package className="mx-auto mb-3 text-slate-300" size={48} /><p className="text-[#4A5B6E]">No items</p><p className="text-sm text-[#4A5B6E] mt-1">Use AI: "Add item: Laptop, HSN 84713020, rate 50000"</p></div>
            ) : (
              <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="border-b border-[#1B2D42]"><th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Item</th><th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Stock</th><th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Rate</th><th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Value</th></tr></thead><tbody>{items.map(item => (<tr key={item.id} className="border-b border-slate-100"><td className="py-3"><div><p className="font-medium text-[#E8EDF2]">{item.item_name}</p><p className="text-xs text-[#4A5B6E] mono">{item.item_code}</p></div></td><td className="py-3 text-right mono">{item.current_stock} {item.stock_uom}</td><td className="py-3 text-right mono">₹{item.standard_rate?.toFixed(2)}</td><td className="py-3 text-right mono font-medium">₹{(item.current_stock * item.standard_rate)?.toFixed(2)}</td></tr>))}</tbody></table></div>
            )
          )}

          {activeTab === 'reorder' && (
            reorderItems.length === 0 ? (
              <div className="text-center py-12"><p className="text-green-600">All items are sufficiently stocked!</p></div>
            ) : (
              <div className="space-y-4">{reorderItems.map((item, idx) => (<div key={idx} className="border border-red-200 bg-[#FF4D6A]/10 p-4 rounded-sm"><h3 className="font-bold text-red-900">{item.item_name}</h3><p className="text-sm text-red-700 mt-1">Current: {item.current_stock} | Reorder Level: {item.reorder_level}</p><p className="text-sm font-medium text-[#FF4D6A] mt-2">Suggested Qty: {item.suggested_qty}</p></div>))}</div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default Stock;
