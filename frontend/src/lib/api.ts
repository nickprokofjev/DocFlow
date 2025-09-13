/**
 * API utilities for DocFlow frontend application.
 * 
 * This module provides:
 * - HTTP client configuration with interceptors
 * - Authentication token management
 * - API endpoints for contracts, parties, and documents
 * - Error handling and response transformation
 * - Request/response interceptors for logging and token management
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Types for API responses
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface Party {
  id: number;
  name: string;
  inn?: string;
  kpp?: string;
  address?: string;
  role: 'customer' | 'contractor';
}

export interface Contract {
  id: number;
  number: string;
  date: string;
  subject?: string;
  amount?: number;
  deadline?: string;
  penalties?: string;
  customer_id: number;
  contractor_id: number;
  customer?: Party;
  contractor?: Party;
}

export interface ContractWithParties {
  id: number;
  number: string;
  date: string;
  subject?: string;
  amount?: number;
  deadline?: string;
  penalties?: string;
  customer: Party;
  contractor: Party;
}

export interface ContractDocument {
  id: number;
  contract_id: number;
  doc_type: string;
  file_path: string;
  date?: string;
  description?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface APIError {
  detail: string;
  error_code?: string;
  type?: string;
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
class AuthManager {
  private static readonly TOKEN_KEY = 'token';
  private static readonly USER_KEY = 'user';

  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  static removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  static getUser(): User | null {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  static setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = AuthManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  (error: AxiosError<APIError>) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data);
    }

    // Handle 401 errors by clearing auth and redirecting to login
    if (error.response?.status === 401) {
      AuthManager.removeToken();
      window.location.href = '/login';
    }

    // Enhance error message
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

// Authentication API
export const authAPI = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Store token and user data
    AuthManager.setToken(response.data.access_token);
    AuthManager.setUser(response.data.user);
    
    return response.data;
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    AuthManager.setUser(response.data);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } finally {
      AuthManager.removeToken();
    }
  },

  // Auth utilities
  getToken: () => AuthManager.getToken(),
  getUser: () => AuthManager.getUser(),
  isAuthenticated: () => AuthManager.isAuthenticated(),
  clearAuth: () => AuthManager.removeToken(),
};

// Contracts API
export const contractsAPI = {
  async getAll(params?: { limit?: number }): Promise<Contract[]> {
    const response = await api.get<Contract[]>('/api/contracts/', { params });
    return response.data;
  },

  async getById(id: number): Promise<Contract> {
    const response = await api.get<Contract>(`/api/contracts/${id}`);
    return response.data;
  },

  async upload(contractData: any): Promise<any> {
    const formData = new FormData();
    formData.append('file', contractData.file);
    formData.append('number', contractData.number);
    formData.append('contract_date', contractData.contract_date);
    formData.append('customer_name', contractData.customer_name);
    formData.append('contractor_name', contractData.contractor_name);
    
    if (contractData.subject) formData.append('subject', contractData.subject);
    if (contractData.amount) formData.append('amount', contractData.amount.toString());
    if (contractData.deadline) formData.append('deadline', contractData.deadline);
    if (contractData.penalties) formData.append('penalties', contractData.penalties);

    const response = await api.post('/api/contracts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async create(contractData: FormData): Promise<any> {
    const response = await api.post('/api/contracts/', contractData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async update(id: number, contractData: Partial<Contract>): Promise<Contract> {
    const response = await api.put<Contract>(`/api/contracts/${id}`, contractData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/contracts/${id}`);
  },

  async getDocuments(contractId: number): Promise<ContractDocument[]> {
    const response = await api.get<ContractDocument[]>(`/api/contracts/${contractId}/documents`);
    return response.data;
  },
};

// Parties API
export const partiesAPI = {
  async getAll(params?: { role?: string; limit?: number }): Promise<Party[]> {
    const response = await api.get<Party[]>('/api/parties/', { params });
    return response.data;
  },

  async getById(id: number): Promise<Party> {
    const response = await api.get<Party>(`/api/parties/${id}`);
    return response.data;
  },

  async create(partyData: Omit<Party, 'id'>): Promise<Party> {
    const response = await api.post<Party>('/api/parties/', partyData);
    return response.data;
  },

  async update(id: number, partyData: Partial<Party>): Promise<Party> {
    const response = await api.put<Party>(`/api/parties/${id}`, partyData);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/api/parties/${id}`);
  },
};

// Documents API
export const documentsAPI = {
  async getAll(params?: { skip?: number; limit?: number; doc_type?: string }): Promise<ContractDocument[]> {
    const response = await api.get<ContractDocument[]>('/api/documents/', { params });
    return response.data;
  },

  async getById(id: number): Promise<ContractDocument> {
    const response = await api.get<ContractDocument>(`/api/documents/${id}`);
    return response.data;
  },
};

// Health check API
export const healthAPI = {
  async check(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

// Export the configured axios instance for custom requests
export { api };

// Default export
export default {
  auth: authAPI,
  contracts: contractsAPI,
  parties: partiesAPI,
  documents: documentsAPI,
  health: healthAPI,
  api,
};