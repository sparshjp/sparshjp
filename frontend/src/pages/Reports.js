import React, { useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { MessageSquare, Send, BarChart3, TrendingUp, DollarSign } from 'lucide-react';
import { toast } from 'sonner';

function Reports() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [profitLoss, setProfitLoss] = useState(null);
  const [trialBalance, setTrialBalance] = useState(null);

  const handleQuery = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    try {
      setLoading(true);
      const res = await axios.post(`${API}/reports/query`, { query });
      setResponse(res.data);
      toast.success('Query processed');
    } catch (error) {
      console.error('Query error:', error);
      toast.error('Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const fetchBalanceSheet = async () => {
    try {
      const res = await axios.get(`${API}/reports/balance-sheet`);
      setBalanceSheet(res.data);
    } catch (error) {
      console.error('Failed to fetch balance sheet:', error);
    }
  };

  const fetchProfitLoss = async () => {
    try {
      const today = new Date();
      const startDate = `${today.getFullYear()}-04-01`;
      const endDate = today.toISOString().split('T')[0];
      const res = await axios.get(`${API}/reports/profit-loss?start_date=${startDate}&end_date=${endDate}`);
      setProfitLoss(res.data);
    } catch (error) {
      console.error('Failed to fetch P&L:', error);
    }
  };

  const fetchTrialBalance = async () => {
    try {
      const res = await axios.get(`${API}/reports/trial-balance`);
      setTrialBalance(res.data);
    } catch (error) {
      console.error('Failed to fetch trial balance:', error);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="reports-title">
            Reports & Analytics
          </h1>
          <p className="text-[#4A5B6E] mt-2">AI-powered conversational reporting and financial statements</p>
        </div>

        <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm tracing-beam" data-testid="ai-report-bot">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-[#00C9A7]/10 rounded-sm">
              <MessageSquare className="text-[#00C9A7]" size={24} />
            </div>
            <div>
              <h2 className="heading-font text-xl font-bold text-[#E8EDF2]">AI Insight Bot</h2>
              <p className="text-xs text-[#4A5B6E]">Ask questions about your financial data</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Example: Show me all electricity spends for Gujarat plant in 2025"
                className="flex-1 bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-3 text-sm text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                data-testid="ai-query-input"
                onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              />
              <button
                onClick={handleQuery}
                disabled={loading}
                className="bg-[#00C9A7] hover:bg-[#002480] text-white px-6 py-3 rounded-sm font-medium transition-colors flex items-center space-x-2 disabled:opacity-50"
                data-testid="submit-query-button"
              >
                <Send size={18} />
              </button>
            </div>

            {response && (
              <div className="p-4 bg-[#152236] border border-[#1B2D42] rounded-sm" data-testid="ai-response">
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">AI Response</p>
                <p className="text-sm text-[#7A8BA0] leading-relaxed">{response.answer}</p>
                <p className="text-xs text-[#4A5B6E] mt-2 mono">Based on {response.data_points} transactions</p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button
            onClick={fetchBalanceSheet}
            className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm hover:shadow-sm transition-all text-left"
            data-testid="balance-sheet-button"
          >
            <BarChart3 className="text-[#00C9A7] mb-3" size={32} />
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2]">Balance Sheet</h3>
            <p className="text-sm text-[#4A5B6E] mt-1">Assets, Liabilities, Equity</p>
          </button>

          <button
            onClick={fetchProfitLoss}
            className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm hover:shadow-sm transition-all text-left"
            data-testid="profit-loss-button"
          >
            <TrendingUp className="text-[#10B981] mb-3" size={32} />
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2]">Profit & Loss</h3>
            <p className="text-sm text-[#4A5B6E] mt-1">Revenue, Expenses, Net Profit</p>
          </button>

          <button
            onClick={fetchTrialBalance}
            className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm hover:shadow-sm transition-all text-left"
            data-testid="trial-balance-button"
          >
            <DollarSign className="text-[#FFCC00] mb-3" size={32} />
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2]">Trial Balance</h3>
            <p className="text-sm text-[#4A5B6E] mt-1">All Account Balances</p>
          </button>
        </div>

        {balanceSheet && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="balance-sheet-data">
            <h3 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Balance Sheet</h3>
            <p className="text-xs text-[#4A5B6E] mono mb-4">As of: {balanceSheet.as_of_date}</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">Assets</p>
                <div className="space-y-1 text-sm">
                  {Object.entries(balanceSheet.assets).length > 0 ? (
                    Object.entries(balanceSheet.assets).map(([acc, bal]) => (
                      <div key={acc} className="flex justify-between mono">
                        <span>{acc}</span>
                        <span>₹{(bal.debit - bal.credit).toFixed(2)}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-[#4A5B6E]">No assets</p>
                  )}
                </div>
              </div>
              <div>
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">Liabilities</p>
                <div className="space-y-1 text-sm">
                  {Object.entries(balanceSheet.liabilities).length > 0 ? (
                    Object.entries(balanceSheet.liabilities).map(([acc, bal]) => (
                      <div key={acc} className="flex justify-between mono">
                        <span>{acc}</span>
                        <span>₹{(bal.credit - bal.debit).toFixed(2)}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-[#4A5B6E]">No liabilities</p>
                  )}
                </div>
              </div>
              <div>
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">Equity</p>
                <div className="space-y-1 text-sm">
                  {Object.entries(balanceSheet.equity).length > 0 ? (
                    Object.entries(balanceSheet.equity).map(([acc, bal]) => (
                      <div key={acc} className="flex justify-between mono">
                        <span>{acc}</span>
                        <span>₹{(bal.credit - bal.debit).toFixed(2)}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-[#4A5B6E]">No equity</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {profitLoss && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="profit-loss-data">
            <h3 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Profit & Loss Statement</h3>
            <p className="text-xs text-[#4A5B6E] mono mb-4">
              Period: {profitLoss.period.start} to {profitLoss.period.end}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">Revenue</p>
                <div className="space-y-1 text-sm mono">
                  {Object.entries(profitLoss.revenue).map(([acc, amt]) => (
                    <div key={acc} className="flex justify-between">
                      <span>{acc}</span>
                      <span className="text-green-600">₹{amt.toFixed(2)}</span>
                    </div>
                  ))}
                  <div className="border-t border-[#1B2D42] pt-1 flex justify-between font-bold">
                    <span>Total Revenue</span>
                    <span className="text-green-600">₹{profitLoss.total_revenue.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2">Expenses</p>
                <div className="space-y-1 text-sm mono">
                  {Object.entries(profitLoss.expenses).map(([acc, amt]) => (
                    <div key={acc} className="flex justify-between">
                      <span>{acc}</span>
                      <span className="text-red-600">₹{amt.toFixed(2)}</span>
                    </div>
                  ))}
                  <div className="border-t border-[#1B2D42] pt-1 flex justify-between font-bold">
                    <span>Total Expenses</span>
                    <span className="text-red-600">₹{profitLoss.total_expenses.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-6 p-4 bg-[#00C9A7]/5 border border-[#002FA7] rounded-sm">
              <div className="flex justify-between items-center">
                <span className="heading-font text-lg font-bold text-[#E8EDF2]">Net Profit</span>
                <span className="heading-font text-2xl font-bold text-[#00C9A7] mono">
                  ₹{profitLoss.net_profit.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}

        {trialBalance && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="trial-balance-data">
            <h3 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Trial Balance</h3>
            <p className="text-xs text-[#4A5B6E] mono mb-4">As of: {trialBalance.as_of_date}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[#1B2D42]">
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Account</th>
                    <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Debit</th>
                    <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Credit</th>
                  </tr>
                </thead>
                <tbody className="mono">
                  {Object.entries(trialBalance.accounts).map(([acc, bal]) => (
                    <tr key={acc} className="border-b border-[#1B2D42]/40">
                      <td className="py-2 text-[#7A8BA0]">{acc}</td>
                      <td className="py-2 text-right text-[#E8EDF2]">₹{bal.debit.toFixed(2)}</td>
                      <td className="py-2 text-right text-[#E8EDF2]">₹{bal.credit.toFixed(2)}</td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-[#1B2D42] font-bold">
                    <td className="py-2 text-[#E8EDF2]">Total</td>
                    <td className="py-2 text-right text-[#E8EDF2]">₹{trialBalance.total_debit.toFixed(2)}</td>
                    <td className="py-2 text-right text-[#E8EDF2]">₹{trialBalance.total_credit.toFixed(2)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            {trialBalance.difference !== 0 && (
              <p className="mt-4 text-sm text-red-600">Difference: ₹{trialBalance.difference.toFixed(2)}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Reports;