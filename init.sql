-- Initialize DocFlow database
CREATE DATABASE IF NOT EXISTS docflow;

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