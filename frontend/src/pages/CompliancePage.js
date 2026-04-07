import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { Shield, CheckCircle2, AlertTriangle, XCircle, Users, Activity, Lock } from 'lucide-react';

const STATUS_COLORS = { compliant: '#22c55e', partial: '#f59e0b', non_compliant: '#ef4444' };

export default function CompliancePage() {
  const [frameworks, setFrameworks] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [accessLogs, setAccessLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('overview');
  const [expandedFw, setExpandedFw] = useState(null);

  const load = useCallback(async () => {
    try {
      const [fw, db, logs] = await Promise.all([
        fetch(`${API}/compliance/frameworks`).then(r => r.json()),
        fetch(`${API}/compliance/dashboard`).then(r => r.json()),
        fetch(`${API}/compliance/access-logs?limit=50`).then(r => r.json()),
      ]);
      setFrameworks(fw || {});
      setDashboard(db || {});
      setAccessLogs(Array.isArray(logs) ? logs : []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const updateControl = async (fw, controlId, status) => {
    await fetch(`${API}/compliance/controls/${fw}/${controlId}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, reviewed_by: 'admin' }),
    });
    load();
  };

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading compliance data...</div>;

  const fwEntries = Object.entries(dashboard.frameworks || {});

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="compliance-page">
      <div>
        <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="compliance-title">Audit & Compliance</h1>
        <p className="text-[#4A5B6E] text-sm mt-1">SOC 2 / ISO 27001 readiness, access logs</p>
      </div>

      {/* Readiness Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {fwEntries.map(([id, fw]) => (
          <div key={id} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4" data-testid={`fw-card-${id}`}>
            <p className="text-xs text-[#4A5B6E] uppercase tracking-wider">{fw.name}</p>
            <p className="text-3xl font-bold mt-1" style={{ color: fw.readiness_pct >= 70 ? '#22c55e' : fw.readiness_pct >= 40 ? '#f59e0b' : '#ef4444' }}>{fw.readiness_pct}%</p>
            <p className="text-xs text-[#7A8BA0] mt-1">{fw.compliant}/{fw.total} controls</p>
          </div>
        ))}
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
          <div className="flex items-center gap-2"><Users size={16} className="text-[#38bdf8]" /><p className="text-xs text-[#4A5B6E]">Active Users</p></div>
          <p className="text-3xl font-bold text-[#E8EDF2] mt-1">{dashboard.user_stats?.active || 0}<span className="text-sm text-[#4A5B6E]">/{dashboard.user_stats?.total || 0}</span></p>
        </div>
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
          <div className="flex items-center gap-2"><Activity size={16} className="text-[#a78bfa]" /><p className="text-xs text-[#4A5B6E]">Access Logs (7d)</p></div>
          <p className="text-3xl font-bold text-[#E8EDF2] mt-1">{dashboard.activity?.access_logs_7d || 0}</p>
        </div>
      </div>

      {/* System Status */}
      <div className="flex gap-4 flex-wrap">
        {[
          { label: 'RBAC Enabled', active: dashboard.rbac_enabled, icon: Lock },
          { label: 'Audit Trail', active: dashboard.audit_trail_enabled, icon: Shield },
          { label: 'Encryption at Rest', active: dashboard.encryption_at_rest, icon: Lock },
        ].map(s => (
          <div key={s.label} className="flex items-center gap-2 px-3 py-2 bg-[#0A1628] border border-[#1B2D42] rounded-lg">
            <s.icon size={14} className={s.active ? 'text-[#22c55e]' : 'text-[#ef4444]'} />
            <span className="text-xs text-[#7A8BA0]">{s.label}</span>
            <span className={`text-xs font-bold ${s.active ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>{s.active ? 'ON' : 'OFF'}</span>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0A1628] border border-[#1B2D42] rounded-lg p-1 w-fit">
        {['overview', 'access-logs'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${tab === t ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#7A8BA0]'}`} data-testid={`tab-${t}`}>{t.replace('-', ' ')}</button>
        ))}
      </div>

      {tab === 'overview' && (
        <div className="space-y-4">
          {Object.entries(frameworks).map(([fwId, fw]) => (
            <div key={fwId} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg" data-testid={`framework-${fwId}`}>
              <div className="p-4 cursor-pointer flex items-center justify-between" onClick={() => setExpandedFw(expandedFw === fwId ? null : fwId)}>
                <div>
                  <p className="text-sm font-bold text-[#E8EDF2]">{fw.name}</p>
                  <p className="text-xs text-[#4A5B6E]">{fw.compliant} compliant | {fw.partial} partial | {fw.non_compliant} non-compliant</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-[#152236] rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-[#22c55e]" style={{ width: `${fw.readiness_pct}%` }} />
                  </div>
                  <span className="text-sm font-bold" style={{ color: fw.readiness_pct >= 70 ? '#22c55e' : '#f59e0b' }}>{fw.readiness_pct}%</span>
                </div>
              </div>
              {expandedFw === fwId && (
                <div className="px-4 pb-4 border-t border-[#1B2D42] pt-3">
                  <div className="space-y-2">
                    {fw.controls?.map(c => (
                      <div key={c.id} className="flex items-center justify-between bg-[#152236] rounded p-3" data-testid={`control-${c.id}`}>
                        <div className="flex items-center gap-2">
                          {c.status === 'compliant' ? <CheckCircle2 size={14} className="text-[#22c55e]" /> : c.status === 'partial' ? <AlertTriangle size={14} className="text-[#f59e0b]" /> : <XCircle size={14} className="text-[#ef4444]" />}
                          <div>
                            <p className="text-xs font-bold text-[#E8EDF2]">{c.id} — {c.title}</p>
                            <p className="text-[10px] text-[#4A5B6E]">{c.category}</p>
                          </div>
                        </div>
                        <select value={c.status} onChange={e => updateControl(fwId, c.id, e.target.value)} className="px-2 py-1 bg-[#0A1628] border border-[#1B2D42] rounded text-xs text-[#E8EDF2] outline-none" data-testid={`status-${c.id}`}>
                          <option value="compliant">Compliant</option>
                          <option value="partial">Partial</option>
                          <option value="non_compliant">Non-Compliant</option>
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === 'access-logs' && (
        <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
          {accessLogs.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No access logs recorded</p> : (
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
                <th className="text-left p-3">User</th><th className="text-left p-3">Action</th><th className="text-left p-3">Resource</th><th className="text-left p-3">IP</th><th className="text-left p-3">Time</th>
              </tr></thead>
              <tbody>
                {accessLogs.map(l => (
                  <tr key={l.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50">
                    <td className="p-3 text-[#E8EDF2]">{l.user_name || l.user_id}</td>
                    <td className="p-3 text-[#7A8BA0]">{l.action}</td>
                    <td className="p-3 text-[#7A8BA0]">{l.resource}</td>
                    <td className="p-3 text-[#4A5B6E]">{l.ip_address || '-'}</td>
                    <td className="p-3 text-[#4A5B6E]">{l.timestamp?.slice(0, 16).replace('T', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
