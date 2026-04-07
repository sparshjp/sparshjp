import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Globe, Trash2, Copy, Users, Key, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import AiEntryModal from '../components/AiEntryModal';

export default function PortalPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAiModal, setShowAiModal] = useState(false);

  const load = useCallback(async () => {
    try {
      const c = await fetch(`${API}/portal/clients`).then(r => r.json());
      setClients(Array.isArray(c) ? c : []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createClient = async (data) => {
    const res = await fetch(`${API}/portal/clients`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error('Failed to add portal client');
    load();
  };

  const deleteClient = async (id) => {
    if (!window.confirm('Remove this client from portal?')) return;
    await fetch(`${API}/portal/clients/${id}`, { method: 'DELETE' });
    load();
  };

  const copyToken = (token) => {
    navigator.clipboard.writeText(token);
    toast.success('Portal token copied to clipboard');
  };

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading portal...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="portal-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="portal-title">Client Portal</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Manage external client access to projects, invoices & timesheets</p>
        </div>
        <button onClick={() => setShowAiModal(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-portal-client-btn"><Sparkles size={16} /> Add Client</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Portal Clients', value: clients.length, icon: Users, color: '#38bdf8' },
          { label: 'Active', value: clients.filter(c => c.is_active).length, icon: Globe, color: '#22c55e' },
          { label: 'Tokens Issued', value: clients.filter(c => c.portal_token).length, icon: Key, color: '#a78bfa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Clients */}
      <div className="space-y-3">
        {clients.length === 0 && <p className="text-[#4A5B6E] text-center py-8">No portal clients configured</p>}
        {clients.map(c => (
          <div key={c.id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`portal-client-${c.id}`}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-bold text-[#E8EDF2]">{c.client_name}</p>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${c.is_active ? 'text-[#22c55e] bg-[#22c55e]/15' : 'text-[#4A5B6E] bg-[#152236]'}`}>{c.is_active ? 'Active' : 'Inactive'}</span>
                </div>
                <p className="text-xs text-[#4A5B6E] mt-1">{c.contact_name} | {c.email}</p>
              </div>
              <div className="flex gap-2">
                {c.portal_token && (
                  <button onClick={() => copyToken(c.portal_token)} className="px-2 py-1 border border-[#1B2D42] text-[#7A8BA0] rounded text-xs hover:bg-[#152236] flex items-center gap-1" data-testid={`copy-token-${c.id}`}><Copy size={12} /> Copy Token</button>
                )}
                <button onClick={() => deleteClient(c.id)} className="p-1.5 hover:bg-[#152236] rounded text-[#ef4444]" data-testid={`delete-client-${c.id}`}><Trash2 size={14} /></button>
              </div>
            </div>
            {c.portal_token && (
              <div className="mt-2 p-2 bg-[#152236] rounded">
                <p className="text-[10px] text-[#4A5B6E] uppercase tracking-wider mb-1">Portal Token</p>
                <p className="text-xs text-[#7A8BA0] font-mono break-all">{c.portal_token.slice(0, 30)}...{c.portal_token.slice(-10)}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <AiEntryModal open={showAiModal} onClose={() => setShowAiModal(false)} module="portal_client" title="Add Portal Client" placeholder='e.g. "Add TechCorp to portal, contact: John Smith, john@techcorp.com"' onSubmit={createClient} />
    </div>
  );
}
