import apiClient from './api';

export const healthCheckService = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export const productService = {
  // Backend: GET /api/products?page=&page_size=&category_id=&search=
  getAll: async ({ categoryId, search, page = 1, pageSize = 50 } = {}) => {
    const params = { page, page_size: pageSize };
    if (categoryId) params.category_id = categoryId;
    if (search) params.search = search;
    const response = await apiClient.get('/products', { params });
    return response.data; // { products, total, page, page_size }
  },
  // Backend: GET /api/products/{id}
  getById: async (id) => {
    const response = await apiClient.get(`/products/${id}`);
    return response.data;
  },
};

export const categoryService = {
  // Backend: GET /api/categories
  getAll: async () => {
    const response = await apiClient.get('/categories');
    return response.data; // [{ category_id, category_name, description, ... }]
  },
};

export const profileService = {
  // Backend: GET/PUT/DELETE /api/profile
  get: async () => {
    const response = await apiClient.get('/profile');
    return response.data;
  },
  update: async (data) => {
    const response = await apiClient.put('/profile', data);
    return response.data;
  },
  remove: async () => {
    await apiClient.delete('/profile');
    return true;
  },
};

export const addressService = {
  // Backend: GET/POST /api/addresses and PUT/DELETE /api/addresses/{id}
  getAll: async () => {
    const response = await apiClient.get('/addresses');
    return response.data;
  },
  create: async (data) => {
    const response = await apiClient.post('/addresses', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await apiClient.put(`/addresses/${id}`, data);
    return response.data;
  },
  remove: async (id) => {
    await apiClient.delete(`/addresses/${id}`);
    return true;
  },
  setDefault: async (id) => {
    const response = await apiClient.put(`/addresses/${id}`, { is_default: true });
    return response.data;
  },
};
