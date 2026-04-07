import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { useAuth } from '../contexts/AuthContext';
import { Users, Plus, Pencil, Trash2, Shield, X, Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const BASE_ROLE_OPTIONS = [
  { value: 'admin', label: 'Admin', color: '#f59e0b' },
  { value: 'finance_manager', label: 'Finance Manager', color: '#3b82f6' },
  { value: 'project_manager', label: 'Project Manager', color: '#8b5cf6' },
  { value: 'hr_manager', label: 'HR Manager', color: '#ec4899' },
  { value: 'ap_clerk', label: 'AP Clerk', color: '#14b8a6' },
  { value: 'ar_clerk', label: 'AR Clerk', color: '#06b6d4' },
  { value: 'tax_compliance', label: 'Tax & Compliance', color: '#f97316' },
  { value: 'viewer', label: 'Viewer', color: '#6b7280' },
];

const ROLE_COLORS = { creator: '#00d4aa', admin: '#f59e0b', finance_manager: '#3b82f6', project_manager: '#8b5cf6', hr_manager: '#ec4899', ap_clerk: '#14b8a6', ar_clerk: '#06b6d4', tax_compliance: '#f97316', viewer: '#6b7280' };

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'viewer' });
  const [saving, setSaving] = useState(false);
  const token = localStorage.getItem('kairos_token');
  const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };

  const fetchUsers = useCallback(async () => {
    try {
      const res = await fetch(`${API}/auth/users`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setUsers(await res.json());
    } catch {}
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editUser) {
        const body = { name: form.name, role: form.role };
        if (form.password) body.password = form.password;
        const res = await fetch(`${API}/auth/users/${editUser.id}`, { method: 'PUT', headers, body: JSON.stringify(body) });
        if (!res.ok) throw new Error((await res.json()).detail);
        toast.success('User updated');
      } else {
        const res = await fetch(`${API}/auth/users`, { method: 'POST', headers, body: JSON.stringify(form) });
        if (!res.ok) throw new Error((await res.json()).detail);
        toast.success('User created');
      }
      setShowForm(false);
      setEditUser(null);
      setForm({ name: '', email: '', password: '', role: 'viewer' });
      fetchUsers();
    } catch (e) { toast.error(e.message); }
    setSaving(false);
  };

  const handleDelete = async (uid) => {
    if (!window.confirm('Delete this user?')) return;
    const res = await fetch(`${API}/auth/users/${uid}`, { method: 'DELETE', headers });
    if (res.ok) { toast.success('User deleted'); fetchUsers(); } else toast.error('Delete failed');
  };

  const openEdit = (u) => {
    setEditUser(u);
    setForm({ name: u.name, email: u.email, password: '', role: u.role });
    setShowForm(true);
  };

  // Build role options - add creator only if current user is creator
  const ROLE_OPTIONS = currentUser?.role === 'creator' 
    ? [{ value: 'creator', label: 'Creator', color: '#00d4aa' }, ...BASE_ROLE_OPTIONS]
    : BASE_ROLE_OPTIONS;

  return (
    <div className="max-w-5xl mx-auto space-y-6" data-testid="user-management">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2] flex items-center gap-2"><Users size={22} /> User Management</h1>
          <p className="text-sm text-[#4A5B6E] mt-1">Manage team members and their access roles</p>
        </div>
        <button onClick={() => { setEditUser(null); setForm({ name: '', email: '', password: '', role: 'viewer' }); setShowForm(true); }}
          className="px-4 py-2 rounded-lg bg-[#00d4aa] text-[#0D1B2A] font-bold text-sm hover:bg-[#00b894] transition-colors flex items-center gap-2"
          data-testid="add-user-btn">
          <Plus size={16} /> Add User
        </button>
      </div>

      {showForm && (
        <div className="bg-[#152236] border border-[#1B2D42] rounded-lg p-6" data-testid="user-form">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-[#E8EDF2]">{editUser ? 'Edit User' : 'Create User'}</h2>
            <button onClick={() => setShowForm(false)} className="text-[#4A5B6E] hover:text-[#E8EDF2]"><X size={18} /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#7A8BA0] mb-1">Full Name</label>
              <input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="John Doe"
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00d4aa]/50 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-[#7A8BA0] mb-1">Email</label>
              <input value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} placeholder="john@nexora.com"
                disabled={!!editUser}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00d4aa]/50 focus:outline-none disabled:opacity-50" />
            </div>
            <div>
              <label className="block text-xs font-bold text-[#7A8BA0] mb-1">{editUser ? 'New Password (leave blank to keep)' : 'Password'}</label>
              <input type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} placeholder="Min 6 characters"
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00d4aa]/50 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-[#7A8BA0] mb-1">Role</label>
              <select value={form.role} onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
                className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded px-3 py-2 text-sm text-[#E8EDF2] focus:border-[#00d4aa]/50 focus:outline-none">
                {ROLE_OPTIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-3 mt-4 justify-end">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded text-sm text-[#7A8BA0] hover:text-[#E8EDF2] transition-colors">Cancel</button>
            <button onClick={handleSave} disabled={saving || (!form.email && !editUser)}
              className="px-4 py-2 rounded-lg bg-[#00d4aa] text-[#0D1B2A] font-bold text-sm hover:bg-[#00b894] transition-colors disabled:opacity-50 flex items-center gap-2"
              data-testid="save-user-btn">
              {saving ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />} {editUser ? 'Update' : 'Create'}
            </button>
          </div>
        </div>
      )}

      <div className="bg-[#152236] border border-[#1B2D42] rounded-lg overflow-hidden">
        <table className="w-full" data-testid="users-table">
          <thead><tr className="bg-[#0A1628] border-b border-[#1B2D42]">
            {['Name', 'Email', 'Role', 'Status', 'Created', 'Actions'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-bold text-[#4A5B6E] uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-[#4A5B6E]"><Loader2 className="animate-spin inline mr-2" size={16} />Loading...</td></tr>
            ) : users.map(u => (
              <tr key={u.id} className="border-b border-[#1B2D42]/50 hover:bg-[#0A1628]/50" data-testid={`user-row-${u.id}`}>
                <td className="px-4 py-3 text-sm text-[#E8EDF2] font-medium">{u.name}</td>
                <td className="px-4 py-3 text-sm text-[#7A8BA0] font-mono">{u.email}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold border"
                    style={{ color: ROLE_COLORS[u.role] || '#6b7280', borderColor: (ROLE_COLORS[u.role] || '#6b7280') + '40', background: (ROLE_COLORS[u.role] || '#6b7280') + '15' }}>
                    <Shield size={10} className="inline mr-1" />{u.role?.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3"><span className={`text-xs ${u.is_active ? 'text-[#00d4aa]' : 'text-[#ef4444]'}`}>{u.is_active ? 'Active' : 'Disabled'}</span></td>
                <td className="px-4 py-3 text-xs text-[#4A5B6E]">{u.created_at?.split('T')[0]}</td>
                <td className="px-4 py-3">
                  {u.role !== 'creator' || currentUser?.role === 'creator' ? (
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(u)} className="text-[#4A5B6E] hover:text-[#3b82f6] transition-colors" data-testid={`edit-user-${u.id}`}><Pencil size={14} /></button>
                      {u.role !== 'creator' && <button onClick={() => handleDelete(u.id)} className="text-[#4A5B6E] hover:text-[#ef4444] transition-colors" data-testid={`delete-user-${u.id}`}><Trash2 size={14} /></button>}
                    </div>
                  ) : <span className="text-[10px] text-[#4A5B6E]">Protected</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
