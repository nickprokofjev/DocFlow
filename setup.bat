@echo off
echo =================================
echo    DocFlow Setup Script
echo =================================
echo.

echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✅ Python found
    python --version
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+ first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js found
    node --version
)

echo.
echo =================================
echo    Choose Setup Option:
echo =================================
echo 1. Quick Testing Setup (Current - Already Running)
echo 2. Full Development Setup (Database + Frontend)
echo 3. Install OCR Dependencies Only
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto quick_setup
if "%choice%"=="2" goto full_setup
if "%choice%"=="3" goto ocr_setup
if "%choice%"=="4" goto end
goto invalid_choice

:quick_setup
echo.
echo =================================
echo    Quick Testing Setup
echo =================================
echo.
echo ✅ Backend server is already running!
echo.
echo Access your test environment:
echo 🌐 Test Form: http://localhost:8000/test-form
echo 📚 API Docs: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo.
echo What you can test:
echo - Upload PDF/image files for OCR
echo - Fill contract forms
echo - Save contract data
echo - View saved contracts
echo.
echo Data is saved to: backend\test_contracts\
echo.
pause
goto end

:full_setup
echo.
echo =================================
echo    Full Development Setup
echo =================================
echo.

echo Step 1: Setting up backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy asyncpg pydantic alembic
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install pytest pytest-asyncio httpx

echo.
echo Step 2: Setting up frontend...
cd ..\frontend

if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
) else (
    echo Node modules already installed, updating...
    npm update
)

if not exist .env.local (
    echo Creating frontend environment file...
    copy .env.example .env.local
)

echo.
echo ✅ Full setup completed!
echo.
echo To start development:
echo 1. Backend: cd backend && python main.py
echo 2. Frontend: cd frontend && npm run dev
echo.
echo Note: You'll need PostgreSQL for full functionality
echo.
pause
goto end

:ocr_setup
echo.
echo =================================
echo    OCR Dependencies Setup
echo =================================
echo.

cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing OCR dependencies...
pip install Pillow pytesseract pdf2image spacy

echo.
echo Installing spaCy Russian model...
python -m spacy download ru_core_news_lg

echo.
echo Setting up Tesseract OCR for Windows...
if exist setup_windows_ocr.py (
    python setup_windows_ocr.py
) else (
    echo Please install Tesseract manually:
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Install with Russian language pack
    echo 3. Add to PATH: C:\Program Files\Tesseract-OCR
)

echo.
echo ✅ OCR setup completed!
echo.
pause
goto end

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter 1, 2, 3, or 4.
echo.
pause
goto :eof

:end
echo.
echo Thank you for using DocFlow setup!
echo.
pause