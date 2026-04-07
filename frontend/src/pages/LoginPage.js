import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Lock, Mail, LogIn, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome, ${user.name || user.email}`);
      navigate('/');
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#060e1a]" data-testid="login-page">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[#00d4aa] to-[#00a88a] mb-4 shadow-lg shadow-[#00d4aa]/20">
            <LogIn className="w-6 h-6 text-[#060e1a]" />
          </div>
          <h1 className="text-3xl font-black text-[#E8EDF2] tracking-tight">Nexora ERP</h1>
          <p className="text-[#4A5B6E] text-sm mt-2">Sign in to your workspace</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" data-testid="login-form">
          <div>
            <label className="block text-xs font-bold text-[#7A8BA0] mb-2 uppercase tracking-wider">
              <Mail className="inline w-3.5 h-3.5 mr-1.5 opacity-60" />Username / Email
            </label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="kairoserp"
              required
              data-testid="login-email"
              className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-4 py-3 text-sm text-[#E8EDF2] placeholder-[#2A3F56] focus:border-[#00d4aa]/60 focus:outline-none focus:ring-1 focus:ring-[#00d4aa]/20 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#7A8BA0] mb-2 uppercase tracking-wider">
              <Lock className="inline w-3.5 h-3.5 mr-1.5 opacity-60" />Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              data-testid="login-password"
              className="w-full bg-[#0D1B2A] border border-[#1B2D42] rounded-lg px-4 py-3 text-sm text-[#E8EDF2] placeholder-[#2A3F56] focus:border-[#00d4aa]/60 focus:outline-none focus:ring-1 focus:ring-[#00d4aa]/20 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            data-testid="login-submit"
            className="w-full py-3 rounded-lg bg-gradient-to-r from-[#00d4aa] to-[#00b894] text-[#060e1a] font-bold text-sm hover:shadow-lg hover:shadow-[#00d4aa]/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-[#060e1a]/30 border-t-[#060e1a] rounded-full animate-spin" />
            ) : (
              <>Sign In <ArrowRight size={16} /></>
            )}
          </button>
        </form>

        <p className="text-center text-[10px] text-[#2A3F56] mt-8">Nexora Digital Solutions Pvt. Ltd.</p>
      </div>
    </div>
  );
}
