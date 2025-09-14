#!/bin/bash

# Local Development Setup Script for DocFlow
echo "==================================="
echo "   DocFlow Local Development Setup"
echo "==================================="
echo

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if command -v python &> /dev/null; then
    echo "✅ Python found: $(python --version)"
else
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo
echo "Setting up backend..."

# Backend setup
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment (Windows Git Bash)
echo "Activating virtual environment..."
source venv/Scripts/activate

# Install basic dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy asyncpg pydantic alembic
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install pytest pytest-asyncio httpx

# Install OCR dependencies (optional)
echo "Installing OCR dependencies..."
pip install Pillow pytesseract pdf2image spacy

echo
echo "Backend setup completed!"

# Frontend setup
cd ../frontend

echo "Setting up frontend..."

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Updating Node.js dependencies..."
    npm update
fi

# Create environment file
if [ ! -f ".env.local" ]; then
    echo "Creating frontend environment file..."
    cp .env.example .env.local 2>/dev/null || echo "VITE_API_URL=http://localhost:8000" > .env.local
fi

echo
echo "Frontend setup completed!"

echo
echo "==================================="
echo "   Setup Complete! 🎉"
echo "==================================="
echo
echo "To start the application:"
echo
echo "1. Start Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/Scripts/activate"
echo "   python main.py"
echo
echo "2. Start Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo
echo "Access points:"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🧪 Test Form: http://localhost:8000/test-form"
echo
echo "Note: The test form is already available and working!"
echo

read -p "Press Enter to continue..."