import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Plus, Search } from 'lucide-react';
import { toast } from 'sonner';

function CostCenters() {
  const [costCenters, setCostCenters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCenter, setNewCenter] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    fetchCostCenters();
  }, []);

  const fetchCostCenters = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/cost-centers`);
      setCostCenters(res.data);
    } catch (error) {
      console.error('Failed to fetch cost centers:', error);
      toast.error('Failed to load cost centers');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCenter = async () => {
    if (!newCenter.name) {
      toast.error('Cost center name is required');
      return;
    }

    try {
      await axios.post(`${API}/cost-centers`, newCenter);
      toast.success('Cost center added successfully');
      setShowAddForm(false);
      setNewCenter({ name: '', description: '' });
      fetchCostCenters();
    } catch (error) {
      console.error('Failed to add cost center:', error);
      toast.error('Failed to add cost center');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="cost-centers-title">
              Cost Centers
            </h1>
            <p className="text-[#4A5B6E] mt-2">Define departments, projects, and business units for expense tracking</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-[#00C9A7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium transition-colors flex items-center space-x-2"
            data-testid="add-cost-center-button"
          >
            <Plus size={16} />
            <span>Add Cost Center</span>
          </button>
        </div>

        {showAddForm && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="add-cost-center-form">
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2] mb-4">Add New Cost Center</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Name</label>
                <input
                  type="text"
                  value={newCenter.name}
                  onChange={(e) => setNewCenter({...newCenter, name: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="e.g., Marketing Department"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Description</label>
                <input
                  type="text"
                  value={newCenter.description}
                  onChange={(e) => setNewCenter({...newCenter, description: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="Optional description"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-4">
              <button
                onClick={handleAddCenter}
                className="bg-[#00C9A7] hover:bg-[#002480] text-white px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Save Cost Center
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] text-[#E8EDF2] px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Active Cost Centers</h2>
          
          {loading ? (
            <p className="text-center py-8 text-[#4A5B6E]">Loading...</p>
          ) : costCenters.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-[#1B2D42] rounded-sm">
              <p className="text-[#4A5B6E]">No cost centers defined</p>
              <p className="text-sm text-[#4A5B6E] mt-1">Add your first cost center to start tracking</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {costCenters.map((center) => (
                <div key={center.id} className="border border-[#1B2D42] p-4 rounded-sm hover:shadow-sm transition-all" data-testid={`cost-center-${center.id}`}>
                  <h3 className="heading-font text-lg font-bold text-[#E8EDF2] mb-1">{center.name}</h3>
                  {center.description && (
                    <p className="text-sm text-[#4A5B6E]">{center.description}</p>
                  )}
                  <p className="text-xs text-[#4A5B6E] mt-2 mono">ID: {center.id.slice(0, 8)}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-[#0D1B2A] border border-[#1B2D42] p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-3">How Cost Centers Work</h3>
          <ul className="space-y-2 text-sm text-[#7A8BA0]">
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-[#00C9A7] rounded-full mt-2"></span>
              <span>Every transaction can be tagged with a Cost Center (defaults to "General")</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-[#00C9A7] rounded-full mt-2"></span>
              <span>Filter Balance Sheet and P&L reports by Cost Center to view departmental profitability</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="w-1.5 h-1.5 bg-[#00C9A7] rounded-full mt-2"></span>
              <span>Use AI Prompt Interface to specify cost center when creating transactions</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default CostCenters;