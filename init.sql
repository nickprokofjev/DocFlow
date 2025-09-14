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

-- Insert default admin user if not exists
-- Password hash for "admin123" using bcrypt
INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
SELECT 
    'admin@example.com',
    'admin', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- admin123
    true,
    true
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@example.com' OR username = 'admin'
);

-- Grant table permissions to docflow_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO docflow_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO docflow_user;