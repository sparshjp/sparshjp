import { useState, useEffect, useCallback } from 'react';
import { API } from '../App';
import { FileUp, FolderOpen, Trash2, Download, Loader2, File, Image, FileText } from 'lucide-react';

const ICON_MAP = { 'application/pdf': FileText, 'image/': Image };
const getIcon = (ct) => { for (const [k, v] of Object.entries(ICON_MAP)) { if (ct?.startsWith(k)) return v; } return File; };

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [filter, setFilter] = useState({ entity_type: '' });

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (filter.entity_type) params.append('entity_type', filter.entity_type);
      const [d, c, s] = await Promise.all([
        fetch(`${API}/documents?${params}`).then(r => r.json()),
        fetch(`${API}/documents/categories`).then(r => r.json()),
        fetch(`${API}/documents/stats`).then(r => r.json()),
      ]);
      setDocuments(Array.isArray(d) ? d : []);
      setCategories(Array.isArray(c) ? c : []);
      setStats(s || {});
    } catch {}
    setLoading(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const uploadFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('entity_type', 'general');
      formData.append('category', 'general');
      await fetch(`${API}/documents/upload`, { method: 'POST', body: formData });
      load();
    } catch {}
    setUploading(false);
    e.target.value = '';
  };

  const deleteDoc = async (id) => {
    if (!window.confirm('Delete this document?')) return;
    await fetch(`${API}/documents/${id}`, { method: 'DELETE' });
    load();
  };

  const totalDocs = Object.values(stats).reduce((s, v) => s + (v.count || 0), 0);
  const totalSize = Object.values(stats).reduce((s, v) => s + (v.total_size_mb || 0), 0);

  if (loading) return <div className="p-8 text-center text-[#4A5B6E]">Loading documents...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6" data-testid="documents-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#E8EDF2]" data-testid="documents-title">Document Management</h1>
          <p className="text-[#4A5B6E] text-sm mt-1">Upload & attach files to transactions, contracts, projects</p>
        </div>
        <label className="px-3 py-2 bg-[#00C9A7] text-[#0A1628] rounded-lg text-sm font-semibold hover:bg-[#00b396] cursor-pointer flex items-center gap-1" data-testid="upload-btn">
          {uploading ? <Loader2 size={16} className="animate-spin" /> : <FileUp size={16} />} Upload
          <input type="file" className="hidden" onChange={uploadFile} disabled={uploading} />
        </label>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Documents', value: totalDocs, icon: FolderOpen, color: '#38bdf8' },
          { label: 'Total Size', value: `${totalSize.toFixed(1)} MB`, icon: FileUp, color: '#a78bfa' },
          { label: 'Categories', value: Object.keys(stats).length, icon: File, color: '#00d4aa' },
        ].map(c => (
          <div key={c.label} className="bg-[#0A1628] border border-[#1B2D42] rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ background: c.color + '15' }}><c.icon size={18} style={{ color: c.color }} /></div>
              <div><p className="text-xs text-[#4A5B6E]">{c.label}</p><p className="text-xl font-bold text-[#E8EDF2]">{c.value}</p></div>
            </div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2 items-center">
        <span className="text-xs text-[#4A5B6E]">Filter:</span>
        <select value={filter.entity_type} onChange={e => setFilter({ entity_type: e.target.value })} className="px-3 py-1.5 bg-[#152236] border border-[#1B2D42] rounded-lg text-sm text-[#E8EDF2] outline-none" data-testid="doc-filter">
          <option value="">All Types</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {/* Documents Grid */}
      <div className="bg-[#0A1628] border border-[#1B2D42] rounded-lg overflow-hidden">
        {documents.length === 0 ? <p className="text-[#4A5B6E] text-center py-8">No documents uploaded</p> : (
          <table className="w-full text-sm">
            <thead><tr className="text-xs text-[#4A5B6E] border-b border-[#1B2D42]">
              <th className="text-left p-3">File</th><th className="text-left p-3">Type</th><th className="text-left p-3">Entity</th><th className="text-right p-3">Size</th><th className="text-left p-3">Uploaded</th><th className="text-center p-3">Actions</th>
            </tr></thead>
            <tbody>
              {documents.map(d => {
                const Icon = getIcon(d.content_type);
                return (
                  <tr key={d.id} className="border-b border-[#1B2D42]/50 hover:bg-[#152236]/50" data-testid={`doc-${d.id}`}>
                    <td className="p-3"><div className="flex items-center gap-2"><Icon size={16} className="text-[#7A8BA0]" /><span className="text-[#E8EDF2] truncate max-w-[200px]">{d.filename}</span></div></td>
                    <td className="p-3 text-[#7A8BA0] capitalize">{d.category || d.entity_type}</td>
                    <td className="p-3 text-[#7A8BA0]">{d.entity_name || '-'}</td>
                    <td className="p-3 text-right text-[#7A8BA0]">{d.size_display}</td>
                    <td className="p-3 text-[#4A5B6E]">{d.uploaded_at?.slice(0, 10)}</td>
                    <td className="p-3 text-center">
                      <div className="flex gap-2 justify-center">
                        <a href={`${API}/documents/download/${d.id}`} className="p-1 hover:bg-[#152236] rounded text-[#00C9A7]" data-testid={`download-${d.id}`}><Download size={14} /></a>
                        <button onClick={() => deleteDoc(d.id)} className="p-1 hover:bg-[#152236] rounded text-[#ef4444]" data-testid={`delete-doc-${d.id}`}><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
