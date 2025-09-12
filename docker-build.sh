#!/bin/bash

# DocFlow Docker Build Script
echo "Building DocFlow Docker images..."

# Build backend
echo "Building backend image..."
docker build -t docflow-backend ./backend

# Build frontend
echo "Building frontend image..."
docker build -t docflow-frontend ./frontend

echo "Build completed successfully!"
echo ""
echo "To run the application:"
echo "  docker-compose up -d"
echo ""
echo "To run in development mode:"
echo "  docker-compose -f docker-compose.dev.yml up -d"