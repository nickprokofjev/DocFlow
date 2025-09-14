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

import { 
  Contract, 
  ContractWithParties, 
  Party, 
  User, 
  UploadContractRequest,
  CreatePartyRequest,
  APIResponse,
  PaginatedResponse 
} from '@/types';

// Base API URL - will be resolved by Vite proxy in development
const API_BASE_URL = '/api/v1';
const AUTH_BASE_URL = '/auth';

// Helper function to get auth headers
function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Generic fetch wrapper with error handling
async function apiRequest<T>(
  url: string, 
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// File upload wrapper
async function uploadRequest<T>(
  url: string,
  formData: FormData
): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Authentication API
export const authAPI = {
  login: async (credentials: { username: string; password: string }): Promise<{ access_token: string; user: User }> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await fetch(`${AUTH_BASE_URL}/login`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.message || 'Login failed');
    }
    
    return response.json();
  },

  getCurrentUser: async (): Promise<User> => {
    return apiRequest(`${AUTH_BASE_URL}/me`);
  },

  register: async (userData: { email: string; username: string; password: string }): Promise<User> => {
    return apiRequest(`${AUTH_BASE_URL}/register`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  logout: async (): Promise<void> => {
    await apiRequest(`${AUTH_BASE_URL}/logout`, {
      method: 'POST',
    });
  },
};

// Contracts API
export const contractsAPI = {
  getAll: async (params?: { limit?: number; offset?: number }): Promise<ContractWithParties[]> => {
    const queryString = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    return apiRequest(`${API_BASE_URL}/contracts/${queryString}`);
  },

  getAllPaginated: async (params?: { limit?: number; offset?: number }): Promise<PaginatedResponse<ContractWithParties>> => {
    const queryString = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await apiRequest<ContractWithParties[]>(`${API_BASE_URL}/contracts/${queryString}`);
    // For now, create a mock paginated response since backend doesn't return pagination metadata
    // TODO: Update backend to return proper pagination metadata
    return {
      items: response,
      total: response.length,
      page: Math.floor((params?.offset || 0) / (params?.limit || 100)) + 1,
      size: params?.limit || 100,
      pages: Math.ceil(response.length / (params?.limit || 100))
    };
  },

  getById: async (id: number): Promise<ContractWithParties> => {
    return apiRequest(`${API_BASE_URL}/contracts/${id}`);
  },

  upload: async (contractData: UploadContractRequest): Promise<APIResponse<Contract>> => {
    const formData = new FormData();
    
    // Add all contract fields to FormData
    Object.entries(contractData).forEach(([key, value]) => {
      if (value !== undefined && value !== null && key !== 'file') {
        formData.append(key, value.toString());
      }
    });
    
    if (contractData.file) {
      formData.append('file', contractData.file);
    }
    
    return uploadRequest(`${API_BASE_URL}/contracts/`, formData);
  },

  delete: async (id: number): Promise<void> => {
    await apiRequest(`${API_BASE_URL}/contracts/${id}`, {
      method: 'DELETE',
    });
  },

  update: async (id: number, contractData: Partial<Contract>): Promise<Contract> => {
    return apiRequest(`${API_BASE_URL}/contracts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contractData),
    });
  },
};

// Parties API
export const partiesAPI = {
  getAll: async (params?: { limit?: number; offset?: number; role?: string }): Promise<Party[]> => {
    const queryString = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    return apiRequest(`${API_BASE_URL}/parties/${queryString}`);
  },

  getAllPaginated: async (params?: { limit?: number; offset?: number }): Promise<PaginatedResponse<Party>> => {
    const queryString = params ? `?${new URLSearchParams(params as any).toString()}` : '';
    const response = await apiRequest<Party[]>(`${API_BASE_URL}/parties/${queryString}`);
    // For now, create a mock paginated response since backend doesn't return pagination metadata
    // TODO: Update backend to return proper pagination metadata
    return {
      items: response,
      total: response.length,
      page: Math.floor((params?.offset || 0) / (params?.limit || 100)) + 1,
      size: params?.limit || 100,
      pages: Math.ceil(response.length / (params?.limit || 100))
    };
  },

  getById: async (id: number): Promise<Party> => {
    return apiRequest(`${API_BASE_URL}/parties/${id}`);
  },

  create: async (partyData: CreatePartyRequest): Promise<Party> => {
    return apiRequest(`${API_BASE_URL}/parties/`, {
      method: 'POST',
      body: JSON.stringify(partyData),
    });
  },

  update: async (id: number, partyData: Partial<Party>): Promise<Party> => {
    return apiRequest(`${API_BASE_URL}/parties/${id}`, {
      method: 'PUT',
      body: JSON.stringify(partyData),
    });
  },

  delete: async (id: number): Promise<void> => {
    await apiRequest(`${API_BASE_URL}/parties/${id}`, {
      method: 'DELETE',
    });
  },
};

// Health API
export const healthAPI = {
  check: async (): Promise<{ status: string; timestamp: string }> => {
    return apiRequest('/health');
  },
};

// Documents API
export const documentsAPI = {
  getAll: async (): Promise<any[]> => {
    return apiRequest(`${API_BASE_URL}/documents/`);
  },

  getByContractId: async (contractId: number): Promise<any[]> => {
    return apiRequest(`${API_BASE_URL}/contracts/${contractId}/documents`);
  },
};
