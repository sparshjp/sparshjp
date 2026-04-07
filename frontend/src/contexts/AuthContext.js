import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API } from '../App';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('kairos_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        localStorage.setItem('kairos_user', JSON.stringify(userData));
      } else {
        localStorage.removeItem('kairos_token');
        localStorage.removeItem('kairos_user');
        setUser(null);
      }
    } catch {
      // Offline or backend down — use cached user
      const cached = localStorage.getItem('kairos_user');
      if (cached) setUser(JSON.parse(cached));
    }
    setLoading(false);
  }, []);

  useEffect(() => { checkAuth(); }, [checkAuth]);

  const login = async (email, password) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('kairos_token', data.token);
    localStorage.setItem('kairos_user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try { await fetch(`${API}/auth/logout`, { method: 'POST' }); } catch {}
    localStorage.removeItem('kairos_token');
    localStorage.removeItem('kairos_user');
    setUser(null);
  };

  const hasAccess = (section) => {
    if (!user) return false;
    const SECTION_ACCESS = {
      core: ['creator', 'admin', 'finance_manager', 'project_manager', 'hr_manager', 'ap_clerk', 'ar_clerk', 'tax_compliance', 'viewer'],
      selling: ['creator', 'admin', 'finance_manager', 'ar_clerk'],
      buying: ['creator', 'admin', 'finance_manager', 'ap_clerk'],
      stock: ['creator', 'admin', 'finance_manager', 'ap_clerk', 'ar_clerk'],
      hr: ['creator', 'admin', 'hr_manager'],
      ai: ['creator'],
      delivery: ['creator', 'admin', 'project_manager'],
      accounting: ['creator', 'admin', 'finance_manager'],
      gst: ['creator', 'admin', 'finance_manager', 'tax_compliance'],
      tds: ['creator', 'admin', 'finance_manager', 'tax_compliance'],
      'reporting-ai': ['creator', 'admin', 'finance_manager', 'project_manager'],
      reports: ['creator', 'admin', 'finance_manager', 'project_manager', 'hr_manager', 'viewer'],
      settings: ['creator', 'admin'],
      'user-management': ['creator', 'admin'],
    };
    const allowed = SECTION_ACCESS[section] || [];
    return allowed.includes(user.role);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasAccess, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
