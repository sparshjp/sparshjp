import { useState } from 'react';
import { API } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { Lock, Mail, User, LogIn } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register';
      const payload = mode === 'login' 
        ? { email, password }
        : { email, password, name, role: 'user' };
      
      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Request failed');
      }
      
      const data = await res.json();
      
      if (mode === 'login') {
        localStorage.setItem('kairos_token', data.token);
        localStorage.setItem('kairos_user', JSON.stringify(data.user));
        toast.success(`Welcome back, ${data.user.name || data.user.email}!`);
        navigate('/');
      } else {
        toast.success('Account created! Please log in.');
        setMode('login');
        setPassword('');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0D1B2A] p-4">
      <Card className="w-full max-w-md p-8 bg-[#152236] border-[#1B2D42]">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#00d4aa]/10 mb-4">
            <LogIn className="w-8 h-8 text-[#00d4aa]" />
          </div>
          <h1 className="text-2xl font-bold text-[#E8EDF2] mb-2">
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-[#7A8BA0] text-sm">
            {mode === 'login' ? 'Sign in to continue to Kairos' : 'Sign up to get started'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-[#E8EDF2] mb-2">
                <User className="inline w-4 h-4 mr-2" />
                Full Name
              </label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                required
                className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-[#E8EDF2] mb-2">
              <Mail className="inline w-4 h-4 mr-2" />
              Email
            </label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#E8EDF2] mb-2">
              <Lock className="inline w-4 h-4 mr-2" />
              Password
            </label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
              className="bg-[#0D1B2A] border-[#1B2D42] text-[#E8EDF2]"
            />
          </div>

          <Button
            type="submit"
            className="w-full bg-[#00d4aa] hover:bg-[#00b894] text-[#0D1B2A]"
            disabled={loading}
          >
            {loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="text-sm text-[#00d4aa] hover:underline"
          >
            {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </div>
      </Card>
    </div>
  );
}
