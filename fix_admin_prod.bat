@echo off
echo 🔑 Создание admin пользователя в production окружении
echo.

echo 📦 Проверка статуса контейнеров...
docker-compose ps

echo.
echo 👤 Создание admin пользователя...
docker-compose exec backend python create_admin.py

echo.
echo ✅ Готово! Теперь вы можете войти с помощью:
echo    Email: admin@example.com
echo    Password: admin123
echo.
echo ⚠️  ВНИМАНИЕ: Это production окружение!
echo    Рекомендуется сменить пароль после первого входа!
echo.
pause