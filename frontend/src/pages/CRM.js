import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Users, Star, UserCheck, TrendingUp, Plus } from 'lucide-react';
import { toast } from 'sonner';

function CRM() {
  const [activeTab, setActiveTab] = useState('leads');
  const [leads, setLeads] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'leads') fetchLeads();
    else if (activeTab === 'opportunities') fetchOpportunities();
    else if (activeTab === 'customers') fetchCustomers();
  }, [activeTab]);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/crm/leads`);
      setLeads(res.data);
    } catch (error) {
      toast.error('Failed to fetch leads');
    } finally {
      setLoading(false);
    }
  };

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/crm/opportunities`);
      setOpportunities(res.data);
    } catch (error) {
      toast.error('Failed to fetch opportunities');
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/crm/customers`);
      setCustomers(res.data);
    } catch (error) {
      toast.error('Failed to fetch customers');
    } finally {
      setLoading(false);
    }
  };

  const qualifyLead = async (leadId) => {
    try {
      const res = await axios.post(`${API}/crm/leads/${leadId}/qualify`);
      toast.success(`Lead scored: ${res.data.qualification_score}/100`);
      fetchLeads();
    } catch (error) {
      toast.error('Failed to qualify lead');
    }
  };

  const convertLead = async (leadId) => {
    try {
      await axios.post(`${API}/crm/leads/${leadId}/convert`);
      toast.success('Lead converted to customer!');
      fetchLeads();
    } catch (error) {
      toast.error('Failed to convert lead');
    }
  };

  const tabs = [
    { id: 'leads', label: 'Leads', icon: Users, count: leads.length },
    { id: 'opportunities', label: 'Opportunities', icon: TrendingUp, count: opportunities.length },
    { id: 'customers', label: 'Customers', icon: UserCheck, count: customers.length },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="crm-title">
              CRM
            </h1>
            <p className="text-[#4A5B6E] mt-2">Customer Relationship Management</p>
          </div>
          <button className="bg-[#00C9A7] hover:bg-[#002480] text-white px-4 py-2 rounded-sm text-sm font-medium flex items-center space-x-2">
            <Plus size={16} />
            <span>New Lead</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 border-b border-[#1B2D42]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 font-medium transition-colors flex items-center space-x-2 border-b-2 ${
                  activeTab === tab.id
                    ? 'border-[#002FA7] text-[#00C9A7]'
                    : 'border-transparent text-[#4A5B6E] hover:text-[#E8EDF2]'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
                <span className="mono text-xs px-2 py-0.5 rounded bg-[#1B2D42]">{tab.count}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="bg-[#152236] border border-[#1B2D42] rounded-sm p-6">
          {loading ? (
            <p className="text-center py-12 text-[#4A5B6E]">Loading...</p>
          ) : activeTab === 'leads' ? (
            leads.length === 0 ? (
              <div className="text-center py-12">
                <Users className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No leads yet</p>
                <p className="text-sm text-[#4A5B6E] mt-1">Use AI Prompt to capture leads from conversations</p>
              </div>
            ) : (
              <div className="space-y-4">
                {leads.map((lead) => (
                  <div key={lead.id} className="border border-[#1B2D42] p-4 rounded-sm hover:shadow-sm transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-bold text-[#E8EDF2]">{lead.lead_name || lead.contact_name || lead.company || '—'}</h3>
                        {(lead.company_name || lead.company) && <p className="text-sm text-[#4A5B6E]">{lead.company_name || lead.company}</p>}
                        <p className="text-sm text-[#4A5B6E] mt-2">{lead.requirement || lead.interest || ''}</p>
                        <div className="flex items-center space-x-4 mt-3 text-xs">
                          {lead.email && <span className="text-[#4A5B6E]">{lead.email}</span>}
                          {lead.phone && <span className="text-[#4A5B6E]">{lead.phone}</span>}
                          {lead.ai_score && (
                            <span className="flex items-center space-x-1 text-[#00C9A7]">
                              <Star size={12} fill="#002FA7" />
                              <span className="mono font-bold">{lead.ai_score}/100</span>
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-col space-y-2 ml-4">
                        <span className={`px-3 py-1 rounded text-xs font-medium ${
                          lead.status === 'Open' ? 'bg-blue-100 text-blue-700' :
                          lead.status === 'Qualified' ? 'bg-green-100 text-green-700' :
                          lead.status === 'Converted' ? 'bg-purple-100 text-purple-700' :
                          'bg-red-100 text-red-700'
                        }`}>{lead.status || lead.stage}</span>
                        {lead.status === 'Open' && (
                          <>
                            <button
                              onClick={() => qualifyLead(lead.id)}
                              className="text-xs px-3 py-1 bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] rounded-sm"
                            >
                              AI Qualify
                            </button>
                            <button
                              onClick={() => convertLead(lead.id)}
                              className="text-xs px-3 py-1 bg-[#00C9A7] text-white hover:bg-[#002480] rounded-sm"
                            >
                              Convert
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : activeTab === 'opportunities' ? (
            opportunities.length === 0 ? (
              <div className="text-center py-12">
                <TrendingUp className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No opportunities</p>
              </div>
            ) : (
              <div className="space-y-4">
                {opportunities.map((opp) => (
                  <div key={opp.id} className="border border-[#1B2D42] p-4 rounded-sm">
                    <h3 className="font-bold text-[#E8EDF2]">{opp.party_name}</h3>
                    <p className="text-sm text-[#4A5B6E] mt-1">Amount: ₹{opp.opportunity_amount?.toLocaleString()}</p>
                    <p className="text-xs text-[#4A5B6E] mt-1">Probability: {opp.probability}%</p>
                  </div>
                ))}
              </div>
            )
          ) : (
            customers.length === 0 ? (
              <div className="text-center py-12">
                <UserCheck className="mx-auto mb-3 text-slate-300" size={48} />
                <p className="text-[#4A5B6E]">No customers</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {customers.map((customer) => (
                  <div key={customer.id} className="border border-[#1B2D42] p-4 rounded-sm hover:shadow-sm transition-all">
                    <h3 className="font-bold text-[#E8EDF2]">{customer.customer_name}</h3>
                    <p className="text-xs text-[#4A5B6E] mt-1">{customer.customer_type}</p>
                    {customer.gstin && <p className="text-xs text-[#4A5B6E] mono mt-2">GSTIN: {customer.gstin}</p>}
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default CRM;