import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Users, Calendar, FileText } from 'lucide-react';
import { toast } from 'sonner';

function HR() {
  const [activeTab, setActiveTab] = useState('employees');
  const [employees, setEmployees] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [leaves, setLeaves] = useState([]);

  useEffect(() => {
    if (activeTab === 'employees') fetchEmployees();
    else if (activeTab === 'attendance') fetchAttendance();
    else if (activeTab === 'leave') fetchLeaves();
  }, [activeTab]);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API}/hr/employees`);
      setEmployees(res.data);
    } catch (error) {
      toast.error('Failed to fetch employees');
    }
  };

  const fetchAttendance = async () => {
    try {
      const res = await axios.get(`${API}/hr/attendance`);
      setAttendance(res.data);
    } catch (error) {
      toast.error('Failed to fetch attendance');
    }
  };

  const fetchLeaves = async () => {
    try {
      const res = await axios.get(`${API}/hr/leave-applications`);
      setLeaves(res.data);
    } catch (error) {
      toast.error('Failed to fetch leaves');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="heading-font text-4xl font-black tracking-tighter text-[#E8EDF2]">HR & Payroll</h1>
        
        <div className="flex space-x-1 border-b border-[#1B2D42]">
          <button onClick={() => setActiveTab('employees')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'employees' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <Users size={16} /><span>Employees</span><span className="mono text-xs px-2 py-0.5 rounded bg-[#1B2D42]">{employees.length}</span>
          </button>
          <button onClick={() => setActiveTab('attendance')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'attendance' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <Calendar size={16} /><span>Attendance</span>
          </button>
          <button onClick={() => setActiveTab('leave')} className={`px-4 py-3 font-medium flex items-center space-x-2 border-b-2 ${activeTab === 'leave' ? 'border-[#002FA7] text-[#00C9A7]' : 'border-transparent text-[#4A5B6E]'}`}>
            <FileText size={16} /><span>Leave</span>
          </button>
        </div>

        <div className="bg-[#152236] border border-[#1B2D42] rounded-sm p-6">
          {activeTab === 'employees' && (
            employees.length === 0 ? (
              <div className="text-center py-12"><Users className="mx-auto mb-3 text-slate-300" size={48} /><p className="text-[#4A5B6E]">No employees</p><p className="text-sm text-[#4A5B6E] mt-1">Use AI: "Add employee John Doe, Marketing, joined 2025-01-01"</p></div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">{employees.map(emp => (<div key={emp.id} className="border border-[#1B2D42] p-4 rounded-sm"><h3 className="font-bold text-[#E8EDF2]">{emp.employee_name}</h3><p className="text-sm text-[#4A5B6E]">{emp.designation}</p><p className="text-xs text-[#4A5B6E] mt-1">{emp.department}</p></div>))}</div>
            )
          )}

          {activeTab === 'attendance' && (
            <div className="text-center py-12"><Calendar className="mx-auto mb-3 text-slate-300" size={48} /><p className="text-[#4A5B6E]">Use AI: "Mark attendance for all employees today" or upload team photo</p></div>
          )}

          {activeTab === 'leave' && (
            <div className="text-center py-12"><FileText className="mx-auto mb-3 text-slate-300" size={48} /><p className="text-[#4A5B6E]">No leave applications</p></div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HR;
