@echo off
echo 📊 DocFlow Services Status
echo.

echo 🔧 DEVELOPMENT ENVIRONMENT:
echo ================================
docker-compose -f docker-compose.dev.yml ps
echo.

echo 🚀 PRODUCTION ENVIRONMENT:
echo ==============================
docker-compose ps
echo.

echo 📄 RECENT LOGS (Development):
echo =============================
echo Backend (last 5 lines):
docker-compose -f docker-compose.dev.yml logs --tail=5 backend 2>nul
echo.
echo Frontend (last 5 lines):
docker-compose -f docker-compose.dev.yml logs --tail=5 frontend 2>nul
echo.

echo 📄 RECENT LOGS (Production):
echo ============================
echo Backend (last 5 lines):
docker-compose logs --tail=5 backend 2>nul
echo.
echo Frontend (last 5 lines):
docker-compose logs --tail=5 frontend 2>nul
echo.

echo 🔗 SERVICES URLs:
echo =================
echo Development:
echo   🌐 Frontend: http://localhost:3000
echo   🌐 Backend:  http://localhost:8000
echo   📊 API Docs: http://localhost:8000/docs
echo.
echo Production:
echo   🌐 Frontend: http://localhost:3000
echo   🌐 Backend:  http://localhost:8000  
echo   📊 API Docs: http://localhost:8000/docs
echo.
pause