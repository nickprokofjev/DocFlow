@echo off
echo 🔑 Создание admin пользователя в development окружении
echo.

echo 📦 Проверка статуса контейнеров...
docker-compose -f docker-compose.dev.yml ps

echo.
echo 👤 Создание admin пользователя...
docker-compose -f docker-compose.dev.yml exec backend python create_admin.py

echo.
echo ✅ Готово! Теперь вы можете войти с помощью:
echo    Email: admin@example.com
echo    Password: admin123
echo.
pause