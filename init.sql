-- Initialize DocFlow database
-- Database is created by PostgreSQL environment variables, so we just connect to it

-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'docflow_user') THEN

      CREATE ROLE docflow_user LOGIN PASSWORD 'docflow_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE docflow TO docflow_user;

-- Switch to docflow database for table creation
\c docflow;

-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email and username for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- User creation is handled by the application initialization script
-- This section is intentionally left empty

-- Create other tables
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    inn VARCHAR(12),
    kpp VARCHAR(9),
    address VARCHAR(1000),
    role VARCHAR(20) NOT NULL,
    ogrn VARCHAR(20),
    okpo VARCHAR(10),
    okved VARCHAR(10),
    bank_name VARCHAR(200),
    bank_account VARCHAR(50),
    correspondent_account VARCHAR(50),
    bik VARCHAR(20),
    director_name VARCHAR(200),
    director_position VARCHAR(200),
    acting_basis VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(255),
    legal_address VARCHAR(500),
    postal_address VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_parties_name ON parties(name);
CREATE INDEX IF NOT EXISTS idx_parties_role ON parties(role);

CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    number VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    subject TEXT,
    amount NUMERIC,
    deadline DATE,
    penalties TEXT,
    customer_id INTEGER REFERENCES parties(id),
    contractor_id INTEGER REFERENCES parties(id),
    contract_type VARCHAR(100),
    place_of_conclusion VARCHAR(200),
    work_object_name TEXT,
    work_object_address TEXT,
    cadastral_number VARCHAR(50),
    land_area NUMERIC,
    construction_permit VARCHAR(100),
    permit_date DATE,
    amount_including_vat NUMERIC,
    vat_amount NUMERIC,
    vat_rate NUMERIC,
    retention_percentage NUMERIC,
    payment_terms_days INTEGER,
    work_start_date DATE,
    work_completion_date DATE,
    warranty_period_months INTEGER,
    warranty_start_basis TEXT,
    delay_penalty_first_week NUMERIC,
    delay_penalty_after_week NUMERIC,
    late_payment_penalty NUMERIC,
    document_penalty_amount NUMERIC,
    site_violation_penalty NUMERIC,
    project_documentation TEXT,
    status VARCHAR(50) DEFAULT 'active',
    currency VARCHAR(3) DEFAULT 'RUB',
    force_majeure_clause TEXT,
    dispute_resolution TEXT,
    governing_law TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_contracts_number ON contracts(number);
CREATE INDEX IF NOT EXISTS idx_contracts_date ON contracts(date);
CREATE INDEX IF NOT EXISTS idx_contracts_customer ON contracts(customer_id);
CREATE INDEX IF NOT EXISTS idx_contracts_contractor ON contracts(contractor_id);

CREATE TABLE IF NOT EXISTS contract_documents (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    doc_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contract_documents_contract ON contract_documents(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_documents_type ON contract_documents(doc_type);

CREATE TABLE IF NOT EXISTS document_links (
    id SERIAL PRIMARY KEY,
    parent_document_id INTEGER NOT NULL REFERENCES contract_documents(id),
    child_document_id INTEGER NOT NULL REFERENCES contract_documents(id),
    link_type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS contract_attachments (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    attachment_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    number VARCHAR(100),
    description TEXT,
    file_path VARCHAR(500),
    is_integral_part BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contract_attachments_contract ON contract_attachments(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_attachments_type ON contract_attachments(attachment_type);

CREATE TABLE IF NOT EXISTS contract_penalties (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    penalty_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    penalty_rate NUMERIC,
    penalty_amount NUMERIC,
    period_days INTEGER,
    calculation_basis VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contract_penalties_contract ON contract_penalties(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_penalties_type ON contract_penalties(penalty_type);

CREATE TABLE IF NOT EXISTS contract_milestones (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    milestone_name VARCHAR(200) NOT NULL,
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    status VARCHAR(50) DEFAULT 'planned',
    description TEXT,
    milestone_amount NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contract_milestones_contract ON contract_milestones(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_milestones_status ON contract_milestones(status);

CREATE TABLE IF NOT EXISTS contact_persons (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id),
    party_id INTEGER NOT NULL REFERENCES parties(id),
    name VARCHAR(200) NOT NULL,
    position VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contact_persons_contract ON contact_persons(contract_id);
CREATE INDEX IF NOT EXISTS idx_contact_persons_party ON contact_persons(party_id);

-- Grant table permissions to docflow_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO docflow_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO docflow_user;