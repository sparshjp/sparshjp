import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Upload, Plus, Search } from 'lucide-react';
import { toast } from 'sonner';

function ChartOfAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAccount, setNewAccount] = useState({
    ledger_name: '',
    category: 'Asset',
    opening_balance: 0
  });

  const categories = [
    'Asset', 'Liability', 'Equity', 'Revenue', 'Expense', 
    'Fixed Asset', 'Current Asset', 'Current Liability', 'Other'
  ];

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/coa`);
      setAccounts(res.data);
    } catch (error) {
      console.error('Failed to fetch CoA:', error);
      toast.error('Failed to load Chart of Accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const res = await axios.post(`${API}/coa/upload`, formData);
      toast.success(`Imported ${res.data.imported} accounts`);
      if (res.data.errors.length > 0) {
        toast.warning(`${res.data.errors.length} errors occurred`);
      }
      fetchAccounts();
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Failed to upload Chart of Accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async () => {
    if (!newAccount.ledger_name) {
      toast.error('Ledger name is required');
      return;
    }

    try {
      await axios.post(`${API}/coa`, newAccount);
      toast.success('Account added successfully');
      setShowAddForm(false);
      setNewAccount({ ledger_name: '', category: 'Asset', opening_balance: 0 });
      fetchAccounts();
    } catch (error) {
      console.error('Failed to add account:', error);
      toast.error('Failed to add account');
    }
  };

  const filteredAccounts = accounts.filter(acc => 
    acc.ledger_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    acc.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="coa-title">
              Chart of Accounts
            </h1>
            <p className="text-[#4A5B6E] mt-2">Manage your ledger accounts and categories</p>
          </div>
          <div className="flex space-x-3">
            <label className="bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] text-[#E8EDF2] px-4 py-2 rounded-sm text-sm font-medium cursor-pointer transition-colors flex items-center space-x-2">
              <Upload size={16} />
              <span>Upload CSV</span>
              <input type="file" onChange={handleFileUpload} className="hidden" accept=".csv" />
            </label>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-[#00C9A7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium transition-colors flex items-center space-x-2"
              data-testid="add-account-button"
            >
              <Plus size={16} />
              <span>Add Account</span>
            </button>
          </div>
        </div>

        {showAddForm && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="add-account-form">
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2] mb-4">Add New Account</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Ledger Name</label>
                <input
                  type="text"
                  value={newAccount.ledger_name}
                  onChange={(e) => setNewAccount({...newAccount, ledger_name: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="e.g., Bank Account - HDFC"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Category</label>
                <select
                  value={newAccount.category}
                  onChange={(e) => setNewAccount({...newAccount, category: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7]"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat} className="bg-[#0D1B2A] text-[#E8EDF2]">{cat}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Opening Balance</label>
                <input
                  type="number"
                  value={newAccount.opening_balance}
                  onChange={(e) => setNewAccount({...newAccount, opening_balance: parseFloat(e.target.value)})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7]"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-4">
              <button
                onClick={handleAddAccount}
                className="bg-[#00C9A7] hover:bg-[#002480] text-white px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Save Account
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] text-[#E8EDF2] px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm">
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#4A5B6E]" size={18} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search accounts..."
                className="w-full bg-[#0D1B2A] pl-10 pr-4 py-2 border border-[#1B2D42] rounded-sm text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
              />
            </div>
            <span className="mono text-sm text-[#4A5B6E]">{filteredAccounts.length} accounts</span>
          </div>

          {loading ? (
            <p className="text-center py-8 text-[#4A5B6E]">Loading...</p>
          ) : filteredAccounts.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-[#1B2D42] rounded-sm">
              <p className="text-[#4A5B6E]">No accounts found</p>
              <p className="text-sm text-[#4A5B6E] mt-1">Upload a CSV or add accounts manually</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="coa-table">
                <thead>
                  <tr className="border-b border-[#1B2D42]">
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Ledger Name</th>
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Category</th>
                    <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Opening Balance</th>
                    <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Current Balance</th>
                  </tr>
                </thead>
                <tbody className="mono">
                  {filteredAccounts.map((acc) => (
                    <tr key={acc.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/30">
                      <td className="py-3 text-[#E8EDF2]">{acc.ledger_name}</td>
                      <td className="py-3">
                        <span className="px-2 py-1 bg-[#1B2D42] text-[#7A8BA0] rounded text-xs">{acc.category}</span>
                      </td>
                      <td className="py-3 text-right text-[#7A8BA0]">₹{acc.opening_balance.toFixed(2)}</td>
                      <td className="py-3 text-right text-[#E8EDF2] font-medium">₹{acc.current_balance.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="bg-[#0D1B2A] border border-[#1B2D42] p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-3">CSV Template Format</h3>
          <p className="text-sm text-[#7A8BA0] mb-2">Your CSV should have these columns:</p>
          <code className="block bg-[#152236] p-3 rounded-sm text-xs mono border border-[#1B2D42] text-[#E8EDF2]">
            Ledger Name, Category, Opening Balance
          </code>
          <p className="text-xs text-[#4A5B6E] mt-2">Example: "Bank Account - HDFC, Current Asset, 50000"</p>
        </div>
      </div>
    </div>
  );
}

export default ChartOfAccounts;