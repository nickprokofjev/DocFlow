# DocFlow - Document Management System

DocFlow is a modern, full-featured document management system built with FastAPI and React. The system provides OCR capabilities, NLP analysis, and comprehensive contract management with authentication and security.

## 🚀 Features

### ✅ **Backend (FastAPI)**
- **REST API** with automatic documentation (Swagger/OpenAPI)
- **JWT Authentication** with secure user management
- **OCR Processing** with Tesseract for text extraction
- **NLP Analysis** with spaCy for entity recognition
- **PostgreSQL Database** with SQLAlchemy ORM
- **File Upload and Storage** with validation
- **Full CRUD Operations** for all entities
- **Input Validation** with Pydantic schemas
- **Error Handling** with custom exceptions
- **Test Suite** with pytest
- **Database Migrations** with Alembic

### ✅ **Frontend (React + TypeScript)**
- **Modern React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for responsive design
- **React Query** for efficient data fetching
- **React Hook Form** with Zod validation
- **React Router** for client-side routing
- **Authentication UI** with protected routes
- **Contract Management** with upload and listing
- **Party Management** with CRUD operations
- **Dashboard** with statistics and recent activity

### ✅ **DevOps and Deployment**
- **Docker Containerization** for all services
- **Docker Compose** for easy orchestration
- **Production-ready** configurations
- **Health Checks** for all services
- **Volume Management** for data persistence
- **Nginx** reverse proxy for frontend
- **Development Environment** setup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│                 │
│  • Authentication│    │  • JWT Auth      │    │  • User data    │
│  • File upload   │    │  • OCR/NLP      │    │  • Contracts    │
│  • CRUD UI       │    │  • File storage │    │  • Documents    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **OR** for local development:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 13+
  - Tesseract OCR

## 🚀 Quick Start with Docker

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd DocFlow
```

### 2. Build and run with Docker Compose
```bash
# Production mode
docker-compose up -d

# Or development mode  
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Access the application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Default credentials
- **Email**: admin@example.com
- **Password**: admin123

### 5. Troubleshooting "User Not Found" Issues

If you encounter "User not found" errors when trying to log in:

#### Quick Fix (Windows):
```bash
# Run the demo user creation script
create_demo_user.bat
```

#### Manual Fix:
```bash
# Create demo users manually
python create_demo_user.py

# Or reset admin user
python backend/create_admin.py
```

#### Available Demo Accounts:
- **Admin**: admin@example.com / admin123 (Full access)
- **Demo**: demo@example.com / demo123 (Demo user) 
- **User**: user@example.com / user123 (Regular user)

## 🔧 Настройка среды разработки

### Разработка бэкенда

```bash
cd backend

# Создание виртуальной среды
python -m venv venv
source venv/bin/activate  # На Windows: venv\\Scripts\\activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/docflow"
export SECRET_KEY="your-secret-key"

# Инициализация базы данных
python init_db.py

# Запуск сервера разработки
python start.py
```

### Разработка фронтенда

```bash
cd frontend

# Установка зависимостей
npm install

# Создание файла окружения
cp .env.example .env.local

# Запуск сервера разработки
npm run dev
```

## 📂 Структура проекта

```
DocFlow/
├── backend/                    # FastAPI бэкенд
│   ├── alembic/               # Миграции базы данных
│   ├── uploads/               # Хранение файлов
│   ├── api.py                 # API эндпоинты
│   ├── auth.py                # Логика аутентификации
│   ├── auth_api.py            # Эндпоинты аутентификации
│   ├── models.py              # Модели базы данных
│   ├── schemas.py             # Pydantic схемы
│   ├── db.py                  # Конфигурация базы данных
│   ├── exceptions.py          # Пользовательские исключения
│   ├── ocr_nlp.py             # OCR/NLP обработка
│   ├── main.py                # FastAPI приложение
│   ├── init_db.py             # Инициализация базы данных
│   ├── start.py               # Запуск приложения
│   ├── requirements.txt       # Python зависимости
│   └── Dockerfile             # Контейнер бэкенда
├── frontend/                   # React фронтенд
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/             # Компоненты страниц
│   │   ├── contexts/          # React контексты
│   │   ├── lib/               # Утилиты и API клиент
│   │   ├── types/             # TypeScript типы
│   │   └── App.tsx            # Главное приложение
│   ├── package.json           # Node.js зависимости
│   ├── vite.config.ts         # Конфигурация Vite
│   ├── tailwind.config.js     # Конфигурация Tailwind CSS
│   ├── nginx.conf             # Конфигурация Nginx
│   └── Dockerfile             # Контейнер фронтенда
├── docker-compose.yml         # Продакшен docker compose
├── docker-compose.dev.yml     # Разработка docker compose
├── init.sql                   # Инициализация базы данных
└── README.md                  # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения

#### Бэкенд (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/docflow
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Фронтенд (.env.local)
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=DocFlow
VITE_APP_VERSION=1.0.0
```

