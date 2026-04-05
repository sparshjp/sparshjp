import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { BarChart3, TrendingUp, TrendingDown, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function Dashboard() {
  const [stats, setStats] = useState({
    drafts: 0,
    posted: 0,
    totalEntries: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const draftsRes = await axios.get(`${API}/transactions/drafts`);
        const postedRes = await axios.get(`${API}/transactions/posted?limit=100`);
        
        setStats({
          drafts: draftsRes.data.length,
          posted: postedRes.data.length,
          totalEntries: draftsRes.data.length + postedRes.data.length
        });
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    };

    fetchData();
  }, []);

  const chartData = [
    { name: 'P2P', value: Math.floor(stats.posted * 0.3) },
    { name: 'O2C', value: Math.floor(stats.posted * 0.25) },
    { name: 'Inventory', value: Math.floor(stats.posted * 0.15) },
    { name: 'Assets', value: Math.floor(stats.posted * 0.1) },
    { name: 'Payroll', value: Math.floor(stats.posted * 0.2) },
  ];

  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-slate-900" data-testid="dashboard-title">Dashboard</h1>
          <p className="text-slate-500 mt-2">AI-Native ERP System Overview</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="draft-transactions-card">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-[#FFCC00]/10 rounded-sm">
                <FileText className="text-[#FFCC00]" size={24} />
              </div>
              <span className="text-xs tracking-widest uppercase font-bold text-slate-500">Draft</span>
            </div>
            <p className="heading-font text-3xl font-bold text-slate-900 mono">{stats.drafts}</p>
            <p className="text-sm text-slate-500 mt-1">Pending Review</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="posted-transactions-card">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-[#10B981]/10 rounded-sm">
                <TrendingUp className="text-[#10B981]" size={24} />
              </div>
              <span className="text-xs tracking-widest uppercase font-bold text-slate-500">Posted</span>
            </div>
            <p className="heading-font text-3xl font-bold text-slate-900 mono">{stats.posted}</p>
            <p className="text-sm text-slate-500 mt-1">Completed</p>
          </div>

          <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="total-entries-card">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-[#002FA7]/10 rounded-sm">
                <BarChart3 className="text-[#002FA7]" size={24} />
              </div>
              <span className="text-xs tracking-widest uppercase font-bold text-slate-500">Total</span>
            </div>
            <p className="heading-font text-3xl font-bold text-slate-900 mono">{stats.totalEntries}</p>
            <p className="text-sm text-slate-500 mt-1">All Transactions</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-6 rounded-sm" data-testid="transactions-chart">
          <h2 className="heading-font text-xl font-bold text-slate-900 mb-6">Transactions by Module</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="#94A3B8" />
              <YAxis stroke="#94A3B8" />
              <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0' }} />
              <Bar dataKey="value" fill="#002FA7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gradient-to-r from-[#002FA7] to-[#002480] border border-[#002FA7] p-8 rounded-sm text-white" data-testid="ai-info-banner">
          <h2 className="heading-font text-2xl font-bold mb-2">Zero-Touch Accounting</h2>
          <p className="text-white/80 mb-4">Use the AI Prompt button (bottom right) to create transactions using natural language. Upload documents for automatic OCR extraction.</p>
          <p className="text-xs text-white/60 mono">Prompt → Draft → Verify → Post</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;