# 🚀 DocFlow Complete Setup Guide

## Prerequisites ✅

You have:
- ✅ Python 3.13.7 (Perfect!)
- ✅ Node.js v22.19.0 (Perfect!)
- ❌ Docker (Not installed - we'll use local development)

## 📋 Setup Options

Choose your preferred setup method:

### Option A: Quick Testing Setup (Recommended for testing)
**Current Status**: ✅ Already Running!
- Backend server is running on http://localhost:8000
- Test form available at http://localhost:8000/test-form
- No database needed, saves to JSON files

### Option B: Full Development Setup (For development work)
**Includes**: Database, authentication, full frontend

---

## 🎯 Option A: Quick Testing (Current Setup)

**Status**: ✅ **ALREADY RUNNING**

Your backend server is currently running and ready for testing:

### Access Points:
- **Main Test Form**: http://localhost:8000/test-form
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### What You Can Test:
1. Upload PDF/image files for OCR processing
2. Fill contract forms manually or auto-fill from OCR
3. Save contract data to JSON files
4. View saved contracts list
5. View contract details

### Test Files Location:
- Saved contracts: `backend/test_contracts/`
- Each contract saved as JSON file

---

## 🔧 Option B: Full Development Setup

If you want the complete system with database and frontend:

### Step 1: Backend Setup
```powershell
# 1. Navigate to backend
cd backend

# 2. Create virtual environment (if not exists)
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install core dependencies
pip install fastapi uvicorn sqlalchemy asyncpg pydantic alembic

# 5. Install authentication dependencies
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# 6. Install OCR/NLP dependencies (optional, for document processing)
pip install Pillow pytesseract pdf2image spacy

# 7. Install testing dependencies
pip install pytest pytest-asyncio httpx
```

### Step 2: External Tools Setup (Windows)

#### A. Tesseract OCR (for document text extraction)
```powershell
# Option 1: Run our setup script
.\setup_windows_ocr.bat

# Option 2: Manual installation
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install with Russian language pack
# Add to PATH: C:\Program Files\Tesseract-OCR
```

#### B. PostgreSQL Database (for full functionality)
```powershell
# Download and install PostgreSQL 13+
# Create database: docflow
# Set connection string in environment
```

### Step 3: Environment Configuration
```powershell
# Create .env file in backend directory
DATABASE_URL=postgresql+asyncpg://user:password@localhost/docflow
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 4: Database Initialization
```powershell
# Initialize database
python init_db.py

# Run migrations
alembic upgrade head
```

### Step 5: Frontend Setup
```powershell
# Navigate to frontend
cd ..\frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env.local

# Start development server
npm run dev
```

### Step 6: Access Full Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🧪 Recommended: Start with Option A

Since your backend is already running successfully, I recommend starting with **Option A** to test the functionality:

### Immediate Next Steps:
1. **Open the test form**: http://localhost:8000/test-form
2. **Click "Fill with test data"** to populate the form
3. **Click "Save contract"** to test saving
4. **Check the results** in the "Saved contracts" section

### Why Start Here:
- ✅ No additional setup required
- ✅ Test all core functionality immediately
- ✅ See OCR/NLP processing in action
- ✅ Understand the data structure
- ✅ Verify everything works before full setup

---

## 🎯 Current Recommendation

**Start testing now with Option A**, then move to Option B if you need:
- User authentication
- Database persistence
- Frontend UI
- Production deployment

**Your backend server is ready - click the preview button above or visit:**
**http://localhost:8000/test-form**

Would you like to:
1. Start testing with the current setup (Option A)?
2. Proceed with full development setup (Option B)?
3. Focus on specific components (OCR, database, frontend)?