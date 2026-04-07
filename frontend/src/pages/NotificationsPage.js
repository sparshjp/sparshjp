import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Bell, CheckCheck, Trash2, RefreshCw, Loader2, AlertTriangle, Info, Clock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const TYPE_ICONS = { overdue: AlertTriangle, reminder: Clock, expiring: AlertTriangle, info: Info };
const PRIORITY_COLORS = { high: '#ef4444', medium: '#f59e0b', normal: '#38bdf8', low: '#4A5B6E' };

export default function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('all');

  const load = useCallback(async () => {
    try {
      const [n, uc] = await Promise.all([
        fetch(`${API}/notifications`).then(r => r.json()),
        fetch(`${API}/notifications/unread-count${user ? `?role=${user.role}` : ''}`).then(r => r.json()),
      ]);
      setNotifications(Array.isArray(n) ? n : []);
      setUnreadCount(uc?.unread || 0);
    } catch {}
    setLoading(false);
  }, [user]);

  useEffect(() => { load(); }, [load]);

  const markRead = async (id) => {
    await fetch(`${API}/notifications/${id}/read`, { method: 'PUT' });
    load();
  };

  const markAllRead = async () => {
    await fetch(`${API}/notifications/read-all`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
    load();
  };

  const deleteNotif = async (id) => {
    await fetch(`${API}/notifications/${id}`, { method: 'DELETE' });
    load();
  };

  const generateReminders = async () => {
    setGenerating(true);
    try {
      await fetch(`${API}/notifications/generate-reminders`, { method: 'POST' });
      load();
    } catch {}
    setGenerating(false);
  };

  const filtered = filter === 'all' ? notifications : filter === 'unread' ? notifications.filter(n => !n.read) : notifications.filter(n => n.type === filter);

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading notifications...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="notifications-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2] flex items-center gap-2" data-testid="notifications-title">
            <Bell size={24} className="text-[#00C9A7]" /> Notifications
            {unreadCount > 0 && <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#ef4444]/20 text-[#ef4444]">{unreadCount}</span>}
          </h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Invoice reminders, approval requests & alerts</p>
        </div>
        <div className="flex gap-2">
          <button onClick={generateReminders} disabled={generating} className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] flex items-center gap-1 disabled:opacity-50" data-testid="generate-reminders-btn">
            {generating ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />} Generate Reminders
          </button>
          {unreadCount > 0 && <button onClick={markAllRead} className="px-3 py-2 border border-[#1B2D42] text-[#7A8BA0] rounded-lg text-sm hover:bg-[#152236] flex items-center gap-1" data-testid="mark-all-read-btn"><CheckCheck size={14} /> Mark All Read</button>}
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit flex-wrap">
        {['all', 'unread', 'overdue', 'reminder', 'expiring'].map(t => (
          <button key={t} onClick={() => setFilter(t)} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors capitalize ${filter === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`filter-${t}`}>{t} {t === 'unread' && unreadCount > 0 ? `(${unreadCount})` : ''}</button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="space-y-2">
        {filtered.length === 0 && <p className="text-[#4A5B6E] text-center py-8">No notifications</p>}
        {filtered.map(n => {
          const Icon = TYPE_ICONS[n.type] || Info;
          return (
            <div key={n.id} className={`bg-[#0A1628] border rounded-lg p-4 flex items-start gap-3 transition-colors ${n.read ? 'border-[#1B2D42] opacity-70' : 'border-[#1B2D42] bg-[#0D1B2A]'}`} data-testid={`notif-${n.id}`}>
              <div className="p-1.5 rounded-lg mt-0.5" style={{ background: (PRIORITY_COLORS[n.priority] || '#38bdf8') + '15' }}>
                <Icon size={16} style={{ color: PRIORITY_COLORS[n.priority] || '#38bdf8' }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-[#E8EDF2]">{n.title}</p>
                  {!n.read && <span className="w-2 h-2 rounded-full bg-[#00C9A7]" />}
                  <span className="px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wider bg-[#152236] text-[#4A5B6E]">{n.type}</span>
                </div>
                <p className="text-xs text-[#7A8BA0] mt-0.5">{n.message}</p>
                <p className="text-xs text-[#4A5B6E] mt-1">{n.created_at?.slice(0, 16).replace('T', ' ')}</p>
              </div>
              <div className="flex gap-1">
                {!n.read && <button onClick={() => markRead(n.id)} className="p-1.5 hover:bg-[#152236] rounded text-[#00C9A7]" title="Mark read" data-testid={`read-${n.id}`}><CheckCheck size={14} /></button>}
                <button onClick={() => deleteNotif(n.id)} className="p-1.5 hover:bg-[#152236] rounded text-[#ef4444]" title="Delete" data-testid={`delete-notif-${n.id}`}><Trash2 size={14} /></button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
