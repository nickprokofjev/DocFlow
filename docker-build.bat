@echo off
REM DocFlow Docker Build Script for Windows

echo Building DocFlow Docker images...

REM Build backend
echo Building backend image...
docker build -t docflow-backend ./backend

REM Build frontend
echo Building frontend image...
docker build -t docflow-frontend ./frontend

echo Build completed successfully!
echo.
echo To run the application:
echo   docker-compose up -d
echo.
echo To run in development mode:
echo   docker-compose -f docker-compose.dev.yml up -d

pause