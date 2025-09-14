@echo off
:start
echo 🚀 DocFlow Environment Manager
echo ==============================
echo.
echo Выберите действие:
echo.
echo 🔧 DEVELOPMENT:
echo   1. Перезапустить dev окружение (restart_dev.bat)
echo   2. Создать admin в dev (fix_admin_dev.bat)
echo.
echo 🚀 PRODUCTION:
echo   3. Перезапустить prod окружение (restart_prod.bat)
echo   4. Создать admin в prod (fix_admin_prod.bat)
echo.
echo 📊 МОНИТОРИНГ:
echo   5. Показать статус всех сервисов (status.bat)
echo.
echo   0. Выход
echo.
set /p choice="Введите номер (0-5): "

if "%choice%"=="1" (
    echo.
    echo 🔧 Запуск development окружения...
    call restart_dev.bat
    goto start
) else if "%choice%"=="2" (
    echo.
    echo 👤 Создание admin в development...
    call fix_admin_dev.bat
    goto start
) else if "%choice%"=="3" (
    echo.
    echo 🚀 Запуск production окружения...
    call restart_prod.bat
    goto start
) else if "%choice%"=="4" (
    echo.
    echo 👤 Создание admin в production...
    call fix_admin_prod.bat
    goto start
) else if "%choice%"=="5" (
    echo.
    echo 📊 Проверка статуса сервисов...
    call status.bat
    goto start
) else if "%choice%"=="0" (
    echo.
    echo 👋 До свидания!
    exit /b 0
) else (
    echo.
    echo ❌ Неверный выбор. Попробуйте снова.
    pause
    goto start
)