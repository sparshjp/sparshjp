import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Plus, Search, Building, Users } from 'lucide-react';
import { toast } from 'sonner';

function MasterData() {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [entityType, setEntityType] = useState('vendor');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEntity, setNewEntity] = useState({
    entity_type: 'vendor',
    name: '',
    gstin: '',
    pan: '',
    address: '',
    contact: '',
    email: ''
  });

  useEffect(() => {
    fetchEntities();
  }, [entityType]);

  const fetchEntities = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/entities?entity_type=${entityType}`);
      setEntities(res.data);
    } catch (error) {
      console.error('Failed to fetch entities:', error);
      toast.error('Failed to load entities');
    } finally {
      setLoading(false);
    }
  };

  const handleAddEntity = async () => {
    if (!newEntity.name) {
      toast.error('Entity name is required');
      return;
    }

    try {
      const res = await axios.post(`${API}/entities`, {...newEntity, entity_type: entityType});
      toast.success(`${entityType === 'vendor' ? 'Vendor' : 'Client'} added successfully`);
      if (res.data.legal_name) {
        toast.info(`Auto-filled from GSTIN: ${res.data.legal_name}`);
      }
      setShowAddForm(false);
      setNewEntity({ entity_type: entityType, name: '', gstin: '', pan: '', address: '', contact: '', email: '' });
      fetchEntities();
    } catch (error) {
      console.error('Failed to add entity:', error);
      toast.error('Failed to add entity');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="master-data-title">
              Master Data
            </h1>
            <p className="text-[#4A5B6E] mt-2">Manage vendors, clients, and party information</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-[#00C9A7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium transition-colors flex items-center space-x-2"
            data-testid="add-entity-button"
          >
            <Plus size={16} />
            <span>Add {entityType === 'vendor' ? 'Vendor' : 'Client'}</span>
          </button>
        </div>

        <div className="flex space-x-4 border-b border-[#1B2D42]">
          <button
            onClick={() => setEntityType('vendor')}
            className={`px-4 py-2 font-medium transition-colors ${entityType === 'vendor' ? 'border-b-2 border-[#002FA7] text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#E8EDF2]'}`}
            data-testid="vendors-tab"
          >
            <div className="flex items-center space-x-2">
              <Building size={16} />
              <span>Vendors</span>
            </div>
          </button>
          <button
            onClick={() => setEntityType('client')}
            className={`px-4 py-2 font-medium transition-colors ${entityType === 'client' ? 'border-b-2 border-[#002FA7] text-[#00C9A7]' : 'text-[#4A5B6E] hover:text-[#E8EDF2]'}`}
            data-testid="clients-tab"
          >
            <div className="flex items-center space-x-2">
              <Users size={16} />
              <span>Clients</span>
            </div>
          </button>
        </div>

        {showAddForm && (
          <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm" data-testid="add-entity-form">
            <h3 className="heading-font text-lg font-bold text-[#E8EDF2] mb-4">Add New {entityType === 'vendor' ? 'Vendor' : 'Client'}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Name</label>
                <input
                  type="text"
                  value={newEntity.name}
                  onChange={(e) => setNewEntity({...newEntity, name: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="Company/Person name"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">GSTIN (15 chars)</label>
                <input
                  type="text"
                  value={newEntity.gstin}
                  onChange={(e) => setNewEntity({...newEntity, gstin: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] mono placeholder:text-[#4A5B6E]"
                  placeholder="22AAAAA0000A1Z5"
                  maxLength="15"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">PAN</label>
                <input
                  type="text"
                  value={newEntity.pan}
                  onChange={(e) => setNewEntity({...newEntity, pan: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] mono placeholder:text-[#4A5B6E]"
                  placeholder="ABCDE1234F"
                  maxLength="10"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Contact</label>
                <input
                  type="text"
                  value={newEntity.contact}
                  onChange={(e) => setNewEntity({...newEntity, contact: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="Phone number"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Email</label>
                <input
                  type="email"
                  value={newEntity.email}
                  onChange={(e) => setNewEntity({...newEntity, email: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="email@example.com"
                />
              </div>
              <div>
                <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Address</label>
                <input
                  type="text"
                  value={newEntity.address}
                  onChange={(e) => setNewEntity({...newEntity, address: e.target.value})}
                  className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-sm px-4 py-2 text-[#E8EDF2] focus:outline-none focus:ring-2 focus:ring-[#00C9A7] placeholder:text-[#4A5B6E]"
                  placeholder="Full address"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-4">
              <button
                onClick={handleAddEntity}
                className="bg-[#00C9A7] hover:bg-[#002480] text-white px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Save {entityType === 'vendor' ? 'Vendor' : 'Client'}
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] text-[#E8EDF2] px-6 py-2 rounded-sm text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
            <p className="text-xs text-[#4A5B6E] mt-3">💡 Enter GSTIN to auto-fetch legal name, constitution, and status</p>
          </div>
        )}

        <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">
            {entityType === 'vendor' ? 'Vendors' : 'Clients'} ({entities.length})
          </h2>
          
          {loading ? (
            <p className="text-center py-8 text-[#4A5B6E]">Loading...</p>
          ) : entities.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-[#1B2D42] rounded-sm">
              <p className="text-[#4A5B6E]">No {entityType}s found</p>
              <p className="text-sm text-[#4A5B6E] mt-1">Add your first {entityType}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#1B2D42]">
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Name</th>
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">GSTIN</th>
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Status</th>
                    <th className="pb-2 text-left font-bold text-xs tracking-widest uppercase text-[#4A5B6E]">Contact</th>
                  </tr>
                </thead>
                <tbody>
                  {entities.map((entity) => (
                    <tr key={entity.id} className="border-b border-[#1B2D42]/40 hover:bg-[#1B2D42]/30">
                      <td className="py-3">
                        <div>
                          <p className="font-medium text-[#E8EDF2]">{entity.name}</p>
                          {entity.legal_name && entity.legal_name !== entity.name && (
                            <p className="text-xs text-[#4A5B6E]">{entity.legal_name}</p>
                          )}
                        </div>
                      </td>
                      <td className="py-3 mono text-[#7A8BA0]">{entity.gstin || '-'}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs ${entity.status === 'Active' ? 'bg-[#00C9A7]/15 text-[#00C9A7]' : 'bg-[#FF4D6A]/15 text-[#FF4D6A]'}`}>
                          {entity.status}
                        </span>
                      </td>
                      <td className="py-3 text-[#7A8BA0]">{entity.contact || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MasterData;