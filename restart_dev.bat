@echo off
echo 🚀 Перезапуск DocFlow Development Environment
echo.

echo 📦 Остановка и удаление контейнеров...
docker-compose -f docker-compose.dev.yml down -v

echo 🧹 Очистка Docker volumes...
docker volume prune -f

echo 🏗️ Сборка и запуск контейнеров...
docker-compose -f docker-compose.dev.yml up --build -d

echo.
echo ⏳ Ожидание готовности сервисов...
timeout /t 10 /nobreak > nul

echo.
echo 📋 Статус контейнеров:
docker-compose -f docker-compose.dev.yml ps

echo.
echo 📄 Логи backend (последние 20 строк):
docker-compose -f docker-compose.dev.yml logs --tail=20 backend

echo.
echo ✅ Development окружение готово!
echo 🌐 Frontend: http://localhost:3000
echo 🌐 Backend: http://localhost:8000
echo 📊 Backend Docs: http://localhost:8000/docs
echo 💾 PostgreSQL: localhost:5432
echo 🔴 Redis: localhost:6379
echo.
echo 🔑 Учетные данные admin:
echo    Email: admin@example.com
echo    Password: admin123
echo.
pause