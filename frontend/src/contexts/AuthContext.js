import { createContext, useContext, useState, useCallback } from 'react';
import { API } from '../App';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [creatorMode, setCreatorMode] = useState(false);
  const [creatorToken, setCreatorToken] = useState(localStorage.getItem('kairos_creator_token') || '');

  // Default user — full access to ERP, no login needed
  const user = {
    name: creatorMode ? 'Kairos Creator' : 'Kairos User',
    role: creatorMode ? 'creator' : 'admin',
    username: creatorMode ? 'kairoserp' : 'user',
  };

  const enterCreatorMode = useCallback(async (password) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'kairoserp', password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid password');
    }
    const data = await res.json();
    localStorage.setItem('kairos_creator_token', data.token);
    setCreatorToken(data.token);
    setCreatorMode(true);
    return true;
  }, []);

  const exitCreatorMode = useCallback(() => {
    localStorage.removeItem('kairos_creator_token');
    setCreatorToken('');
    setCreatorMode(false);
  }, []);

  // Check if stored token is still valid on mount
  useState(() => {
    if (creatorToken) {
      fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${creatorToken}` } })
        .then(res => { if (res.ok) setCreatorMode(true); else { localStorage.removeItem('kairos_creator_token'); setCreatorToken(''); } })
        .catch(() => {});
    }
  });

  // All sections accessible without login
  const hasAccess = () => true;

  return (
    <AuthContext.Provider value={{ user, loading: false, hasAccess, creatorMode, enterCreatorMode, exitCreatorMode, creatorToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
