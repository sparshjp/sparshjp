import React, { useState, useEffect, useCallback } from 'react';
import { BookOpen, FileText } from 'lucide-react';
import { toast } from 'sonner';
import { ModuleAIPrompt } from '../components/AISmartEntry';
import { API } from '../App';

function JournalEntry() {
  const [entries, setEntries] = useState([]);

  const fetchEntries = useCallback(async () => {
    try {
      const res = await fetch(`${API}/journal-entries/manual`);
      if (res.ok) setEntries(await res.json());
    } catch (error) {
      toast.error('Failed to fetch journal entries');
    }
  }, []);

  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  const postEntry = async (entryId) => {
    try {
      await fetch(`${API}/journal-entries/manual/${entryId}/post`, { method: 'POST' });
      toast.success('Entry posted to ledger!');
      fetchEntries();
    } catch (error) {
      toast.error('Failed to post entry');
    }
  };

  return (
    <div className="space-y-6" data-testid="journal-entry-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]">Journal Entries</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Manual entries, corrections, and audit adjustments</p>
        </div>
      </div>

      {/* AI Prompt — replaces old form */}
      <ModuleAIPrompt
        placeholder={`Describe your entry... e.g. "Debit Salary Expense 200000, Credit Salary Payable 200000"`}
        defaultIntent="journal_entry"
        onCreated={fetchEntries}
      />

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
