# DocFlow Setup Commands - Git Bash Version

## 🚀 Setup DocFlow using Git Bash (MINGW64)

### Option 1: Run the automated script
```bash
# Make the script executable
chmod +x setup-local.sh

# Run the setup
./setup-local.sh
```

### Option 2: Manual setup (step by step)

#### Backend Setup:
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy asyncpg pydantic
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install pytest pytest-asyncio httpx

# Start backend server
python main.py
```

#### Frontend Setup (in new terminal):
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file (if not exists)
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start frontend server
npm run dev
```

### Option 3: Using PowerShell (Windows specific)

#### Backend:
```powershell
# Navigate and setup backend
Set-Location backend
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy asyncpg pydantic
python main.py
```

#### Frontend (new PowerShell window):
```powershell
# Navigate and setup frontend  
Set-Location frontend
npm install
npm run dev
```

## 🎯 Current Status

✅ **Backend**: Already running at http://localhost:8000
✅ **Test Form**: Available at http://localhost:8000/test-form
⏳ **Frontend**: Needs npm install and npm run dev

## 🔍 Quick Check Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend dependencies are installed
ls frontend/node_modules

# Check current directory
pwd
```

## 🚀 Fastest Way to Get Running

**Since your backend is already working, just run:**

```bash
# In Git Bash from DocFlow root directory:
cd frontend
npm install
npm run dev
```

**Then access:**
- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000
- Test Form: http://localhost:8000/test-form