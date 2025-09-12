# DocFlow Backend

Backend на FastAPI для хранения и обработки договоров, актов и дополнительных соглашений.

## Возможности

- ✅ Загрузка и хранение документов (PDF, изображения)
- ✅ OCR извлечение текста из документов
- ✅ NLP анализ и извлечение сущностей
- ✅ CRUD операции для сторон, договоров и документов
- ✅ REST API с автодокументацией
- ✅ Валидация данных и обработка ошибок
- ✅ Тестирование

## Структура базы данных

- **parties** - стороны (заказчик, подрядчик)
- **contracts** - договоры  
- **contract_documents** - документы (акты, доп. соглашения)
- **document_links** - связи между документами

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции БД
- **PostgreSQL** - основная БД
- **Pydantic** - валидация данных
- **pytesseract** - OCR распознавание
- **spaCy** - NLP обработка
- **pytest** - тестирование

## Установка и запуск

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте PostgreSQL базу данных и установите переменную окружения:

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql+asyncpg://user:password@localhost/docflow"

# Linux/Mac
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/docflow"
```

### 3. Инициализация базы данных

```bash
python init_db.py
```

### 4. Запуск сервера

```bash
# Простой запуск
python start.py

# Или напрямую через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер будет доступен по адресу: http://localhost:8000

## API Документация

После запуска сервера доступна автодокументация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Основные эндпоинты

### Общие
- `GET /` - информация о сервисе
- `GET /health` - проверка здоровья

### Стороны (Parties)
- `POST /api/v1/parties/` - создать сторону
- `GET /api/v1/parties/` - получить список сторон
- `GET /api/v1/parties/{id}` - получить сторону по ID
- `PUT /api/v1/parties/{id}` - обновить сторону
- `DELETE /api/v1/parties/{id}` - удалить сторону

### Договоры (Contracts)
- `POST /api/v1/contracts/` - загрузить договор с файлом
- `GET /api/v1/contracts/` - получить список договоров
- `GET /api/v1/contracts/{id}` - получить договор по ID

### Документы (Documents)
- `GET /api/v1/contracts/{id}/documents` - документы договора
- `GET /api/v1/documents/` - все документы

## Структура проекта

```
backend/
├── alembic/                 # Миграции БД
│   ├── versions/           # Файлы миграций
│   ├── env.py             # Конфигурация Alembic
│   └── script.py.mako     # Шаблон миграций
├── uploads/                # Загруженные файлы
├── api.py                  # API эндпоинты
├── db.py                   # Подключение к БД
├── exceptions.py           # Кастомные исключения
├── init_db.py             # Инициализация БД
├── main.py                # Главное приложение FastAPI
├── models.py              # SQLAlchemy модели
├── ocr_nlp.py             # OCR и NLP функции
├── schemas.py             # Pydantic схемы
├── start.py               # Скрипт запуска
├── test_api.py            # Тесты API
├── alembic.ini            # Конфигурация Alembic
├── pytest.ini            # Конфигурация pytest
├── requirements.txt       # Зависимости
├── README.md              # Английская документация
└── README.ru.md           # Русская документация (этот файл)
```

## Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск конкретного теста
pytest test_api.py::TestAPI::test_create_party
```

## Разработка

### Добавление новых эндпоинтов

1. Добавьте схемы в `schemas.py`
2. Добавьте модели в `models.py` (если нужно)
3. Добавьте эндпоинты в `api.py`
4. Добавьте тесты в `test_api.py`

### Создание миграций

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание изменений"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## Переменные окружения

- `DATABASE_URL` - URL подключения к PostgreSQL
- `UPLOAD_DIR` - папка для загруженных файлов (по умолчанию: ./uploads)

## Примеры использования

### Создание стороны

```bash
curl -X POST "http://localhost:8000/api/v1/parties/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО Рога и Копыта",
    "inn": "1234567890",
    "role": "customer"
  }'
```

### Загрузка договора

```bash
curl -X POST "http://localhost:8000/api/v1/contracts/" \
  -F "number=001/2024" \
  -F "contract_date=2024-01-15" \
  -F "customer_name=ООО Заказчик" \
  -F "contractor_name=ООО Подрядчик" \
  -F "file=@contract.pdf"
```

## Troubleshooting

### Ошибки подключения к БД

1. Проверьте, что PostgreSQL запущен
2. Проверьте правильность DATABASE_URL
3. Убедитесь, что база данных создана

### Ошибки OCR

1. Установите tesseract: `apt-get install tesseract-ocr` (Linux) или загрузите с официального сайта (Windows)
2. Проверьте путь к tesseract в системе

### Ошибки NLP

1. Убедитесь, что модель spaCy загружена: `python -m spacy download ru_core_news_lg`

## Лицензия

МIT License