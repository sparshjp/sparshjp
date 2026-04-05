import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

function PurchaseToPay() {
  const [drafts, setDrafts] = useState([]);
  const [posted, setPosted] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTxn, setSelectedTxn] = useState(null);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const draftsRes = await axios.get(`${API}/transactions/drafts?module=purchase-to-pay`);
      const postedRes = await axios.get(`${API}/transactions/posted?module=purchase-to-pay&limit=50`);
      setDrafts(draftsRes.data);
      setPosted(postedRes.data);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handlePost = async (txnId) => {
    try {
      await axios.post(`${API}/transactions/post`, { transaction_id: txnId });
      toast.success('Transaction posted successfully');
      fetchTransactions();
      setSelectedTxn(null);
    } catch (error) {
      console.error('Failed to post transaction:', error);
      toast.error('Failed to post transaction');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="p2p-title">
            Purchase-to-Pay
          </h1>
          <p className="text-slate-500 mt-2">Manage vendor invoices, expenses, and payments</p>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4 flex items-center space-x-2">
            <Clock className="text-[#FFCC00]" size={20} />
            <span>Draft Transactions</span>
            <span className="mono text-sm bg-[#FFCC00]/10 px-2 py-1 rounded text-[#FFCC00]">{drafts.length}</span>
          </h2>

          {loading ? (
            <p className="text-slate-500 text-center py-8">Loading...</p>
          ) : drafts.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-sm" data-testid="no-drafts-message">
              <FileText className="mx-auto mb-3 text-slate-300" size={48} />
              <p className="text-slate-500">No draft transactions</p>
              <p className="text-sm text-slate-400 mt-1">Use the AI Prompt to create one</p>
            </div>
          ) : (
            <div className="space-y-4">
              {drafts.map((txn) => (
                <motion.div
                  key={txn.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-slate-200 p-4 rounded-sm hover:shadow-sm transition-all cursor-pointer"
                  onClick={() => setSelectedTxn(txn)}
                  data-testid={`draft-transaction-${txn.id}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900">{txn.user_prompt}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                        <span className="mono">{txn.posting_date || 'No date'}</span>
                        <span>{txn.business_unit || 'No BU'}</span>
                        <span className="mono bg-slate-100 px-2 py-1 rounded">{txn.id.slice(0, 8)}</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePost(txn.id);
                      }}
                      className="ml-4 bg-[#002FA7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium transition-colors"
                      data-testid={`post-button-${txn.id}`}
                    >
                      Post
                    </button>
                  </div>
                  {txn.journal_entries && txn.journal_entries.length > 0 && (
                    <div className="mt-4 p-3 bg-slate-50 rounded-sm">
                      <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2">Journal Entries</p>
                      <div className="space-y-1">
                        {txn.journal_entries.map((entry, idx) => (
                          <div key={idx} className="flex justify-between text-xs mono">
                            <span className="text-slate-700">{entry.account}</span>
                            <div className="space-x-4">
                              {entry.debit > 0 && <span className="text-green-600">Dr: ₹{entry.debit.toFixed(2)}</span>}
                              {entry.credit > 0 && <span className="text-red-600">Cr: ₹{entry.credit.toFixed(2)}</span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4 flex items-center space-x-2">
            <CheckCircle className="text-[#10B981]" size={20} />
            <span>Posted Transactions</span>
            <span className="mono text-sm bg-[#10B981]/10 px-2 py-1 rounded text-[#10B981]">{posted.length}</span>
          </h2>

          {posted.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No posted transactions yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="posted-transactions-table">
                <thead>
                  <tr className="border-b border-slate-200 text-left">
                    <th className="pb-2 font-bold text-xs tracking-widest uppercase text-slate-500">Date</th>
                    <th className="pb-2 font-bold text-xs tracking-widest uppercase text-slate-500">Description</th>
                    <th className="pb-2 font-bold text-xs tracking-widest uppercase text-slate-500">Business Unit</th>
                    <th className="pb-2 font-bold text-xs tracking-widest uppercase text-slate-500 text-right">ID</th>
                  </tr>
                </thead>
                <tbody>
                  {posted.map((txn) => (
                    <tr key={txn.id} className="border-b border-slate-100">
                      <td className="py-3 mono text-slate-900">{txn.posting_date}</td>
                      <td className="py-3 text-slate-700">{txn.user_prompt.slice(0, 60)}...</td>
                      <td className="py-3 text-slate-600">{txn.business_unit}</td>
                      <td className="py-3 mono text-slate-500 text-right">{txn.id.slice(0, 8)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PurchaseToPay;