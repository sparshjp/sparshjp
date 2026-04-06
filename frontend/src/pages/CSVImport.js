import React, { useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

function CSVImport() {
  const [module, setModule] = useState('purchases');
  const [file, setFile] = useState(null);
  const [validation, setValidation] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);

  const modules = [
    { value: 'purchases', label: 'Purchases' },
    { value: 'sales', label: 'Sales' },
    { value: 'journals', label: 'Journal Entries' },
    { value: 'payments', label: 'Payments' }
  ];

  const handleFileSelect = (e) => {
    setFile(e.target.files[0]);
    setValidation(null);
    setImportResult(null);
  };

  const handleValidate = async () => {
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    try {
      const text = await file.text();
      const res = await axios.post(`${API}/import/validate`, {
        module,
        csv_data: text
      });
      setValidation(res.data);
      
      if (res.data.valid) {
        toast.success('Validation passed! Ready to import.');
      } else {
        toast.error('Validation failed. Please fix errors.');
      }
    } catch (error) {
      console.error('Validation error:', error);
      toast.error('Failed to validate CSV');
    }
  };

  const handleImport = async () => {
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    if (validation && !validation.valid) {
      toast.error('Please fix validation errors first');
      return;
    }

    try {
      setImporting(true);
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await axios.post(`${API}/import/process?module=${module}`, formData);
      setImportResult(res.data);
      
      if (res.data.success) {
        toast.success(`Successfully imported ${res.data.imported} transactions`);
      } else {
        toast.error('Import failed');
      }
    } catch (error) {
      console.error('Import error:', error);
      toast.error('Failed to import CSV');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] p-4 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="heading-font text-4xl sm:text-5xl font-black tracking-tighter text-[#E8EDF2]" data-testid="csv-import-title">
            CSV Import
          </h1>
          <p className="text-[#4A5B6E] mt-2">Bulk import transactions from Excel/CSV files</p>
        </div>

        <div className="bg-[#152236] border border-[#1B2D42] p-6 rounded-sm">
          <h2 className="heading-font text-xl font-bold text-[#E8EDF2] mb-4">Import Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Module</label>
              <select
                value={module}
                onChange={(e) => setModule(e.target.value)}
                className="w-full md:w-64 border border-[#1B2D42] rounded-sm px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#002FA7]"
              >
                {modules.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-2 block">Upload CSV File</label>
              <label className="flex items-center justify-center border-2 border-dashed border-[#1B2D42] rounded-sm p-8 cursor-pointer hover:border-[#002FA7] transition-colors" data-testid="csv-upload-area">
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  accept=".csv"
                />
                <div className="text-center">
                  <Upload className="mx-auto mb-2 text-[#4A5B6E]" size={32} />
                  <p className="text-sm text-[#4A5B6E]">{file ? file.name : 'Click to upload CSV file'}</p>
                  {file && <p className="text-xs text-[#4A5B6E] mt-1">{(file.size / 1024).toFixed(2)} KB</p>}
                </div>
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleValidate}
                disabled={!file}
                className="bg-[#152236] border border-[#1B2D42] hover:bg-[#152236] text-[#E8EDF2] px-6 py-2 rounded-sm text-sm font-medium transition-colors disabled:opacity-50"
              >
                Validate CSV
              </button>
              <button
                onClick={handleImport}
                disabled={!file || importing}
                className="bg-[#00C9A7] hover:bg-[#002480] text-white px-6 py-2 rounded-sm text-sm font-medium transition-colors disabled:opacity-50"
                data-testid="import-button"
              >
                {importing ? 'Importing...' : 'Import Transactions'}
              </button>
            </div>
          </div>
        </div>

        {validation && (
          <div className={`border p-6 rounded-sm ${validation.valid ? 'bg-[#00C9A7]/10 border-green-200' : 'bg-[#FF4D6A]/10 border-red-200'}`} data-testid="validation-result">
            <div className="flex items-start space-x-3">
              {validation.valid ? (
                <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
              ) : (
                <AlertCircle className="text-red-600 flex-shrink-0" size={24} />
              )}
              <div className="flex-1">
                <h3 className="heading-font text-lg font-bold mb-2">
                  {validation.valid ? 'Validation Passed' : 'Validation Failed'}
                </h3>
                <p className="text-sm mb-3">Found {validation.row_count} rows</p>
                
                {validation.errors.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-bold mb-2">Errors:</p>
                    <ul className="space-y-1 text-sm">
                      {validation.errors.map((err, idx) => (
                        <li key={idx} className="text-red-700">• {err}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {validation.warnings.length > 0 && (
                  <div>
                    <p className="text-sm font-bold mb-2">Warnings:</p>
                    <ul className="space-y-1 text-sm">
                      {validation.warnings.map((warn, idx) => (
                        <li key={idx} className="text-yellow-700">• {warn}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {importResult && (
          <div className="bg-[#00C9A7]/10 border border-green-200 p-6 rounded-sm" data-testid="import-result">
            <div className="flex items-start space-x-3">
              <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
              <div>
                <h3 className="heading-font text-lg font-bold text-green-900 mb-2">Import Successful</h3>
                <p className="text-sm text-green-700">Imported {importResult.imported} transactions to {module} module</p>
                <p className="text-xs text-green-600 mt-2">Transactions are in draft status. Review and post them from the module page.</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-[#F4F4F5] border border-[#1B2D42] p-6 rounded-sm">
          <h3 className="text-xs tracking-widest uppercase font-bold text-[#4A5B6E] mb-3">Zoho-Standard CSV Format</h3>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm font-bold text-[#7A8BA0] mb-2">Purchases/Sales:</p>
              <code className="block bg-[#152236] p-3 rounded-sm text-xs mono border border-[#1B2D42]">
                Date, Entity Name, Item/Service, HSN Code, Quantity, Rate, GST Rate, Cess, Total, Cost Center
              </code>
              <p className="text-xs text-[#4A5B6E] mt-2">Example: "2026-01-15, ABC Suppliers, Laptop, 84713020, 1, 50000, 18, 0, 59000, IT Department"</p>
            </div>

            <div>
              <p className="text-sm font-bold text-[#7A8BA0] mb-2">Journal Entries:</p>
              <code className="block bg-[#152236] p-3 rounded-sm text-xs mono border border-[#1B2D42]">
                Date, Ledger, Debit, Credit, Description, Cost Center
              </code>
              <p className="text-xs text-[#4A5B6E] mt-2">Example: "2026-01-15, Office Rent, 25000, 0, January rent payment, Mumbai Office"</p>
            </div>

            <div>
              <p className="text-sm font-bold text-[#7A8BA0] mb-2">Payments:</p>
              <code className="block bg-[#152236] p-3 rounded-sm text-xs mono border border-[#1B2D42]">
                Date, Entity Name, Amount, Payment Mode, Description
              </code>
            </div>
          </div>

          <div className="mt-4 p-4 bg-[#00C9A7]/10 border border-blue-200 rounded-sm">
            <p className="text-sm font-bold text-blue-900 mb-1">Important Notes:</p>
            <ul className="space-y-1 text-xs text-blue-700">
              <li>• Date format must be YYYY-MM-DD</li>
              <li>• For purchases with HSN codes, inventory will be automatically updated</li>
              <li>• Ledger names must exist in Chart of Accounts (validation will warn if missing)</li>
              <li>• All imported transactions start in draft status for review</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CSVImport;