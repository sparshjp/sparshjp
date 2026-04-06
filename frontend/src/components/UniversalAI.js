import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, Loader } from 'lucide-react';
import axios from 'axios';
import { API } from '../App';
import { toast } from 'sonner';

function UniversalAI() {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      
      const response = await axios.post(`${API}/ai/universal-prompt`, {
        prompt,
        context: {}
      });
      
      setResult(response.data);
      toast.success(`Detected module: ${response.data.module || 'accounting'}`);
      
      // Optionally close after success
      setTimeout(() => {
        setPrompt('');
        setResult(null);
      }, 3000);
      
    } catch (error) {
      console.error('AI prompt error:', error);
      toast.error('Failed to process prompt');
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    "Customer ABC Corp wants 100 laptops at ₹50k each, delivery in 2 weeks",
    "Mark attendance for all employees today",
    "John Doe from Tech Solutions inquired about our ERP system",
    "Create PO for 500 units of Product X from Vendor ABC",
    "Add item: Laptop Dell XPS 13, HSN 84713020, rate ₹80000"
  ];

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 bg-gradient-to-r from-[#002FA7] to-[#0039CC] hover:shadow-lg text-white p-4 rounded-full shadow-md transition-all flex items-center space-x-2 z-40 group"
        data-testid="universal-ai-button"
      >
        <Sparkles size={24} className="group-hover:rotate-12 transition-transform" />
        <span className="hidden sm:inline font-medium">AI Assistant</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-sm border-2 border-[#002FA7] w-full max-w-3xl p-6 relative"
              data-testid="universal-ai-modal"
            >
              <button
                onClick={() => setIsOpen(false)}
                className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-sm"
              >
                <X size={20} />
              </button>

              <div className="flex items-center space-x-3 mb-4">
                <div className="p-3 bg-gradient-to-r from-[#002FA7] to-[#0039CC] rounded-full">
                  <Sparkles size={24} className="text-white" />
                </div>
                <div>
                  <h2 className="heading-font text-2xl font-black text-slate-900">Universal AI Assistant</h2>
                  <p className="text-sm text-slate-500">Tell me what you need, I'll handle the rest</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-2 block">Your Request</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Create quotation for Tech Corp - 50 laptops @ 60k each..."
                    className="w-full border-2 border-slate-200 focus:border-[#002FA7] rounded-sm px-4 py-3 text-sm focus:outline-none h-32 resize-none"
                    data-testid="universal-ai-input"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        handleSubmit();
                      }
                    }}
                  />
                  <p className="text-xs text-slate-400 mt-1">Press Ctrl+Enter to submit</p>
                </div>

                {result && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-green-50 border-2 border-green-200 rounded-sm"
                  >
                    <p className="text-sm font-bold text-green-900 mb-2">✓ Processed Successfully</p>
                    <p className="text-xs text-green-700">Module: {result.module || 'Unknown'}</p>
                    <p className="text-xs text-green-600 mt-1">Check the relevant module page to review the draft</p>
                  </motion.div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={loading || !prompt.trim()}
                  className="w-full bg-gradient-to-r from-[#002FA7] to-[#0039CC] hover:shadow-lg text-white px-6 py-3 rounded-sm font-medium transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  data-testid="universal-ai-submit"
                >
                  {loading ? (
                    <>
                      <Loader size={18} className="animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      <span>Process with AI</span>
                    </>
                  )}
                </button>

                <div className="pt-4 border-t border-slate-200">
                  <p className="text-xs tracking-widest uppercase font-bold text-slate-500 mb-3">Example Prompts</p>
                  <div className="space-y-2">
                    {examples.map((example, idx) => (
                      <button
                        key={idx}
                        onClick={() => setPrompt(example)}
                        className="w-full text-left text-xs p-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-sm text-slate-700 transition-colors"
                      >
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default UniversalAI;
