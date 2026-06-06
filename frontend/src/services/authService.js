// Authentication service (React/Vite frontend)
// Reuses the single shared axios client in ./api so that the base URL,
// token handling, and 401 behavior are consistent across the whole app.

import apiClient from './api';

const authService = {
  /**
   * Sign up a new user. Does NOT auto-login; the UI redirects to /login.
   * @param {{email,password,firstName,lastName,phoneNumber}} userData
   */
  signup: async (userData) => {
    try {
      const response = await apiClient.post('/auth/signup', {
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName,
        phone_number: userData.phoneNumber || null,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /** Login with email + password. Returns { access_token, customer, ... }. */
  login: async (email, password) => {
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /** Get the current authenticated user (GET /api/auth/me). */
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  changePassword: async (currentPassword, newPassword, confirmPassword) => {
    try {
      const response = await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  checkEmailAvailability: async (email) => {
    try {
      const response = await apiClient.post('/auth/check-email', { email });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_set_at');
  },

  isAuthenticated: () => !!localStorage.getItem('access_token'),

  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  getToken: () => localStorage.getItem('access_token'),
};

export default authService;
