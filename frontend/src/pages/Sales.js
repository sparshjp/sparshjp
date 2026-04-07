import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API } from '../App';
import { FileText, ShoppingCart, Truck } from 'lucide-react';
import { toast } from 'sonner';

function Sales() {
  const [activeTab, setActiveTab] = useState('quotations');
  const [quotations, setQuotations] = useState([]);
  const [salesOrders, setSalesOrders] = useState([]);
  const [deliveryNotes, setDeliveryNotes] = useState([]);

  const fetchQuotations = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sales/quotations`);
      setQuotations(res.data);
    } catch (error) {
      toast.error('Failed to fetch quotations');
    }
  }, []);

  const fetchSalesOrders = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sales/sales-orders`);
      setSalesOrders(res.data);
    } catch (error) {
      toast.error('Failed to fetch sales orders');
    }
  }, []);

  const fetchDeliveryNotes = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sales/delivery-notes`);
      setDeliveryNotes(res.data);
    } catch (error) {
      toast.error('Failed to fetch delivery notes');
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'quotations') fetchQuotations();
    else if (activeTab === 'sales-orders') fetchSalesOrders();
    else if (activeTab === 'delivery-notes') fetchDeliveryNotes();
  }, [activeTab, fetchQuotations, fetchSalesOrders, fetchDeliveryNotes]);

  const convertToSalesOrder = async (quotId) => {
    try {
      await axios.post(`${API}/sales/quotations/${quotId}/convert-to-sales-order`);
      toast.success('Converted to Sales Order!');
      fetchQuotations();
    } catch (error) {
      toast.error('Failed to convert');
    }
  };

  const tabs = [
    { id: 'quotations', label: 'Quotations', icon: FileText, count: quotations.length },
    { id: 'sales-orders', label: 'Sales Orders', icon: ShoppingCart, count: salesOrders.length },
    { id: 'delivery-notes', label: 'Delivery Notes', icon: Truck, count: deliveryNotes.length },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl font-black tracking-tighter text-[#E8EDF2]">Sales</h1>
        
        <div className="flex space-x-1 border-b border-[#1B2D42]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${
                  activeTab === tab.id ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
                <span className="mono text-xs px-2 py-0.5 rounded bg-[#1B2D42]">{tab.count}</span>
              </button>
            );
          })}
        </div>

        <div className="bg-[#152236] border border-[#1B2D42] rounded-sm p-6">
          {activeTab === 'quotations' && (
            quotations.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No quotations</p>
                <p className="text-sm text-[#4A5B6E] mt-1">Use AI: "Create quotation for ABC Corp - 100 laptops"</p>
              </div>
            ) : (
              <div className="space-y-4">
                {quotations.map((quot) => (
                  <div key={quot.id} className="border border-[#1B2D42] p-4 rounded-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold text-[#E8EDF2]">{quot.customer_name}</h3>
                        <p className="text-sm text-[#4A5B6E]">{quot.transaction_date}</p>
                        <p className="text-lg font-bold text-[#00C9A7] mt-2 mono">₹{quot.grand_total?.toLocaleString()}</p>
                      </div>
                      <div className="space-y-2">
                        <span className={`px-3 py-1 rounded text-xs font-medium ${
                          quot.status === 'Draft' ? 'bg-[#1B2D42] text-gray-700' :
                          quot.status === 'Submitted' ? 'bg-blue-100 text-blue-700' :
                          'bg-green-100 text-green-700'
                        }`}>{quot.status}</span>
                        {quot.status === 'Submitted' && (
                          <button
                            onClick={() => convertToSalesOrder(quot.id)}
                            className="block w-full text-xs px-3 py-1 bg-[#00C9A7] text-white rounded-sm"
                          >
                            Convert to SO
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {activeTab === 'sales-orders' && (
            salesOrders.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingCart className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No sales orders</p>
              </div>
            ) : (
              <div className="space-y-4">
                {salesOrders.map((so) => (
                  <div key={so.id} className="border border-[#1B2D42] p-4 rounded-sm">
                    <h3 className="font-bold text-[#E8EDF2]">{so.customer}</h3>
                    <p className="text-sm text-[#4A5B6E]">Delivery: {so.delivery_date || 'TBD'}</p>
                    <div className="mt-2 flex items-center space-x-4 text-xs">
                      <span className="mono">Qty: {so.total_qty}</span>
                      <span className="mono font-bold text-[#00C9A7]">₹{so.grand_total?.toLocaleString()}</span>
                      <span>Delivered: {so.per_delivered}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {activeTab === 'delivery-notes' && (
            deliveryNotes.length === 0 ? (
              <div className="text-center py-12">
                <Truck className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No deliveries</p>
              </div>
            ) : (
              <div className="space-y-4">
                {deliveryNotes.map((dn) => (
                  <div key={dn.id} className="border border-[#1B2D42] p-4 rounded-sm">
                    <h3 className="font-bold text-[#E8EDF2]">{dn.customer}</h3>
                    <p className="text-sm text-[#4A5B6E]">{dn.posting_date}</p>
                    {dn.vehicle_no && <p className="text-xs mono mt-2">Vehicle: {dn.vehicle_no}</p>}
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default Sales;
