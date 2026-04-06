import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Send, FileText } from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

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

  useEffect(() => { fetchEntries(); }, []);

  const fetchEntries = async () => {
    try {
      const res = await fetch(`${API}/api/journal-entries/manual`);
      setEntries(await res.json());
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
    const { difference } = calculateTotals();
    if (Math.abs(difference) > 0.01) {
      toast.error(`Entry not balanced! Difference: ${difference.toFixed(2)}`);
      return;
    }
    try {
      await fetch(`${API}/api/journal-entries/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, entry_type: entryType })
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
      toast.error('Failed to create entry');
    }
  };

  const postEntry = async (entryId) => {
    try {
      await fetch(`${API}/api/journal-entries/manual/${entryId}/post`, { method: 'POST' });
      toast.success('Entry posted to ledger!');
      fetchEntries();
    } catch (error) {
      toast.error('Failed to post entry');
    }
  };

  const totals = showForm ? calculateTotals() : null;

  return (
    <div className="space-y-6" data-testid="journal-entry-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Journal Entries</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Manual entries, corrections, and audit adjustments</p>
        </div>
        <button
          data-testid="je-new-btn"
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] rounded-lg text-sm font-semibold transition-colors"
        >
          <Plus size={16} />
          New Entry
        </button>
      </div>

      {showForm && (
        <div className="bg-[#152236] border border-[#00C9A7]/30 rounded-lg p-6 space-y-4" data-testid="je-form">
          <h2 className="text-base font-bold text-[#E8EDF2]">Create Journal Entry</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Entry Type</label>
              <select data-testid="je-type" value={entryType} onChange={(e) => setEntryType(e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7]">
                <option>Manual Entry</option>
                <option>Correction Entry</option>
                <option>Audit Adjustment</option>
                <option>Opening Balance</option>
                <option>Period End Entry</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Posting Date</label>
              <input data-testid="je-date" type="date" value={formData.posting_date} onChange={(e) => setFormData({...formData, posting_date: e.target.value})} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] font-mono focus:border-[#00C9A7]" />
            </div>
            <div>
              <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Cost Center</label>
              <input data-testid="je-cost-center" type="text" value={formData.cost_center} onChange={(e) => setFormData({...formData, cost_center: e.target.value})} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00C9A7]" />
            </div>
          </div>

          <div>
            <label className="text-[10px] tracking-[2px] uppercase font-semibold text-[#4A5B6E] mb-2 block">Narration</label>
            <textarea data-testid="je-narration" value={formData.narration} onChange={(e) => setFormData({...formData, narration: e.target.value})} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-3 py-2 text-sm text-[#E8EDF2] h-20 resize-none focus:border-[#00C9A7]" placeholder="Brief description of this entry..." />
          </div>

          <div className="border-t border-[#1B2D42] pt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-[#E8EDF2] text-sm">Line Items</h3>
              <button onClick={addRow} className="text-xs text-[#00C9A7] hover:text-[#00B396] font-medium flex items-center gap-1">
                <Plus size={14} /><span>Add Row</span>
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="je-line-items-table">
                <thead>
                  <tr className="border-b border-[#1B2D42]">
                    <th className="pb-2 text-left text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Account</th>
                    <th className="pb-2 text-right text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Debit</th>
                    <th className="pb-2 text-right text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Credit</th>
                    <th className="pb-2 text-left text-[10px] tracking-wider uppercase font-semibold text-[#4A5B6E]">Description</th>
                    <th className="pb-2 w-8"></th>
                  </tr>
                </thead>
                <tbody>
                  {formData.journal_entries.map((je, idx) => (
                    <tr key={idx} className="border-b border-[#1B2D42]/30">
                      <td className="py-2 pr-2"><input type="text" value={je.account} onChange={(e) => updateRow(idx, 'account', e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="Account name" /></td>
                      <td className="py-2 pr-2"><input type="number" step="0.01" value={je.debit || ''} onChange={(e) => updateRow(idx, 'debit', e.target.value)} className="w-28 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm font-mono text-right text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="0" /></td>
                      <td className="py-2 pr-2"><input type="number" step="0.01" value={je.credit || ''} onChange={(e) => updateRow(idx, 'credit', e.target.value)} className="w-28 bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm font-mono text-right text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="0" /></td>
                      <td className="py-2 pr-2"><input type="text" value={je.description} onChange={(e) => updateRow(idx, 'description', e.target.value)} className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-2 py-1.5 text-sm text-[#E8EDF2] focus:border-[#00C9A7]" placeholder="Description" /></td>
                      <td className="py-2"><button onClick={() => removeRow(idx)} className="p-1 text-[#FF4D6A] hover:bg-[#FF4D6A]/10 rounded"><Trash2 size={14} /></button></td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-[#00C9A7]/30">
                    <td className="py-3 font-semibold text-[#E8EDF2]">Total</td>
                    <td className="py-3 text-right font-mono font-bold text-[#E8EDF2]">{totals?.totalDebit.toFixed(2)}</td>
                    <td className="py-3 text-right font-mono font-bold text-[#E8EDF2]">{totals?.totalCredit.toFixed(2)}</td>
                    <td className="py-3" colSpan="2">
                      {Math.abs(totals?.difference || 0) > 0.01 ? (
                        <span className="text-xs text-[#FF4D6A] font-medium">Not balanced: {totals?.difference.toFixed(2)}</span>
                      ) : (
                        <span className="text-xs text-[#00C9A7] font-medium">Balanced</span>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button data-testid="je-submit" onClick={handleSubmit} disabled={Math.abs(totals?.difference || 0) > 0.01}
              className="flex items-center gap-2 bg-[#00C9A7] hover:bg-[#00B396] text-[#0D1B2A] px-5 py-2 rounded-lg text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              <Send size={14} /> Create Entry
            </button>
            <button onClick={() => setShowForm(false)} className="bg-[#1B2D42] hover:bg-[#152236] text-[#7A8BA0] px-5 py-2 rounded-lg text-sm font-medium transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* History */}
      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6" data-testid="je-history">
        <h2 className="text-base font-bold text-[#E8EDF2] mb-4">History</h2>
        {entries.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="mx-auto mb-3 text-[#1B2D42]" size={48} />
            <p className="text-[#4A5B6E]">No journal entries yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {entries.map((entry) => (
              <div key={entry.id} className="bg-[#0D1B2A] border border-[#1B2D42] p-4 rounded-lg" data-testid={`je-entry-${entry.id}`}>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-medium tracking-wider uppercase ${
                      entry.entry_type === 'Manual Entry' ? 'bg-[#00C9A7]/15 text-[#00C9A7]' :
                      entry.entry_type === 'Correction Entry' ? 'bg-[#FFB547]/15 text-[#FFB547]' :
                      entry.entry_type === 'Auto Generated' ? 'bg-[#00C9A7]/10 text-[#00C9A7]/70' :
                      'bg-[#7A8BA0]/15 text-[#7A8BA0]'
                    }`}>
                      {entry.entry_type}
                    </span>
                    <p className="text-sm text-[#7A8BA0] mt-2">{entry.narration}</p>
                    <p className="text-xs text-[#4A5B6E] font-mono mt-1">{entry.posting_date} | {entry.cost_center}</p>
                  </div>
                  <div className="text-right flex flex-col items-end gap-2">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-medium ${
                      entry.status === 'Draft' ? 'bg-[#1B2D42] text-[#7A8BA0]' : 'bg-[#00C9A7]/15 text-[#00C9A7]'
                    }`}>{entry.status}</span>
                    {entry.status === 'Draft' && (
                      <button onClick={() => postEntry(entry.id)} data-testid={`je-post-${entry.id}`}
                        className="text-[10px] px-3 py-1 bg-[#00C9A7] text-[#0D1B2A] rounded font-semibold hover:bg-[#00B396] transition-colors">
                        Post to Ledger
                      </button>
                    )}
                  </div>
                </div>
                <div className="bg-[#152236] p-3 rounded-lg text-xs">
                  {entry.journal_entries?.map((je, idx) => (
                    <div key={idx} className="flex justify-between font-mono py-1 border-b border-[#1B2D42]/30 last:border-0">
                      <span className="text-[#7A8BA0]">{je.account}</span>
                      <div className="flex gap-4">
                        {je.debit > 0 && <span className="text-[#00C9A7]">Dr {je.debit.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>}
                        {je.credit > 0 && <span className="text-[#FF4D6A]">Cr {je.credit.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>}
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
  );
}

export default JournalEntry;
