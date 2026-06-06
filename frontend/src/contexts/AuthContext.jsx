import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const AuthContext = createContext(null);

const FIFTEEN_DAYS_MS = 15 * 24 * 60 * 60 * 1000;

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);

  const clearSession = useCallback(
    (redirect = true) => {
      setUser(null);
      setToken(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('token_set_at');
      if (redirect) navigate('/login');
    },
    [navigate],
  );

  // Auto-expire the session after 15 days.
  useEffect(() => {
    const tokenSet = localStorage.getItem('token_set_at');
    const access = localStorage.getItem('access_token');
    if (access && tokenSet) {
      const setAt = Number(tokenSet);
      if (Number.isFinite(setAt)) {
        const age = Date.now() - setAt;
        if (age >= FIFTEEN_DAYS_MS) {
          clearSession();
        } else {
          const t = setTimeout(() => clearSession(), FIFTEEN_DAYS_MS - age);
          return () => clearTimeout(t);
        }
      }
    }
    return undefined;
  }, [clearSession]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const data = await authService.login(email, password);
      const accessToken = data.access_token;
      const customer = data.customer || data.user || null;
      setToken(accessToken);
      setUser(customer);
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('user', JSON.stringify(customer));
      localStorage.setItem('token_set_at', String(Date.now()));
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const signup = useCallback(async (payload) => {
    setLoading(true);
    try {
      // Intentionally does NOT auto-login; caller redirects to /login.
      return await authService.signup(payload);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  // Keep the cached user in sync after profile edits.
  const updateUser = useCallback((updated) => {
    setUser((prev) => {
      const next = { ...(prev || {}), ...(updated || {}) };
      localStorage.setItem('user', JSON.stringify(next));
      return next;
    });
  }, []);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthContext;
