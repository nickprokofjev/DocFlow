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

def extract_contract_entities(text: str) -> Union[Dict[str, Union[List[str], List[Dict[str, str]], str, int, None]], Dict[str, str]]:
    """
    Извлекает сущности из текста договора с помощью spaCy и регулярных выражений.
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
        entities: Dict[str, Union[List[str], List[Dict[str, str]], str, int, None]] = {"ORG": [], "DATE": [], "MONEY": [], "PERSON": []}
        for ent in doc.ents:
            if ent.label_ in entities and isinstance(entities[ent.label_], list):
                entities[ent.label_].append(ent.text)  # type: ignore
        
        # Теперь извлекаем специфические поля для договора
        contract_data = extract_detailed_contract_fields(text)
        entities.update(contract_data)
        
        logger.info(f"NLP завершён, найдено: {entities}")
        return entities
    except Exception as e:
        logger.exception(f"Ошибка NLP: {e}")
        return {"error": f"Ошибка NLP: {e}"}

def extract_detailed_contract_fields(text: str) -> Dict[str, Union[str, List[Dict[str, str]], None]]:
    """
    Извлекает детальные поля договора из текста с помощью улучшенных регулярных выражений.
    Учитывает российскую строительную специфику и различные форматы данных.
    Поддерживает физических лиц, ИП, различные форматы дат и российские строительные термины.
    """
    import re
    from datetime import datetime
    
    result = {}
    
    # Словарь месяцев для конвертации
    months_dict = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }
    
    try:
        # 1. Номер и дата договора (расширенные паттерны)
        contract_number_patterns = [
            r'ДОГОВОР[\s\w]*№\s*([\w\d\./\-]+)',
            r'Договор[\s\w]*№\s*([\w\d\./\-]+)',
            r'КОНТРАКТ[\s\w]*№\s*([\w\d\./\-]+)',
            r'контракт[\s\w]*№\s*([\w\d\./\-]+)',
            r'СОГЛАШЕНИЕ[\s\w]*№\s*([\w\d\./\-]+)',
            r'соглашение[\s\w]*№\s*([\w\d\./\-]+)',
            r'№\s*([\w\d\./\-]+)\s*от',
            r'Договор\s+подряда\s*№\s*([\w\d\./\-]+)',
            r'ДОГОВОР\s+СТРОИТЕЛЬНОГО\s+ПОДРЯДА\s*№\s*([\w\d\./\-]+)'
        ]
        
        for pattern in contract_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['contract_number'] = match.group(1).strip()
                break
        
        # Дата договора (расширенные форматы с буквенными месяцами)
        date_patterns = [
            # Форматы с буквенными месяцами
            r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\s*г?',
            r'«(\d{1,2})»\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\s*г?',
            r'от\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\s*г?',
            # Числовые форматы
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # 25.07.2024
            r'(\d{1,2})/(\d{1,2})/(\d{4})',   # 25/07/2024
            r'(\d{4})-(\d{1,2})-(\d{1,2})',   # 2024-07-25
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3 and match.group(2) in months_dict:
                    # Буквенный месяц - конвертируем
                    day = match.group(1).zfill(2)
                    month = months_dict[match.group(2)]
                    year = match.group(3)
                    result['contract_date'] = f'{year}-{month}-{day}'
                elif len(match.groups()) == 3:
                    # Числовой формат
                    if '.' in match.group(0):
                        day, month, year = match.groups()
                        result['contract_date'] = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
                    elif '/' in match.group(0):
                        day, month, year = match.groups()
                        result['contract_date'] = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
                    else:  # yyyy-mm-dd format
                        year, month, day = match.groups()
                        result['contract_date'] = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
                else:
                    result['contract_date'] = match.group(0).strip()
                break
        
        # 2. Место заключения (расширенный список городов)
        place_patterns = [
            r'г\.\s*([А-Яа-я\-]+)\s*«\d',
            r'город\s+([А-Яа-я\-]+)',
            r'в\s+г\.\s*([А-Яа-я\-]+)',
            r'([А-Я][а-я]+)\s*«\d{1,2}»'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, text)
            if match:
                result['place_of_conclusion'] = match.group(1).strip()
                break
        
        # 3. Стороны договора - Заказчик (расширенные типы организаций и физлиц)
        customer_patterns = [
            # Юридические лица - основные формы
            r'(Общество с ограниченной ответственностью[^)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ООО[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(Открытое акционерное общество[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ОАО[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(Закрытое акционерное общество[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ЗАО[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(Публичное акционерное общество[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ПАО[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(Акционерное общество[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(АО[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            # МУП, ГУП и другие муниципальные организации
            r'(Муниципальное унитарное предприятие[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(МУП[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(Государственное унитарное предприятие[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ГУП[^,)]*)[,\.].*?ИНН[\s:]*(\d+)',
            # Индивидуальные предприниматели
            r'(Индивидуальный предприниматель[^,]*[\u0410-\u042f][а-\u044f]+[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'(ИП [\u0410-\u042f][а-\u044f]+[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            # Физические лица
            r'(гражданин[^,]*)[,\.].*?паспорт',
            r'([\u0410-\u042f][а-\u044f]+\s+[\u0410-\u042f][а-\u044f]+\s+[\u0410-\u042f][а-\u044f]+)[^,]*паспорт[\s:]*(\d+\s+\d+)',
        ]
        
        for pattern in customer_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                result['customer_name'] = match.group(1).strip()
                if len(match.groups()) > 1 and match.group(2):
                    if 'паспорт' in pattern:
                        result['customer_passport'] = match.group(2).strip()
                        result['customer_type'] = 'физическое лицо'
                    else:
                        result['customer_inn'] = match.group(2).strip()
                        if 'ИП' in match.group(1) or 'Индивидуальный предприниматель' in match.group(1):
                            result['customer_type'] = 'индивидуальный предприниматель'
                        else:
                            result['customer_type'] = 'юридическое лицо'
                break
        
        # 4. Подрядчик (расширенные паттерны для всех типов организаций)
        contractor_patterns = [
            # После заказчика ищем подрядчика
            r'и[\s\n]*(Общество[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(ООО[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(ОАО[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(ЗАО[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(ПАО[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(АО[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(Индивидуальный предприниматель[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            r'и[\s\n]*(ИП [\u0410-\u042f][а-\u044f]+[^,]*)[,\.].*?ИНН[\s:]*(\d+)',
            # Паттерны с "именуемый подрядчик"
            r'(ООО[^,]*)[^,]*именуемое[^"]*«Подрядчик»',
            r'(ИП [^,]*)[^,]*именуемый[^"]*«Подрядчик»',
            r'(Индивидуальный предприниматель[^,]*)[^,]*именуемый[^"]*«Подрядчик»',
        ]
        
        for pattern in contractor_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                result['contractor_name'] = match.group(1).strip()
                if len(match.groups()) > 1 and match.group(2):
                    result['contractor_inn'] = match.group(2).strip()
                
                if 'ИП' in match.group(1) or 'Индивидуальный предприниматель' in match.group(1):
                    result['contractor_type'] = 'индивидуальный предприниматель'
                else:
                    result['contractor_type'] = 'юридическое лицо'
                break
        
        # 4.1. Сроки выполнения работ (с различными форматами дат)
        deadline_patterns = [
            # Периоды с буквенными месяцами
            r'с\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+по\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})',
            r'с\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+до\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})',
            # Периоды с числовыми датами
            r'с\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+по\s+(\d{1,2})\.(\d{1,2})\.(\d{4})',
            r'с\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+до\s+(\d{1,2})\.(\d{1,2})\.(\d{4})',
            # Общие сроки
            r'срок\s+выполнения[^:]*:\s*до\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})',
            r'срок\s+выполнения[^:]*:\s*до\s+(\d{1,2})\.(\d{1,2})\.(\d{4})',
            r'в\s+течение\s+(\d+)\s*(месяцев|месяца|мес)',
            r'в\s+течение\s+(\d+)\s*(календарных\s+дней|дней|дня)',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 5:  # Период с начальной и конечной датами
                    if match.group(2) in months_dict:  # Буквенные месяцы
                        start_day = match.group(1).zfill(2)
                        start_month = months_dict[match.group(2)]
                        end_day = match.group(3).zfill(2)
                        end_month = months_dict[match.group(4)]
                        year = match.group(5)
                        result['work_start_date'] = f'{year}-{start_month}-{start_day}'
                        result['deadline'] = f'{year}-{end_month}-{end_day}'
                    else:  # Числовые даты
                        start_day, start_month, start_year = match.group(1), match.group(2), match.group(3)
                        end_day, end_month, end_year = match.group(4), match.group(5), match.group(6)
                        result['work_start_date'] = f'{start_year}-{start_month.zfill(2)}-{start_day.zfill(2)}'
                        result['deadline'] = f'{end_year}-{end_month.zfill(2)}-{end_day.zfill(2)}'
                elif len(match.groups()) == 3:  # Одна дата срока
                    if match.group(2) in months_dict:
                        day = match.group(1).zfill(2)
                        month = months_dict[match.group(2)]
                        year = match.group(3)
                        result['deadline'] = f'{year}-{month}-{day}'
                    else:
                        day, month, year = match.group(1), match.group(2), match.group(3)
                        result['deadline'] = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
                elif len(match.groups()) == 2:  # Период в месяцах/днях
                    duration = match.group(1)
                    unit = match.group(2)
                    if 'мес' in unit:
                        result['work_duration_months'] = duration
                    elif 'дн' in unit:
                        result['work_duration_days'] = duration
                break
        
        # 5. Объект работ (российская строительная специфика)
        work_object_patterns = [
            # Типы строительных объектов
            r'на объекте строительства:\s*«([^»]+)»',
            r'по адресу объекта:\s*([^,]+)',
            r'(Многоквартирный жилой дом[^,.]+)',
            r'(Среднеэтажный жилой дом[^,.]+)',
            r'(Малоэтажный жилой дом[^,.]+)',
            r'(Высотный жилой дом[^,.]+)',
            r'(Жилой комплекс[^,.]+)',
            r'(Торговый центр[^,.]+)',
            r'(Офисное здание[^,.]+)',
            r'(Административное здание[^,.]+)',
            r'(Производственное здание[^,.]+)',
            r'(Складское здание[^,.]+)',
            r'(Логистический центр[^,.]+)',
            r'(Подземная парковка[^,.]+)',
            r'(Многоуровневая парковка[^,.]+)',
            r'(Объект капитального строительства[^,.]+)',
            r'(Объект социальной инфраструктуры[^,.]+)',
            r'строительство\s+([^,.]+)',
            r'возведение\s+([^,.]+)',
            r'реконструкция\s+([^,.]+)',
            r'капитальный ремонт\s+([^,.]+)',
        ]
        
        for pattern in work_object_patterns:
            match = re.search(pattern, text)
            if match:
                result['work_object_name'] = match.group(1).strip()
                # Определяем тип строительства
                if 'Многоквартирный' in match.group(1):
                    result['building_type'] = 'Многоквартирный дом'
                elif 'жилой' in match.group(1).lower():
                    result['building_type'] = 'Жилое строительство'
                elif 'торгов' in match.group(1).lower():
                    result['building_type'] = 'Коммерческая недвижимость'
                elif 'офис' in match.group(1).lower():
                    result['building_type'] = 'Офисная недвижимость'
                elif 'производств' in match.group(1).lower():
                    result['building_type'] = 'Промышленная недвижимость'
                elif 'парковк' in match.group(1).lower():
                    result['building_type'] = 'Паркинг'
                break
        
        # 5.1. Адрес объекта (расширенные паттерны для российских адресов)
        address_patterns = [
            r'расположенный по адресу:\s*([^,.]+)',
            r'по адресу:\s*([^,.]+)',
            r'адрес объекта:\s*([^,.]+)',
            r'местоположение:\s*([^,.]+)',
            # Полные адреса с различными сокращениями
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*ул\. ?([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*пр-т\s+([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*пр\. ?([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*наб\. ?([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*шоссе\s+([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*пер\. ?([^,дкс]+),?\s*д\. ?(\d+[\u0430-\u044f]?)',
            # Адреса с районами и областями
            r'([\u0410-\u042f][\u0430-\u044f\-]+ область),?\s*г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*([^,]+)',
            r'г\. ?([\u0410-\u042f][\u0430-\u044f\-]+),?\s*([\u0410-\u042f][\u0430-\u044f\-]+ район),?\s*([^,]+)',
            # Московские адреса с округами
            r'г\. Москва,?\s*([\u0410-\u042f\u041e]+ округ),?\s*([^,]+)',
            r'Москва,?\s*([^,]+ул\.|[^,]+пр\.|[^,]+пр-т)[^,]*',
            # Общий паттерн
            r'г\.\s*([\u0410-\u042f][\u0430-\u044f]+)[^,]*ул\.\s*([^,]+)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) >= 3:  # Полный адрес
                    result['work_object_address'] = f'г. {match.group(1)}, {match.group(2)}, д. {match.group(3)}'
                elif len(match.groups()) == 2:
                    result['work_object_address'] = f'{match.group(1)}, {match.group(2)}'
                else:
                    result['work_object_address'] = match.group(1).strip()
                break
        
        # 6. Кадастровый номер (российские стандарты)
        cadastral_patterns = [
            r'кадастровым номером\s+([\d:]+)',
            r'кадастровый номер\s+([\d:]+)',
            r'кад\. ?№\s*([\d:]+)',
            r'к\.н\.\s*([\d:]+)',
            # Стандартные российские форматы
            r'(\d{2}:\d{2}:\d{6,7}:\d+)',  # Основной формат
            r'(\d{2}:\d{2}:\d{6,7}:\d+:\d+)',  # Полный формат
            r'кад\. ?номер\s*([\d:]+)',
            r'№ кад\. ([\d:]+)',
        ]
        
        for pattern in cadastral_patterns:
            match = re.search(pattern, text)
            if match:
                result['cadastral_number'] = match.group(1).strip()
                break
        
        # 7. Площадь участка и здания
        # 9. Площадь участка и здания (российские единицы измерения)
        area_patterns = [
            r'Площадь земельного участка[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'площадь участка[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'Общая площадь здания[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'общая площадь[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'площадь застройки[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'площадью[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
            r'с площадью[:\s]+(\d+[\s,]*\d*)\s*кв\.?м',
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                area_value = match.group(1).replace(' ', '').replace(',', '.')
                if 'земельного участка' in match.group(0).lower() or 'участка' in match.group(0).lower():
                    result['land_area'] = area_value
                elif 'здания' in match.group(0).lower() or 'общая площадь' in match.group(0).lower():
                    result['building_area'] = area_value
                break
        
        # 8. Разрешение на строительство (российская специфика с различными форматами)
        permit_patterns = [
            # Основные паттерны для разрешения
            r'разрешение на строительство\s*№ ?([^\s]+)\s*от\s+([\d\.\sянваряфеврлмартпелиюнявгустснябокьдек]+)',
            r'Разрешение\s*№ ?([^\s]+)\s*от\s+([\d\.\sянваряфеврлмартпелиюнявгустснябокьдек]+)',
            r'По разрешению\s*№ ?([^\s]+)\s*от\s+([\d\.\sянваряфеврлмартпелиюнявгустснябокьдек]+)',
            # Короткие форматы
            r'№ ?([\d\-РМО]+)\s*от\s+([\d\.\sянваряфеврлмартпелиюнявгустснябокьдек]+)\s*г',
            r'разрешение\s*№ ?([^\sот]+)',
            r'на основании разрешения\s*№ ?([^\s]+)',
            # Типичные российские форматы разрешений
            r'(\d{2}-\d{3}-\d{2,3}-\d{4})',  # Общий формат
            r'(\d{2}\.\d{2}\.\d{4}\.\d{4,6})',  # Альтернативный формат
            r'(РМО-\d{2}-\d{6})',  # Московский формат
            r'(\d{2}/\d{4}/\d{4})',  # Еще одна вариация
        ]
        
        for pattern in permit_patterns:
            match = re.search(pattern, text)
            if match:
                result['construction_permit'] = match.group(1).strip().replace('№', '')
                if len(match.groups()) > 1:
                    permit_date_str = match.group(2).strip()
                    # Пробуем конвертировать дату с буквенным месяцем
                    for month_word, month_num in months_dict.items():
                        if month_word in permit_date_str:
                            parts = permit_date_str.split()
                            if len(parts) >= 3:
                                day = parts[0].zfill(2)
                                year = parts[2]
                                result['permit_date'] = f'{year}-{month_num}-{day}'
                            break
                    else:
                        result['permit_date'] = permit_date_str
                break
        
        # 6. Финансовые условия
        # Общая стоимость (улучшенный паттерн)
        amount_pattern = r'составляет\s+(\d+\s*\d+\s*\d+[,\.]\d+)\s*руб'
        amount_match = re.search(amount_pattern, text)
        if amount_match:
            amount_str = amount_match.group(1).replace(' ', '').replace(',', '.')
            result['amount_including_vat'] = amount_str
        
        # Альтернативный паттерн для суммы
        if 'amount_including_vat' not in result:
            amount_alt_pattern = r'(\d+\s*\d+\s*\d+[,\.]\d+)\s*руб[^,]*\([^)]+\)'
            amount_alt_match = re.search(amount_alt_pattern, text)
            if amount_alt_match:
                amount_str = amount_alt_match.group(1).replace(' ', '').replace(',', '.')
                result['amount_including_vat'] = amount_str
        
        # НДС
        vat_pattern = r'НДС\s+(\d+)%\s*-\s*(\d+\s*\d+[,\.]\d+)\s*руб'
        vat_match = re.search(vat_pattern, text)
        if vat_match:
            result['vat_rate'] = vat_match.group(1)
            vat_amount_str = vat_match.group(2).replace(' ', '').replace(',', '.')
            result['vat_amount'] = vat_amount_str
        
        # Процент удержания
        retention_pattern = r'удерживает\s+(\d+)%'
        retention_match = re.search(retention_pattern, text)
        if retention_match:
            result['retention_percentage'] = retention_match.group(1)
        
        # Срок оплаты
        payment_pattern = r'в течение\s+(\d+)\s*\([^)]+\)\s*календарных дней'
        payment_match = re.search(payment_pattern, text)
        if payment_match:
            result['payment_terms_days'] = payment_match.group(1)
        
        # 7. Гарантийный срок (улучшенный паттерн)
        warranty_pattern = r'(\d+)\s*месяцев\s*с\s*момента\s*передачи'
        warranty_match = re.search(warranty_pattern, text)
        if warranty_match:
            result['warranty_period_months'] = warranty_match.group(1)
            result['warranty_start_basis'] = 'передача объекта участнику долевого строительства'
        
        # Альтернативный паттерн для гарантии
        if 'warranty_period_months' not in result:
            warranty_alt_pattern = r'шестидесяти\s*месяцев|шестьдесят\s*месяцев'
            warranty_alt_match = re.search(warranty_alt_pattern, text, re.IGNORECASE)
            if warranty_alt_match:
                result['warranty_period_months'] = '60'
                result['warranty_start_basis'] = 'передача объекта участнику долевого строительства'
        
        # 8. Штрафы и неустойки
        # Штраф за просрочку первые 7 дней
        delay1_pattern = r'(\d+,\d+)\s*%\s*от\s*цены\s*договора[^,]*первых\s*(\d+)'
        delay1_match = re.search(delay1_pattern, text)
        if delay1_match:
            result['delay_penalty_first_week'] = delay1_match.group(1).replace(',', '.')
        
        # Штраф за просрочку после 7 дней
        delay2_pattern = r'(\d+,\d+)\s*%\s*от\s*цены\s*договора[^,]*начиная\s*с\s*(\d+)-го\s*дня'
        delay2_match = re.search(delay2_pattern, text)
        if delay2_match:
            result['delay_penalty_after_week'] = delay2_match.group(1).replace(',', '.')
        
        # Штраф за документы
        doc_penalty_pattern = r'(\d+\s*\d+)\s*руб[^,]*за\s*каждый\s*факт\s*нарушения'
        doc_penalty_match = re.search(doc_penalty_pattern, text)
        if doc_penalty_match:
            result['document_penalty_amount'] = doc_penalty_match.group(1).replace(' ', '')
        
        # Штраф за нарушения на стройплощадке
        site_penalty_pattern = r'(\d+\s*\d+)\s*рублей[^,]*за\s*каждый\s*факт\s*нарушения[^,]*содержания\s*строительной\s*площадки'
        site_penalty_match = re.search(site_penalty_pattern, text)
        if site_penalty_match:
            result['site_violation_penalty'] = site_penalty_match.group(1).replace(' ', '')
        
        # 9. Приложения
        attachments = []
        # Приложение 1
        attachment1_pattern = r'Приложение\s*№1[^—]*—\s*([^;]+)'
        attachment1_match = re.search(attachment1_pattern, text)
        if attachment1_match:
            attachments.append({'number': '1', 'title': attachment1_match.group(1).strip(), 'type': 'material_protocol'})
        
        # Приложение 2
        attachment2_pattern = r'Приложение\s*№2[^—]*—\s*([^;]+)'
        attachment2_match = re.search(attachment2_pattern, text)
        if attachment2_match:
            attachments.append({'number': '2', 'title': attachment2_match.group(1).strip(), 'type': 'estimate'})
        
        # Приложение 3
        attachment3_pattern = r'Приложение\s*№3[^—]*—\s*([^;]+)'
        attachment3_match = re.search(attachment3_pattern, text)
        if attachment3_match:
            attachments.append({'number': '3', 'title': attachment3_match.group(1).strip(), 'type': 'schedule'})
        
        # Приложение 4
        attachment4_pattern = r'Приложение\s*№4[^—]*([^;]+)'
        attachment4_match = re.search(attachment4_pattern, text)
        if attachment4_match:
            attachments.append({'number': '4', 'title': attachment4_match.group(1).strip(), 'type': 'consent_form'})
        
        # Приложение 5
        attachment5_pattern = r'Приложение\s*№5[^—]*—\s*([^.]+)'
        attachment5_match = re.search(attachment5_pattern, text)
        if attachment5_match:
            attachments.append({'number': '5', 'title': attachment5_match.group(1).strip(), 'type': 'technical_map'})
        
        if attachments:
            result['attachments'] = attachments
        
        # 10. Проектная документация
        project_docs_pattern = r'проектной документацией\s*\(([^)]+)\)'
        project_docs_match = re.search(project_docs_pattern, text)
        if project_docs_match:
            result['project_documentation'] = project_docs_match.group(1).strip()
        
        # 11. Банковские реквизиты заказчика
        customer_bank_pattern = r'р/с\s*(\d+)\s*([^к]+)к/с\s*(\d+)\s*БИК\s*(\d+)'
        customer_bank_match = re.search(customer_bank_pattern, text)
        if customer_bank_match:
            result['customer_bank_account'] = customer_bank_match.group(1).strip()
            result['customer_bank_name'] = customer_bank_match.group(2).strip()
            result['customer_correspondent_account'] = customer_bank_match.group(3).strip()
            result['customer_bik'] = customer_bank_match.group(4).strip()
        
        # 12. Банковские реквизиты подрядчика (ищем второе вхождение)
        contractor_bank_matches = list(re.finditer(r'р/с\s*(\d+)[^к]*([^к]+)к/с\s*(\d+)\s*БИК\s*(\d+)', text))
        if len(contractor_bank_matches) > 1:
            contractor_bank_match = contractor_bank_matches[1]
            result['contractor_bank_account'] = contractor_bank_match.group(1).strip()
            result['contractor_bank_name'] = contractor_bank_match.group(2).strip()
            result['contractor_correspondent_account'] = contractor_bank_match.group(3).strip()
            result['contractor_bik'] = contractor_bank_match.group(4).strip()
        
        # 13. ОГРН
        customer_ogrn_pattern = r'ОГРН\s*(\d+)'
        customer_ogrn_match = re.search(customer_ogrn_pattern, text)
        if customer_ogrn_match:
            result['customer_ogrn'] = customer_ogrn_match.group(1).strip()
        
        # 14. Тип договора
        contract_type_pattern = r'ДОГОВОР\s+(\w+)'
        contract_type_match = re.search(contract_type_pattern, text)
        if contract_type_match:
            result['contract_type'] = contract_type_match.group(1).strip()
        
        # 15. Поручительство
        guarantee_pattern = r'([А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+)\s+предоставляет\s+личное\s+поручительство'
        guarantee_match = re.search(guarantee_pattern, text)
        if guarantee_match:
            result['guarantor_name'] = guarantee_match.group(1).strip()
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении полей договора: {e}")
        result['extraction_error'] = str(e)
    
    return result
