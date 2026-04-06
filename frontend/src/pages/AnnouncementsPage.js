import React, { useState, useEffect } from 'react';
import { API } from '../App';
import { Bell, Plus, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

export default function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    priority: 'medium'
  });

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch(`${API}/announcements`);
      const data = await response.json();
      setAnnouncements(data);
    } catch (error) {
      console.error('Error fetching announcements:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/announcements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        setFormData({ title: '', content: '', priority: 'medium' });
        setShowForm(false);
        fetchAnnouncements();
      }
    } catch (error) {
      console.error('Error creating announcement:', error);
    }
  };

  const getPriorityIcon = (priority) => {
    switch(priority) {
      case 'high': return <AlertCircle className="text-red-500" size={20} />;
      case 'medium': return <AlertTriangle className="text-yellow-500" size={20} />;
      case 'low': return <Info className="text-blue-500" size={20} />;
      default: return <Bell size={20} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return 'border-l-4 border-red-500';
      case 'medium': return 'border-l-4 border-yellow-500';
      case 'low': return 'border-l-4 border-blue-500';
      default: return '';
    }
  };

  if (loading) {
    return <div className="p-6 text-[#E8EDF2]">Loading announcements...</div>;
  }

  return (
    <div className="p-6" data-testid="announcements-page">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <Bell className="text-[#00d4aa]" size={32} />
          <h1 className="text-3xl font-bold text-[#E8EDF2]">Announcements</h1>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="bg-[#00d4aa] hover:bg-[#00b894] text-[#0D1B2A]"
          data-testid="toggle-form-button"
        >
          <Plus size={20} className="mr-2" />
          {showForm ? 'Cancel' : 'New Announcement'}
        </Button>
      </div>

      {showForm && (
        <div className="bg-[#152236] p-6 rounded-lg border border-[#1B2D42] mb-6" data-testid="announcement-form">
          <h2 className="text-xl font-semibold text-[#E8EDF2] mb-4">Create New Announcement</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#E8EDF2] mb-2">Title</label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Enter announcement title"
                required
                className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]"
                data-testid="title-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#E8EDF2] mb-2">Content</label>
              <Textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                placeholder="Enter announcement content"
                required
                rows={4}
                className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]"
                data-testid="content-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#E8EDF2] mb-2">Priority</label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData({...formData, priority: value})}
              >
                <SelectTrigger className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]" data-testid="priority-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#152236] border-[#1B2D42]">
                  <SelectItem value="high" className="text-[#E8EDF2]">High Priority</SelectItem>
                  <SelectItem value="medium" className="text-[#E8EDF2]">Medium Priority</SelectItem>
                  <SelectItem value="low" className="text-[#E8EDF2]">Low Priority</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              type="submit"
              className="w-full bg-[#00d4aa] hover:bg-[#00b894] text-[#0D1B2A]"
              data-testid="submit-button"
            >
              Create Announcement
            </Button>
          </form>
        </div>
      )}

      <div className="space-y-4" data-testid="announcements-list">
        {announcements.length === 0 ? (
          <div className="bg-[#152236] p-8 rounded-lg border border-[#1B2D42] text-center">
            <Bell className="mx-auto mb-3 text-[#00d4aa]" size={48} />
            <p className="text-[#E8EDF2] text-lg">No announcements yet</p>
            <p className="text-[#E8EDF2]/60 text-sm mt-2">Create your first announcement to get started</p>
          </div>
        ) : (
          announcements.map((announcement) => (
            <div
              key={announcement.id}
              className={`bg-[#152236] p-6 rounded-lg border border-[#1B2D42] ${getPriorityColor(announcement.priority)}`}
              data-testid={`announcement-${announcement.id}`}
            >
              <div className="flex items-start gap-4">
                <div className="mt-1">{getPriorityIcon(announcement.priority)}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-[#E8EDF2] mb-2">{announcement.title}</h3>
                  <p className="text-[#E8EDF2]/80 mb-3 whitespace-pre-wrap">{announcement.content}</p>
                  <div className="flex items-center gap-4 text-sm text-[#E8EDF2]/60">
                    <span>Priority: <span className="capitalize">{announcement.priority}</span></span>
                    <span>•</span>
                    <span>{new Date(announcement.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}