import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Database, Download, Search, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

function AdminDataTables() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState({ records: [], total: 0 });
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const limit = 50;

  useEffect(() => {
    fetchTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      fetchTableData();
    }
  }, [selectedTable, page, search]);

  const fetchTables = async () => {
    try {
      const res = await axios.get(`${API}/admin/tables`);
      setTables(res.data);
      if (res.data.length > 0 && !selectedTable) {
        setSelectedTable(res.data[0].name);
      }
    } catch (error) {
      toast.error('Failed to fetch tables');
    }
  };

  const fetchTableData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/admin/tables/${selectedTable}`, {
        params: { skip: page * limit, limit, search: search || undefined }
      });
      setTableData(res.data);
    } catch (error) {
      toast.error('Failed to fetch table data');
    } finally {
      setLoading(false);
    }
  };

  const exportTable = async () => {
    try {
      const res = await axios.get(`${API}/admin/tables/${selectedTable}/export`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedTable}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Table exported!');
    } catch (error) {
      toast.error('Failed to export');
    }
  };

  const renderValue = (value) => {
    if (value === null || value === undefined) return <span className="text-slate-400">null</span>;
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'object') return <code className="text-xs bg-slate-100 px-1 rounded">{JSON.stringify(value).substring(0, 50)}...</code>;
    if (typeof value === 'string' && value.length > 50) return value.substring(0, 50) + '...';
    return value.toString();
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-full mx-auto space-y-6">
        <div>
          <h1 className="heading-font text-4xl font-black tracking-tighter text-slate-900 flex items-center space-x-3">
            <Database size={40} />
            <span>Admin Data Tables</span>
          </h1>
          <p className="text-slate-500 mt-2">Complete database access with unique IDs</p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Tables Sidebar */}
          <div className="col-span-12 lg:col-span-3">
            <div className="bg-white border border-slate-200 rounded-sm p-4 sticky top-24">
              <h3 className="font-bold text-slate-900 mb-3">Tables ({tables.length})</h3>
              <div className="space-y-1 max-h-[600px] overflow-y-auto">
                {tables.map((table) => (
                  <button
                    key={table.name}
                    onClick={() => { setSelectedTable(table.name); setPage(0); }}
                    className={`w-full text-left px-3 py-2 rounded-sm text-sm transition-colors ${
                      selectedTable === table.name
                        ? 'bg-[#002FA7] text-white'
                        : 'hover:bg-slate-100 text-slate-700'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{table.name}</span>
                      <span className="mono text-xs">{table.count}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Table Data */}
          <div className="col-span-12 lg:col-span-9">
            <div className="bg-white border border-slate-200 rounded-sm">
              {/* Header */}
              <div className="p-4 border-b border-slate-200">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h2 className="heading-font text-xl font-bold text-slate-900">{selectedTable}</h2>
                    <p className="text-xs text-slate-500 mono mt-1">
                      {tableData.total} records | Page {page + 1} of {Math.ceil(tableData.total / limit)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
                      <input
                        type="text"
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setPage(0); }}
                        placeholder="Search..."
                        className="pl-10 pr-4 py-2 border border-slate-200 rounded-sm text-sm focus:outline-none focus:ring-2 focus:ring-[#002FA7]"
                      />
                    </div>
                    <button
                      onClick={fetchTableData}
                      className="p-2 border border-slate-200 hover:bg-slate-50 rounded-sm"
                    >
                      <RefreshCw size={16} />
                    </button>
                    <button
                      onClick={exportTable}
                      className="flex items-center space-x-2 px-4 py-2 bg-[#002FA7] hover:bg-[#002480] text-white rounded-sm text-sm font-medium"
                    >
                      <Download size={16} />
                      <span>Export CSV</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Data */}
              <div className="p-4">
                {loading ? (
                  <p className="text-center py-12 text-slate-500">Loading...</p>
                ) : tableData.records.length === 0 ? (
                  <p className="text-center py-12 text-slate-500">No records</p>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className="border-b border-slate-200">
                            {Object.keys(tableData.records[0]).map((key) => (
                              <th key={key} className="pb-2 px-2 text-left font-bold tracking-widest uppercase text-slate-500 whitespace-nowrap">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="mono">
                          {tableData.records.map((record, idx) => (
                            <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                              {Object.entries(record).map(([key, value]) => (
                                <td key={key} className="py-2 px-2 text-slate-700 whitespace-nowrap">
                                  {key === 'id' ? (
                                    <span className="px-2 py-1 bg-[#002FA7]/10 text-[#002FA7] rounded font-medium">
                                      {value}
                                    </span>
                                  ) : (
                                    renderValue(value)
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    {tableData.total > limit && (
                      <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200">
                        <p className="text-sm text-slate-600">
                          Showing {page * limit + 1} to {Math.min((page + 1) * limit, tableData.total)} of {tableData.total}
                        </p>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setPage(Math.max(0, page - 1))}
                            disabled={page === 0}
                            className="px-4 py-2 border border-slate-200 rounded-sm text-sm font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Previous
                          </button>
                          <button
                            onClick={() => setPage(page + 1)}
                            disabled={(page + 1) * limit >= tableData.total}
                            className="px-4 py-2 border border-slate-200 rounded-sm text-sm font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDataTables;
