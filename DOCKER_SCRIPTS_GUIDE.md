# 🚀 DocFlow Management Scripts

Удобные batch-скрипты для управления DocFlow в различных окружениях.

## 📋 Доступные скрипты

### 🔧 Development Environment

#### `restart_dev.bat`
Полный перезапуск development окружения:
- Останавливает и удаляет все контейнеры
- Очищает Docker volumes  
- Пересобирает и запускает все сервисы
- Автоматически создает admin пользователя

**Что включает:**
- PostgreSQL с инициализацией данных
- FastAPI Backend с hot reload
- React Frontend с hot reload (Vite)
- Redis для кэширования

**URLs:**
- Frontend: http://localhost:3000 (hot reload)
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### `fix_admin_dev.bat`
Быстрое создание admin пользователя без перезапуска:
```cmd
fix_admin_dev.bat
```

### 🚀 Production Environment

#### `restart_prod.bat`
Полный перезапуск production окружения:
- Останавливает и удаляет все контейнеры
- Очищает Docker volumes
- Пересобирает и запускает все сервисы
- Использует оптимизированные production сборки

**Что включает:**
- PostgreSQL с инициализацией данных
- FastAPI Backend (production mode)
- React Frontend (статичные файлы через Nginx)
- Redis для кэширования

**URLs:**
- Frontend: http://localhost:3000 (production build)
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### `fix_admin_prod.bat`
Создание admin пользователя в production:
```cmd
fix_admin_prod.bat
```

### 📊 Monitoring & Status

#### `status.bat`
Показывает статус всех сервисов:
- Список всех контейнеров (dev и prod)
- Последние логи каждого сервиса
- URLs для доступа к сервисам

```cmd
status.bat
```

## 🔑 Учетные данные по умолчанию

**Admin пользователь:**
- Email: `admin@example.com`
- Password: `admin123`

**База данных:**
- Host: `localhost:5432`
- Database: `docflow`
- User: `docflow_user`
- Password: `docflow_password`

## 🔧 Различия между Development и Production

### Development Mode:
- ✅ Hot reload для frontend и backend
- ✅ Volumes для live code editing
- ✅ Подробные логи
- ✅ Быстрый перезапуск
- ⚠️ Не оптимизировано для производительности

### Production Mode:
- ✅ Оптимизированные builds
- ✅ Минимизированные файлы
- ✅ Health checks
- ✅ Готово к production использованию
- ⚠️ Требует смены SECRET_KEY

## 🚨 Безопасность в Production

**ОБЯЗАТЕЛЬНО смените следующие параметры:**

1. **SECRET_KEY** в `docker-compose.yml`:
```yaml
SECRET_KEY: your-super-secret-key-change-in-production
```

2. **Пароль admin пользователя** после первого входа

3. **Пароли базы данных** для production использования

## 📝 Примеры использования

### Первый запуск (Development):
```cmd
restart_dev.bat
```

### Первый запуск (Production):
```cmd
restart_prod.bat
```

### Проверка статуса:
```cmd
status.bat
```

### Исправление проблем с admin:
```cmd
# Development
fix_admin_dev.bat

# Production  
fix_admin_prod.bat
```

### Ручное управление:
```cmd
# Development
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml down

# Production
docker-compose up -d
docker-compose down
```

## 🔧 Troubleshooting

### Проблема: Контейнеры не запускаются
**Решение:** Убедитесь что Docker Desktop запущен и используйте `restart_*.bat`

### Проблема: Нет admin пользователя
**Решение:** Используйте `fix_admin_*.bat` скрипты

### Проблема: Frontend не загружается
**Решение:** Проверьте статус контейнеров через `status.bat`

### Проблема: База данных недоступна
**Решение:** Полный перезапуск через `restart_*.bat`