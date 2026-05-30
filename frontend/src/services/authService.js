// Authentication Service (React/Vite Frontend)
// Save as: src/services/authService.js

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - attach token to every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth Service API Calls
const authService = {
  /**
   * Sign up new user
   * @param {Object} userData - User data {email, password, first_name, last_name, phone_number}
   * @returns {Promise} Login response with token
   */
  signup: async (userData) => {
    try {
      const response = await apiClient.post('/auth/signup', {
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName,
        phone_number: userData.phoneNumber || null
      });

      // Do NOT auto-store token or log the user in after signup.
      // Return the server response so the UI can redirect to /login.
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise} Login response with token
   */
  login: async (email, password) => {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password
      });

      // Return the server response. AuthContext will handle storing the token and user.
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Get current authenticated user
   * @returns {Promise} Current user data
   */
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Change user password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Confirm new password
   * @returns {Promise} Success response
   */
  changePassword: async (currentPassword, newPassword, confirmPassword) => {
    try {
      const response = await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Check if email is available
   * @param {string} email - Email to check
   * @returns {Promise} Availability status
   */
  checkEmailAvailability: async (email) => {
    try {
      const response = await apiClient.post('/auth/check-email', { email });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Deactivate user account
   * @returns {Promise} Success response
   */
  deactivateAccount: async () => {
    try {
      const response = await apiClient.post('/auth/deactivate');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Validate current token
   * @returns {Promise} Token validity status
   */
  validateToken: async () => {
    try {
      const response = await apiClient.get('/auth/validate-token');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Logout user
   */
  logout: () => {
    // Client code should handle clearing storage and redirecting.
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_set_at');
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} Authentication status
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored user data
   * @returns {Object|null} User data or null
   */
  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  /**
   * Get access token
   * @returns {string|null} Access token or null
   */
  getToken: () => {
    return localStorage.getItem('access_token');
  }
};

export default authService;
