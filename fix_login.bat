@echo off
echo ===================================================
echo DocFlow Admin User Creation Script
echo ===================================================
echo.

echo Step 1: Copying admin creation script to container...
docker cp backend\create_admin.py docflow_backend:/app/create_admin.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy script to container
    pause
    exit /b 1
)
echo ✓ Script copied successfully

echo.
echo Step 2: Running admin user creation...
docker exec docflow_backend python create_admin.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to create admin user
    echo Trying alternative method...
    echo.
    echo Step 2b: Running database initialization...
    docker exec docflow_backend python init_db.py
    if %errorlevel% neq 0 (
        echo ERROR: Database initialization also failed
        echo Please check Docker container status
        pause
        exit /b 1
    )
)

echo.
echo ✓ Admin user creation completed!
echo.
echo ===================================================
echo You can now login with:
echo Email: admin@example.com
echo Password: admin123
echo ===================================================
echo.
echo Press any key to check container logs...
pause > nul

echo.
echo Recent backend logs:
docker logs --tail 20 docflow_backend

echo.
echo Script completed. Please try logging in now.
pause