#!/bin/bash
# Docker initialization script
# This script is run during container startup to ensure proper initialization

echo "Starting DocFlow Docker initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U docflow_user; do
  echo "PostgreSQL is not ready yet, waiting..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Run database initialization
echo "Running database initialization..."
python init_db_docker.py

echo "Docker initialization completed!"

# Start the main application
echo "Starting DocFlow application..."
exec python start.py