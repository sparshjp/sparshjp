import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Globe, Plus, Trash2, Copy, Loader2, Users, Key } from 'lucide-react';
import { toast } from 'sonner';

export default function PortalPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ client_name: '', contact_name: '', email: '', projects: [] });

  const load = useCallback(async () => {
    try {
      const c = await fetch(`${API}/portal/clients`).then(r => r.json());
      setClients(Array.isArray(c) ? c : []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const createClient = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await fetch(`${API}/portal/clients`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      setShowForm(false);
      setForm({ client_name: '', contact_name: '', email: '', projects: [] });
      load();
    } catch {}
    setSubmitting(false);
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
        <button onClick={() => setShowForm(true)} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1" data-testid="new-portal-client-btn"><Plus size={16} /> Add Client</button>
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

      {/* Create Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowForm(false)}>
          <form onClick={e => e.stopPropagation()} onSubmit={createClient} className="bg-[#0D1B2A] border border-[#1B2D42] rounded-xl p-6 w-full max-w-lg space-y-4">
            <h2 className="text-lg font-bold text-[#E8EDF2]">Add Portal Client</h2>
            <input placeholder="Client / Company Name" value={form.client_name} onChange={e => setForm(p => ({ ...p, client_name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" required data-testid="portal-client-name" />
            <input placeholder="Contact Person" value={form.contact_name} onChange={e => setForm(p => ({ ...p, contact_name: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="portal-contact-name" />
            <input type="email" placeholder="Email" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} className="w-full px-3 py-2 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="portal-email" />
            <p className="text-xs text-[#4A5B6E]">A JWT portal token will be auto-generated upon creation. Share this token with the client to access their portal.</p>
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-bold hover:bg-[#00b396] disabled:opacity-50 flex items-center gap-1" data-testid="create-portal-client-btn">{submitting && <Loader2 size={14} className="animate-spin" />} Create</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
