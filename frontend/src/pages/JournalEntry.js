import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { BookOpen, Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

function JournalEntry() {
  const [entries, setEntries] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [entryType, setEntryType] = useState('Manual Entry');
  const [formData, setFormData] = useState({
    posting_date: new Date().toISOString().split('T')[0],
    cost_center: 'General',
    narration: '',
    journal_entries: [
      { account: '', debit: 0, credit: 0, description: '' },
      { account: '', debit: 0, credit: 0, description: '' }
    ]
  });

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      const res = await axios.get(`${API}/journal-entries/manual`);
      setEntries(res.data);
    } catch (error) {
      toast.error('Failed to fetch journal entries');
    }
  };

  const addRow = () => {
    setFormData({
      ...formData,
      journal_entries: [...formData.journal_entries, { account: '', debit: 0, credit: 0, description: '' }]
    });
  };

  const removeRow = (index) => {
    const newEntries = formData.journal_entries.filter((_, i) => i !== index);
    setFormData({ ...formData, journal_entries: newEntries });
  };

  const updateRow = (index, field, value) => {
    const newEntries = [...formData.journal_entries];
    newEntries[index][field] = field === 'debit' || field === 'credit' ? parseFloat(value) || 0 : value;
    setFormData({ ...formData, journal_entries: newEntries });
  };

  const calculateTotals = () => {
    const totalDebit = formData.journal_entries.reduce((sum, je) => sum + (je.debit || 0), 0);
    const totalCredit = formData.journal_entries.reduce((sum, je) => sum + (je.credit || 0), 0);
    return { totalDebit, totalCredit, difference: totalDebit - totalCredit };
  };

  const handleSubmit = async () => {
    const { totalDebit, totalCredit, difference } = calculateTotals();
    
    if (Math.abs(difference) > 0.01) {
      toast.error(`Entry not balanced! Difference: ₹${difference.toFixed(2)}`);
      return;
    }

    try {
      await axios.post(`${API}/journal-entries/manual`, {
        ...formData,
        entry_type: entryType
      });
      toast.success('Journal entry created!');
      setShowForm(false);
      setFormData({
        posting_date: new Date().toISOString().split('T')[0],
        cost_center: 'General',
        narration: '',
        journal_entries: [
          { account: '', debit: 0, credit: 0, description: '' },
          { account: '', debit: 0, credit: 0, description: '' }
        ]
      });
      fetchEntries();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create entry');
    }
  };

  const postEntry = async (entryId) => {
    try {
      await axios.post(`${API}/journal-entries/manual/${entryId}/post`);
      toast.success('Entry posted to ledger!');
      fetchEntries();
    } catch (error) {
      toast.error('Failed to post entry');
    }
  };

  const totals = showForm ? calculateTotals() : null;

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-font text-4xl font-black tracking-tighter text-slate-900">Journal Entries</h1>
            <p className="text-slate-500 mt-2">Manual entries, corrections, and audit adjustments</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-[#002FA7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium flex items-center space-x-2"
          >
            <Plus size={16} />
            <span>New Entry</span>
          </button>
        </div>

        {showForm && (
          <div className="bg-white border-2 border-[#002FA7] rounded-sm p-6 space-y-4">
            <h2 className="heading-font text-xl font-bold text-slate-900">Create Journal Entry</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Entry Type</label>
                <select value={entryType} onChange={(e) => setEntryType(e.target.value)} className="w-full border border-slate-200 rounded-sm px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#002FA7]">
                  <option>Manual Entry</option>
                  <option>Correction Entry</option>
                  <option>Audit Adjustment</option>
                  <option>Period End Entry</option>
                </select>
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Posting Date</label>
                <input type="date" value={formData.posting_date} onChange={(e) => setFormData({...formData, posting_date: e.target.value})} className="w-full border border-slate-200 rounded-sm px-4 py-2 mono focus:outline-none focus:ring-2 focus:ring-[#002FA7]" />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Cost Center</label>
                <input type="text" value={formData.cost_center} onChange={(e) => setFormData({...formData, cost_center: e.target.value})} className="w-full border border-slate-200 rounded-sm px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#002FA7]" />
              </div>
            </div>

            <div>
              <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Narration</label>
              <textarea value={formData.narration} onChange={(e) => setFormData({...formData, narration: e.target.value})} className="w-full border border-slate-200 rounded-sm px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#002FA7] h-20 resize-none" placeholder="Brief description of this entry..." />
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold text-slate-900">Journal Entries</h3>
                <button onClick={addRow} className="text-sm text-[#002FA7] hover:text-[#002480] font-medium flex items-center space-x-1">
                  <Plus size={14} /><span>Add Row</span>
                </button>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Account</th>
                      <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-slate-500">Debit</th>
                      <th className="pb-2 text-right font-bold text-xs tracking-widest uppercase text-slate-500">Credit</th>
                      <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-slate-500">Description</th>
                      <th className="pb-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {formData.journal_entries.map((je, idx) => (
                      <tr key={idx} className="border-b border-slate-100">
                        <td className="py-2"><input type="text" value={je.account} onChange={(e) => updateRow(idx, 'account', e.target.value)} className="w-full border border-slate-200 rounded-sm px-2 py-1 text-sm" placeholder="Account name" /></td>
                        <td className="py-2"><input type="number" step="0.01" value={je.debit} onChange={(e) => updateRow(idx, 'debit', e.target.value)} className="w-full border border-slate-200 rounded-sm px-2 py-1 text-sm mono text-right" /></td>
                        <td className="py-2"><input type="number" step="0.01" value={je.credit} onChange={(e) => updateRow(idx, 'credit', e.target.value)} className="w-full border border-slate-200 rounded-sm px-2 py-1 text-sm mono text-right" /></td>
                        <td className="py-2"><input type="text" value={je.description} onChange={(e) => updateRow(idx, 'description', e.target.value)} className="w-full border border-slate-200 rounded-sm px-2 py-1 text-sm" placeholder="Description" /></td>
                        <td className="py-2"><button onClick={() => removeRow(idx)} className="p-1 text-red-500 hover:bg-red-50 rounded"><Trash2 size={14} /></button></td>
                      </tr>
                    ))}
                    <tr className="font-bold border-t-2 border-slate-300">
                      <td className="py-2">Total</td>
                      <td className="py-2 text-right mono text-slate-900">₹{totals?.totalDebit.toFixed(2)}</td>
                      <td className="py-2 text-right mono text-slate-900">₹{totals?.totalCredit.toFixed(2)}</td>
                      <td className="py-2" colSpan="2">
                        {Math.abs(totals?.difference || 0) > 0.01 && (
                          <span className="text-xs text-red-600">Difference: ₹{totals?.difference.toFixed(2)}</span>
                        )}
                        {Math.abs(totals?.difference || 0) <= 0.01 && (
                          <span className="text-xs text-green-600">✓ Balanced</span>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex space-x-3">
              <button onClick={handleSubmit} disabled={Math.abs(totals?.difference || 0) > 0.01} className="bg-[#002FA7] hover:bg-[#002480] text-white px-6 py-2 rounded-sm text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                Create Entry
              </button>
              <button onClick={() => setShowForm(false)} className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-900 px-6 py-2 rounded-sm text-sm font-medium">
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="bg-white border border-slate-200 rounded-sm p-6">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-4">Journal Entries History</h2>
          {entries.length === 0 ? (
            <div className="text-center py-12"><BookOpen className="mx-auto mb-3 text-slate-300" size={48} /><p className="text-slate-500">No journal entries</p></div>
          ) : (
            <div className="space-y-4">
              {entries.map((entry) => (
                <div key={entry.id} className="border border-slate-200 p-4 rounded-sm">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span className={`px-3 py-1 rounded text-xs font-medium ${entry.entry_type === 'Manual Entry' ? 'bg-blue-100 text-blue-700' : entry.entry_type === 'Correction Entry' ? 'bg-orange-100 text-orange-700' : 'bg-purple-100 text-purple-700'}`}>
                        {entry.entry_type}
                      </span>
                      <p className="text-sm text-slate-600 mt-2">{entry.narration}</p>
                      <p className="text-xs text-slate-500 mono mt-1">{entry.posting_date} | {entry.cost_center}</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded text-xs font-medium ${entry.status === 'Draft' ? 'bg-gray-100 text-gray-700' : 'bg-green-100 text-green-700'}`}>{entry.status}</span>
                      {entry.status === 'Draft' && (
                        <button onClick={() => postEntry(entry.id)} className="block mt-2 text-xs px-3 py-1 bg-[#002FA7] text-white rounded-sm hover:bg-[#002480]">Post to Ledger</button>
                      )}
                    </div>
                  </div>
                  <div className="text-xs bg-slate-50 p-3 rounded-sm">
                    {entry.journal_entries?.map((je, idx) => (
                      <div key={idx} className="flex justify-between mono py-1">
                        <span className="text-slate-700">{je.account}</span>
                        <div className="space-x-4">
                          {je.debit > 0 && <span className="text-green-600">Dr ₹{je.debit.toFixed(2)}</span>}
                          {je.credit > 0 && <span className="text-red-600">Cr ₹{je.credit.toFixed(2)}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default JournalEntry;
