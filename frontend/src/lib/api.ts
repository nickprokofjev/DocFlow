import axios, { AxiosResponse } from 'axios';
import type {
  Party,
  Contract,
  ContractDocument,
  CreatePartyRequest,
  UploadContractRequest,
  User,
} from '@/types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email: string, password: string): Promise<{ access_token: string; user: User }> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
  }): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  me: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Parties API
export const partiesAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    role?: string;
  }): Promise<Party[]> => {
    const response = await api.get('/parties/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Party> => {
    const response = await api.get(`/parties/${id}`);
    return response.data;
  },

  create: async (data: CreatePartyRequest): Promise<Party> => {
    const response = await api.post('/parties/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CreatePartyRequest>): Promise<Party> => {
    const response = await api.put(`/parties/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/parties/${id}`);
  },
};

// Contracts API
export const contractsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<Contract[]> => {
    const response = await api.get('/contracts/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Contract> => {
    const response = await api.get(`/contracts/${id}`);
    return response.data;
  },

  upload: async (data: UploadContractRequest): Promise<{
    contract_id: number;
    file: string;
    ocr_text: string;
    entities: any;
  }> => {
    const formData = new FormData();
    formData.append('number', data.number);
    formData.append('contract_date', data.contract_date);
    formData.append('customer_name', data.customer_name);
    formData.append('contractor_name', data.contractor_name);
    formData.append('file', data.file);
    
    if (data.subject) formData.append('subject', data.subject);
    if (data.amount) formData.append('amount', data.amount.toString());
    if (data.deadline) formData.append('deadline', data.deadline);
    if (data.penalties) formData.append('penalties', data.penalties);

    const response = await api.post('/contracts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  getByContract: async (contractId: number): Promise<ContractDocument[]> => {
    const response = await api.get(`/contracts/${contractId}/documents`);
    return response.data;
  },

  getAll: async (params?: {
    skip?: number;
    limit?: number;
    doc_type?: string;
  }): Promise<ContractDocument[]> => {
    const response = await api.get('/documents/', { params });
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async (): Promise<{ status: string; database: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;