import axios from 'axios';

// Single source of truth for the API base URL. The backend serves everything
// under /api, so the base URL must include it.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach the JWT to every request. We standardize on the "access_token" key
// (the AuthContext stores it under this key).
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// On 401, clear the session and bounce to login (but never loop on the
// login/auth endpoints themselves).
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';
    const isAuthCall = url.includes('/auth/login') || url.includes('/auth/signup');
    if (status === 401 && !isAuthCall) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('token_set_at');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
