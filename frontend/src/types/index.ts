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
}

export interface ContractWithParties extends Contract {
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

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ErrorResponse {
  success: boolean;
  message: string;
  error_code?: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreatePartyRequest {
  name: string;
  inn?: string;
  kpp?: string;
  address?: string;
  role: 'customer' | 'contractor';
}

export interface UploadContractRequest {
  number: string;
  contract_date: string;
  subject?: string;
  amount?: number;
  deadline?: string;
  penalties?: string;
  customer_name: string;
  contractor_name: string;
  file: File;
}