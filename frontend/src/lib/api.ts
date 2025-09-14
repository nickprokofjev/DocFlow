import axios, { AxiosResponse } from 'axios';
import type { User } from '@/types';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

console.log('API Base URL:', API_BASE_URL);

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
  console.log('API Request:', config);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response);
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    console.error('API Error Response:', error.response);
    console.error('API Error Request:', error.request);
    console.error('API Error Config:', error.config);
    
    // Only redirect to login for 401 errors that are NOT during login attempts
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Job Status Type
export type JobStatus = {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message: string;
  result?: any;
  error?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
};

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
    const response = await api.get('/api/v1/contracts', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/v1/contracts/${id}`);
    return response.data;
  },

  create: async (contractData: any) => {
    const response = await api.post('/api/v1/contracts', contractData);
    return response.data;
  },

  update: async (id: number, contractData: any) => {
    const response = await api.put(`/api/v1/contracts/${id}`, contractData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/api/v1/contracts/${id}`);
  },

  uploadDocument: async (contractId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/v1/contracts/${contractId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  // Document processing methods
  extractData: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/contracts/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  getJobStatus: async (jobId: string) => {
    const response = await api.get(`/api/v1/jobs/${jobId}/status`);
    return response.data;
  },
  
  cancelJob: async (jobId: string) => {
    const response = await api.post(`/api/v1/jobs/${jobId}/cancel`);
    return response.data;
  },
  
  upload: async (uploadData: any) => {
    const formData = new FormData();
    
    // Add all form fields
    Object.keys(uploadData).forEach(key => {
      if (key === 'file' && uploadData[key]) {
        formData.append(key, uploadData[key]);
      } else if (uploadData[key] !== undefined && uploadData[key] !== null) {
        formData.append(key, uploadData[key].toString());
      }
    });
    
    const response = await api.post('/api/v1/contracts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }
};

// Parties API
export const partiesAPI = {
  getAll: async (params?: { limit?: number }) => {
    const response = await api.get('/api/v1/parties', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/v1/parties/${id}`);
    return response.data;
  },

  create: async (partyData: any) => {
    const response = await api.post('/api/v1/parties', partyData);
    return response.data;
  },

  update: async (id: number, partyData: any) => {
    const response = await api.put(`/api/v1/parties/${id}`, partyData);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/api/v1/parties/${id}`);
  },
};

// Documents API
export const documentsAPI = {
  getAll: async () => {
    const response = await api.get('/api/v1/documents');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/api/v1/documents/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/api/v1/dashboard/stats');
    return response.data;
  },

  getRecentActivity: async () => {
    const response = await api.get('/api/v1/dashboard/recent');
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