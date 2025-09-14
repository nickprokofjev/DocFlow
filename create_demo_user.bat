@echo off
echo ==========================================
echo      DOCFLOW DEMO USER SETUP
echo ==========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo.
echo Setting up demo users for DocFlow...
echo.

REM Set database URL if not already set
if not defined DATABASE_URL (
    echo Setting default DATABASE_URL...
    set DATABASE_URL=postgresql+asyncpg://docflow_user:docflow_password@localhost/docflow
)

echo Current DATABASE_URL: %DATABASE_URL%
echo.

echo Running demo user creation script...
python create_demo_user.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create demo users
    echo.
    echo Possible solutions:
    echo 1. Make sure PostgreSQL is running
    echo 2. Check DATABASE_URL environment variable
    echo 3. Run: docker-compose up -d db
    echo 4. Or run: python backend/init_db.py
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    DEMO USERS CREATED SUCCESSFULLY!
echo ==========================================
echo.
echo You can now log in to DocFlow using:
echo - admin@example.com / admin123 (Administrator)
echo - demo@example.com / demo123   (Demo user)
echo - user@example.com / user123   (Regular user)
echo.
pause