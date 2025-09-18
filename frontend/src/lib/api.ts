import axios, { AxiosResponse, InternalAxiosRequestConfig } from "axios";

// Base API configuration
const API_BASE_URL = "http://localhost:8000";

console.log("API Base URL:", API_BASE_URL);

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log("API Request:", config);
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: any) => {
    console.error("API Error:", error);
    console.error("API Error Response:", error.response);
    console.error("API Error Request:", error.request);
    console.error("API Error Config:", error.config);

    if (error.response?.status === 401) {
      // Clear auth data on 401
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Don't redirect here, let the component handle it
    }
    return Promise.reject(error);
  }
);

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    username: string;
    is_active: boolean;
    created_at: string;
  };
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

// Auth API
export const authAPI = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Use form data for OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);

    const response = await apiClient.post<LoginResponse>(
      "/auth/login",
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );
    return response.data;
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>("/auth/register", userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post("/auth/logout");
  },
};

// Contracts API
export const contractsAPI = {
  async getAll(params?: { limit?: number }): Promise<any[]> {
    const response = await apiClient.get("/api/v1/contracts", { params });
    return response.data;
  },

  async create(data: any): Promise<any> {
    const response = await apiClient.post("/api/v1/contracts", data);
    return response.data;
  },

  async update(id: number, data: any): Promise<any> {
    const response = await apiClient.put(`/api/v1/contracts/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/contracts/${id}`);
  },

  async upload(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post(
      "/api/v1/contracts/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },
};

// Parties API
export const partiesAPI = {
  async getAll(params?: { role?: string; limit?: number }): Promise<any[]> {
    const response = await apiClient.get("/api/v1/parties", { params });
    return response.data;
  },

  async create(data: any): Promise<any> {
    const response = await apiClient.post("/api/v1/parties", data);
    return response.data;
  },

  async update(id: number, data: any): Promise<any> {
    const response = await apiClient.put(`/api/v1/parties/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/parties/${id}`);
  },
};

// Health API
export const healthAPI = {
  async check(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get("/health");
    return response.data;
  },
};

// Job Status for file uploads
export interface JobStatus {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress?: number;
  result?: any;
  error?: string;
}

export { apiClient };
