import axios, { AxiosResponse } from 'axios';
import type { User } from '@/types';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: { username: string; password: string }) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response: AxiosResponse<{
      access_token: string;
      token_type: string;
      user: User;
    }> = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
  }) => {
    const response: AxiosResponse<User> = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    await api.post('/auth/logout');
  },
};

// Contracts API
export const contractsAPI = {
  getAll: async (params?: { limit?: number }) => {
    const response = await api.get('/api/contracts', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/contracts/${id}`);
    return response.data;
  },

  create: async (contractData: any) => {
    const response = await api.post('/api/contracts', contractData);
    return response.data;
  },

  update: async (id: number, contractData: any) => {
    const response = await api.put(`/api/contracts/${id}`, contractData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/api/contracts/${id}`);
  },

  uploadDocument: async (contractId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/contracts/${contractId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
};

// Parties API
export const partiesAPI = {
  getAll: async (params?: { limit?: number }) => {
    const response = await api.get('/api/parties', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/parties/${id}`);
    return response.data;
  },

  create: async (partyData: any) => {
    const response = await api.post('/api/parties', partyData);
    return response.data;
  },

  update: async (id: number, partyData: any) => {
    const response = await api.put(`/api/parties/${id}`, partyData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/api/parties/${id}`);
  },
};

// Documents API
export const documentsAPI = {
  getAll: async () => {
    const response = await api.get('/api/documents');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/documents/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  },

  getRecentActivity: async () => {
    const response = await api.get('/api/dashboard/recent');
    return response.data;
  },
};

// Health API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export { api };
export default api;