## 📊 API Эндпоинты

### Аутентификация
- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/login` - Вход в систему
- `GET /auth/me` - Получить текущего пользователя
- `POST /auth/logout` - Выход из системы

### Стороны
- `GET /api/v1/parties/` - Список сторон
- `POST /api/v1/parties/` - Создать сторону
- `GET /api/v1/parties/{id}` - Получить сторону
- `PUT /api/v1/parties/{id}` - Обновить сторону
- `DELETE /api/v1/parties/{id}` - Удалить сторону

### Договоры
- `GET /api/v1/contracts/` - Список договоров
- `POST /api/v1/contracts/` - Загрузить договор
- `GET /api/v1/contracts/{id}` - Получить договор

### Документы
- `GET /api/v1/documents/` - Список документов
- `GET /api/v1/contracts/{id}/documents` - Получить документы договора

### Система
- `GET /` - Информация об API
- `GET /health` - Проверка состояния

## 🧪 Тестирование

### Тесты бэкенда
```bash
cd backend
pytest
pytest -v                    # Подробный вывод
pytest test_api.py           # Конкретный файл тестов
```

### Тесты фронтенда
```bash
cd frontend
npm test
npm run test:coverage        # С покрытием
```

## 🚀 Развертывание

### Продакшен развертывание

1. **Сборка и развертывание с Docker**:
```bash
docker-compose up -d
```

2. **Переменные окружения**: Обновите продакшен переменные окружения в `docker-compose.yml`

3. **SSL/HTTPS**: Настройте SSL сертификаты и обновите конфигурацию Nginx

4. **Домен**: Обновите CORS origins и API URL для вашего домена

### Соображения масштабирования

- Используйте Redis для хранения сессий в многоэкземплярных развертываниях
- Реализуйте хранение файлов на общих томах или облачном хранилище
- Настройте балансировку нагрузки для нескольких экземпляров бэкенда
- Используйте управляемый сервис PostgreSQL для продакшена

## 🔒 Функции безопасности

- **JWT Аутентификация** с настраиваемым истечением
- **Хеширование паролей** с bcrypt
- **Валидация входных данных** с Pydantic
- **CORS защита** с настраиваемыми источниками
- **Заголовки безопасности** в конфигурации Nginx
- **Валидация загрузки файлов** с ограничениями типа и размера
- **Защита от SQL инъекций** с SQLAlchemy ORM

## 📈 Мониторинг и проверки состояния

- **Эндпоинты проверки состояния** для всех сервисов
- **Docker проверки состояния** с автоматическими перезапусками
- **Логирование** с настраиваемыми уровнями
- **Отслеживание ошибок** со структурированной обработкой исключений

## 🤝 Участие в разработке

1. Сделайте форк репозитория
2. Создайте ветку функции: `git checkout -b feature/amazing-feature`
3. Зафиксируйте изменения: `git commit -m 'Добавить потрясающую функцию'`
4. Отправьте в ветку: `git push origin feature/amazing-feature`
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл LICENSE для деталей.

## 🆘 Устранение неполадок

### Общие проблемы

**Сбой сборки Docker**:
- Убедитесь, что Docker имеет достаточно выделенной памяти (4ГБ+)
- Проверьте, что демон Docker запущен

**Ошибки подключения к базе данных**:
- Проверьте, что PostgreSQL запущен
- Проверьте формат DATABASE_URL
- Убедитесь, что база данных существует

**OCR не работает**:
- Установите Tesseract OCR: `apt-get install tesseract-ocr tesseract-ocr-rus`
- Проверьте, что tesseract находится в PATH

**Фронтенд не загружается**:
- Проверьте API URL в переменных окружения
- Убедитесь, что бэкенд доступен
- Проверьте консоль браузера на ошибки

### Получение помощи

- Проверьте логи: `docker-compose logs [service-name]`
- Проверьте состояние: `curl http://localhost:8000/health`
- Документация API: http://localhost:8000/docs

## 🎯 Дорожная карта

- [ ] Email уведомления для событий договоров
- [ ] Расширенный поиск с фильтрами
- [ ] Версионирование документов
- [ ] Интеграция цифровой подписи
- [ ] Отчетность и аналитика
- [ ] Мультитенантная поддержка
- [ ] Мобильное приложение
- [ ] Интеграция с внешними системами

---

Создано с ❤️ используя FastAPI, React и современные практики разработки.