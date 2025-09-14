@echo off
echo 🚀 Перезапуск DocFlow Production Environment
echo.

echo 📦 Остановка и удаление контейнеров...
docker-compose down -v

echo 🧹 Очистка Docker volumes...
docker volume prune -f

echo 🏗️ Сборка и запуск контейнеров...
docker-compose up --build -d

echo.
echo ⏳ Ожидание готовности сервисов...
timeout /t 15 /nobreak > nul

echo.
echo 📋 Статус контейнеров:
docker-compose ps

echo.
echo 📄 Логи backend (последние 20 строк):
docker-compose logs --tail=20 backend

echo.
echo 📄 Логи frontend (последние 10 строк):
docker-compose logs --tail=10 frontend

echo.
echo ✅ Production окружение готово!
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
echo ⚠️  ВНИМАНИЕ: Это production окружение!
echo    Смените SECRET_KEY в docker-compose.yml перед использованием!
echo.
pause