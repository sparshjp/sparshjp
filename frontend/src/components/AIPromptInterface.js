import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Upload, Send } from 'lucide-react';
import axios from 'axios';
import { API } from '../App';
import { toast } from 'sonner';

function AIPromptInterface() {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [module, setModule] = useState('purchase-to-pay');
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await axios.post(`${API}/documents/upload`, formData);
      setUploadedDoc(response.data);
      toast.success('Document uploaded and OCR processed');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload document');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/transactions/prompt`, {
        prompt,
        module,
        document_id: uploadedDoc?.document_id
      });
      
      toast.success('Draft transaction created! Check the module page to review.');
      setPrompt('');
      setUploadedDoc(null);
      setIsOpen(false);
    } catch (error) {
      console.error('Prompt processing error:', error);
      toast.error('Failed to process prompt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 bg-[#002FA7] hover:bg-[#002480] text-white p-4 rounded-full shadow-lg transition-all flex items-center space-x-2 z-40"
        data-testid="open-ai-prompt-button"
      >
        <Sparkles size={24} />
        <span className="hidden sm:inline font-medium">AI Prompt</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-sm border border-slate-200 w-full max-w-2xl p-6 relative tracing-beam"
              data-testid="ai-prompt-modal"
            >
              <button
                onClick={() => setIsOpen(false)}
                className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600"
                data-testid="close-ai-prompt-button"
              >
                <X size={20} />
              </button>

              <h2 className="heading-font text-2xl font-bold text-slate-900 mb-2">AI Prompt Interface</h2>
              <p className="text-sm text-slate-500 mb-6">Describe your transaction in natural language</p>

              <div className="space-y-4">
                <div>
                  <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Module</label>
                  <select
                    value={module}
                    onChange={(e) => setModule(e.target.value)}
                    className="w-full border border-slate-200 rounded-sm px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#002FA7]"
                    data-testid="module-select"
                  >
                    <option value="purchase-to-pay">Purchase to Pay</option>
                    <option value="order-to-cash">Order to Cash</option>
                    <option value="inventory">Inventory</option>
                    <option value="fixed-assets">Fixed Assets</option>
                    <option value="payroll">Payroll</option>
                    <option value="banking">Banking</option>
                  </select>
                </div>

                {uploadedDoc && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-sm">
                    <p className="text-sm font-medium text-green-900">Document Uploaded</p>
                    <p className="text-xs text-green-700 mono mt-1">Vendor: {uploadedDoc.extracted_data?.vendor_name}</p>
                  </div>
                )}

                <div>
                  <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Upload Document (Optional)</label>
                  <label className="flex items-center justify-center border-2 border-dashed border-slate-200 rounded-sm p-6 cursor-pointer hover:border-[#002FA7] transition-colors" data-testid="document-upload-area">
                    <input
                      type="file"
                      onChange={handleUpload}
                      className="hidden"
                      accept="image/*,.pdf"
                      data-testid="document-upload-input"
                    />
                    <div className="text-center">
                      <Upload className="mx-auto mb-2 text-slate-400" size={32} />
                      <p className="text-sm text-slate-600">Click to upload invoice/receipt</p>
                    </div>
                  </label>
                </div>

                <div>
                  <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Prompt</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Record electricity expense of ₹15,000 for Gujarat plant for December 2025, paid to ABC Power Corp (GSTIN: 24XXXXX...). Posting date: 2025-01-02"
                    className="w-full border border-slate-200 rounded-sm px-4 py-3 mono text-sm focus:outline-none focus:ring-2 focus:ring-[#002FA7] h-32 resize-none"
                    data-testid="ai-prompt-input"
                  />
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full bg-[#002FA7] hover:bg-[#002480] text-white px-6 py-3 rounded-sm font-medium transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                  data-testid="submit-prompt-button"
                >
                  {loading ? (
                    <span>Processing...</span>
                  ) : (
                    <>
                      <Send size={18} />
                      <span>Generate Draft</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default AIPromptInterface;