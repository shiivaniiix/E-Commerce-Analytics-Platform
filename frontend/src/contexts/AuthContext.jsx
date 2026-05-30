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
    } catch (e) {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);

  const clearSession = useCallback((showMessage) => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_set_at');
    if (showMessage) {
      // simple user-facing message; consumer UI can replace this with toasts
      try {
        // eslint-disable-next-line no-alert
        alert(showMessage);
      } catch (e) {}
    }
    navigate('/login');
  }, [navigate]);

  // Auto-check token expiry on mount
  useEffect(() => {
    const tokenSet = localStorage.getItem('token_set_at');
    const access = localStorage.getItem('access_token');
    if (access && tokenSet) {
      const setAt = Number(tokenSet);
      if (Number.isFinite(setAt)) {
        const age = Date.now() - setAt;
        if (age >= FIFTEEN_DAYS_MS) {
          clearSession('Session expired. Please login again.');
        } else {
          // set a timeout to auto-logout when expires
          const remaining = FIFTEEN_DAYS_MS - age;
          const t = setTimeout(() => clearSession('Session expired. Please login again.'), remaining);
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
      // expect { access_token, customer }
      const accessToken = data.access_token;
      const customer = data.customer || data.user || null;
      setToken(accessToken);
      setUser(customer);
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('user', JSON.stringify(customer));
      localStorage.setItem('token_set_at', String(Date.now()));

      // schedule auto logout after 15 days
      const t = setTimeout(() => {
        clearSession('Session expired. Please login again.');
      }, FIFTEEN_DAYS_MS);
      // we don't keep a ref to timer; on reload mount will set again

      return data;
    } finally {
      setLoading(false);
    }
  }, [clearSession]);

  const signup = useCallback(async (payload) => {
    setLoading(true);
    try {
      const data = await authService.signup(payload);
      // do NOT auto-login: caller should redirect to /login
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthContext;
