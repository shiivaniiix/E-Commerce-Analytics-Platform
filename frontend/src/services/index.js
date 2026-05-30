import apiClient from './api';

export const healthCheckService = {
  check: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Health check failed');
    }
  },
};

export const productService = {
  getAll: async () => {
    const response = await apiClient.get('/products');
    return response.data;
  },
  getById: async (id) => {
    const response = await apiClient.get(`/products/${id}`);
    return response.data;
  },
  search: async (query) => {
    const response = await apiClient.get('/products/search', { params: { q: query } });
    return response.data;
  },
};

export const authService = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token);
    }
    return response.data;
  },
  register: async (email, password, firstName, lastName) => {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('auth_token');
  },
};

export const userService = {
  getProfile: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
  updateProfile: async (userData) => {
    const response = await apiClient.put('/users/me', userData);
    return response.data;
  },
};
