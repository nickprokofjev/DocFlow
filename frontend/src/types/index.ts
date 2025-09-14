export interface Party {
  id: number;
  name: string;
  inn?: string;
  kpp?: string;
  address?: string;
  role: 'customer' | 'contractor';
  // Extended fields
  ogrn?: string;
  okpo?: string;
  okved?: string;
  bank_name?: string;
  bank_account?: string;
  correspondent_account?: string;
  bik?: string;
  director_name?: string;
  director_position?: string;
  acting_basis?: string;
  phone?: string;
  email?: string;
  legal_address?: string;
  postal_address?: string;
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
  // Extended fields
  contract_type?: string;
  place_of_conclusion?: string;
  work_object_name?: string;
  work_object_address?: string;
  cadastral_number?: string;
  land_area?: number;
  construction_permit?: string;
  permit_date?: string;
  amount_including_vat?: number;
  vat_amount?: number;
  vat_rate?: number;
  retention_percentage?: number;
  payment_terms_days?: number;
  work_start_date?: string;
  work_completion_date?: string;
  warranty_period_months?: number;
  warranty_start_basis?: string;
  delay_penalty_first_week?: number;
  delay_penalty_after_week?: number;
  late_payment_penalty?: number;
  document_penalty_amount?: number;
  site_violation_penalty?: number;
  project_documentation?: string;
  status?: string;
  currency?: string;
  created_at?: string;
  updated_at?: string;
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
  // Extended fields
  contract_type?: string;
  work_object_name?: string;
  work_object_address?: string;
  cadastral_number?: string;
  construction_permit?: string;
  amount_including_vat?: number;
  vat_rate?: number;
  warranty_period_months?: number;
  status?: string;
}

// New interfaces for extended models
export interface ContractAttachment {
  id: number;
  contract_id: number;
  attachment_type: string;
  title: string;
  number?: string;
  description?: string;
  file_path?: string;
  is_integral_part: boolean;
  created_at: string;
}

export interface ContractPenalty {
  id: number;
  contract_id: number;
  penalty_type: string;
  description: string;
  penalty_rate?: number;
  penalty_amount?: number;
  period_days?: number;
  calculation_basis?: string;
}

export interface ContractMilestone {
  id: number;
  contract_id: number;
  milestone_name: string;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  status: string;
  description?: string;
  milestone_amount?: number;
}

export interface ContactPerson {
  id: number;
  contract_id: number;
  party_id: number;
  name: string;
  position?: string;
  phone?: string;
  email?: string;
  role: string;
  is_primary: boolean;
}