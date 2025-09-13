"""
Модуль OCR и NLP обработки для системы DocFlow.

Обеспечивает функциональность:
- OCR (Оптическое распознавание символов) для извлечения текста из PDF и изображений
- NLP (Обработка естественного языка) для извлечения сущностей из текста

Используемые библиотеки:
- Tesseract OCR для распознавания текста на русском языке
- spaCy с русской моделью для анализа сущностей
- pdf2image для конвертации PDF в изображения
- PIL (Pillow) для обработки изображений
"""
import logging
import platform
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    import spacy
    OCR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"OCR/NLP dependencies not available: {e}")
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None
    convert_from_path = None
    spacy = None
import os
from typing import Dict, Union, List

# Настройка логгирования для OCR/NLP
logger = logging.getLogger(__name__)

# Configure Tesseract path for Windows
TESSERACT_PATH = None
if platform.system() == "Windows" and OCR_AVAILABLE and pytesseract:
    # Common Tesseract installation paths on Windows
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe",
        os.path.join(os.path.expanduser("~"), "Tesseract-OCR", "tesseract.exe")
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            TESSERACT_PATH = path
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"Tesseract найден и настроен: {path}")
            break
    
    if not TESSERACT_PATH:
        logger.warning("Tesseract не найден в стандартных путях Windows")

# Configure Poppler path for Windows
POPPLER_PATH = None
if platform.system() == "Windows":
    # Common Poppler installation paths on Windows
    possible_paths = [
        r"C:\poppler\Library\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\poppler\bin",
        os.path.join(os.path.expanduser("~"), "poppler", "bin")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            POPPLER_PATH = path
            break

def check_tesseract_availability() -> bool:
    """
    Проверяет доступность Tesseract OCR.
    Возвращает True, если Tesseract доступен, иначе False.
    """
    if not OCR_AVAILABLE or not pytesseract:
        return False
    
    try:
        # Попытка получить версию Tesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract доступен, версия: {version}")
        return True
    except Exception as e:
        logger.warning(f"Tesseract недоступен: {e}")
        return False

# Загрузка русской модели spaCy
nlp = None
if OCR_AVAILABLE and spacy:
    try:
        nlp = spacy.load("ru_core_news_lg")
        logger.info("spaCy модель ru_core_news_lg успешно загружена")
    except OSError:
        try:
            from spacy.cli.download import download
            logger.info("spaCy модель не найдена, скачиваем...")
            download("ru_core_news_lg")
            nlp = spacy.load("ru_core_news_lg")
            logger.info("spaCy модель ru_core_news_lg успешно скачана и загружена")
        except Exception as e:
            logger.error(f"Не удалось загрузить spaCy модель: {e}")
            nlp = None

# Проверка доступности Tesseract при инициализации
if OCR_AVAILABLE:
    TESSERACT_AVAILABLE = check_tesseract_availability()
else:
    TESSERACT_AVAILABLE = False

def extract_text_from_file(file_path: str) -> str:
    """
    Извлекает текст из файла (PDF или изображения) с помощью OCR.
    Возвращает распознанный текст или сообщение об ошибке.
    """
    if not OCR_AVAILABLE or not pytesseract or not Image or not convert_from_path:
        logger.warning("Библиотеки OCR не установлены. Установите pytesseract, Pillow, pdf2image")
        return "Ошибка: OCR недоступен"
    
    if not TESSERACT_AVAILABLE:
        logger.warning("Программа Tesseract OCR не найдена или недоступна")
        if platform.system() == "Windows":
            return ("Ошибка: Tesseract не найден\n\n"
                   "Решение для Windows:\n"
                   "1. Скачайте и установите Tesseract OCR\n"
                   "2. Ссылка: https://github.com/UB-Mannheim/tesseract/wiki\n"
                   "3. Обязательно выберите русский языковой пакет при установке")
        else:
            return "Ошибка: Tesseract OCR недоступен"

    if not file_path:
        logger.error("Путь к файлу не указан (None или пустая строка)")
        return "Ошибка: путь к файлу отсутствует"

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return "Ошибка: файл не найден"

    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"Начало OCR для файла: {file_path}")

    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="rus")

        elif ext == ".pdf":
            # Use Poppler path if specified for Windows
            if POPPLER_PATH:
                logger.info(f"Используется Poppler из: {POPPLER_PATH}")
                images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
            else:
                images = convert_from_path(file_path)
            if not images:
                logger.error("PDF не содержит страниц или не удалось конвертировать")
                return "Ошибка: пустой PDF"
            text = "\n".join([pytesseract.image_to_string(img, lang="rus") for img in images])

        else:
            logger.warning(f"Неподдерживаемый формат файла: {ext}")
            return "Ошибка: неподдерживаемый формат"

        logger.info(f"OCR завершён, длина текста: {len(text)} символов")
        return text

    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Ошибка при OCR: {e}")
        
        # Provide specific help for common Poppler errors
        if "poppler" in error_msg.lower() or "page count" in error_msg.lower():
            if platform.system() == "Windows":
                return (f"Ошибка OCR: {e}\n\n"
                       "Решение для Windows:\n"
                       "1. Запустите setup_windows_ocr.bat для автоматической установки\n"
                       "2. Или скачайте Poppler: https://github.com/oschwartz10612/poppler-windows/releases\n"
                       "3. Добавьте путь к Poppler в переменную PATH")
            else:
                return (f"Ошибка OCR: {e}\n\n"
                       "Решение: установите poppler-utils:\n"
                       "Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                       "macOS: brew install poppler")
        
        # Provide specific help for common Tesseract errors
        if "tesseract" in error_msg.lower() or "not installed" in error_msg.lower() or "PATH" in error_msg:
            if platform.system() == "Windows":
                return (f"Ошибка OCR: {e}\n\n"
                       "Решение для Windows:\n"
                       "1. Скачайте Tesseract: https://github.com/UB-Mannheim/tesseract/wiki\n"
                       "2. Установите с русским языковым пакетом\n"
                       "3. Добавьте путь к Tesseract в переменную PATH\n"
                       "4. Или установите в стандартный путь: C:\\Program Files\\Tesseract-OCR\\")
            else:
                return (f"Ошибка OCR: {e}\n\n"
                       "Решение: установите tesseract:\n"
                       "Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-rus\n"
                       "macOS: brew install tesseract")
        
        return f"Ошибка OCR: {e}"

def extract_contract_entities(text: str) -> Union[Dict[str, List[str]], Dict[str, str]]:
    """
    Извлекает сущности из текста договора с помощью spaCy (организации, даты, суммы, лица).
    Возвращает словарь найденных сущностей или сообщение об ошибке.
    """
    if not OCR_AVAILABLE or not spacy or not nlp:
        logger.warning("Библиотека spaCy не установлена или модель не загружена")
        return {"error": "NLP недоступен"}

    if not text or not text.strip():
        logger.warning("Передан пустой текст для NLP")
        return {"error": "Текст пустой"}

    logger.info("Начало NLP-извлечения сущностей из текста")
    try:
        doc = nlp(text)
        entities: Dict[str, List[str]] = {"ORG": [], "DATE": [], "MONEY": [], "PERSON": []}
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        logger.info(f"NLP завершён, найдено: {entities}")
        return entities
    except Exception as e:
        logger.exception(f"Ошибка NLP: {e}")
        return {"error": f"Ошибка NLP: {e}"}
