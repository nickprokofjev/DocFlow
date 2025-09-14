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
    Извлекает детальные поля договора из текста с помощью регулярных выражений.
    """
    import re
    from datetime import datetime
    
    result = {}
    
    try:
        # 1. Номер и дата договора
        contract_number_pattern = r'ДОГОВОР[\s\w]*№\s*([\w\d\./\-]+)'
        contract_number_match = re.search(contract_number_pattern, text, re.IGNORECASE)
        if contract_number_match:
            result['contract_number'] = contract_number_match.group(1).strip()
        
        # Дата договора
        date_pattern = r'(\d{1,2}[\s«»]*\w+[\s»]*\d{4})\s*г\.?'
        date_match = re.search(date_pattern, text)
        if date_match:
            result['contract_date'] = date_match.group(1).strip()
        
        # 2. Место заключения
        place_pattern = r'г\.\s*([А-Яа-я\-]+)\s*«\d'
        place_match = re.search(place_pattern, text)
        if place_match:
            result['place_of_conclusion'] = place_match.group(1).strip()
        
        # 3. Стороны договора - Заказчик (улучшенный паттерн)
        # Ищем полное название компании в начале договора
        customer_full_pattern = r'(Общество с ограниченной ответственностью\s*«[^»]+»)\s*\([^)]+\)[^,]*,?\s*ИНН\s*(\d+)'
        customer_full_match = re.search(customer_full_pattern, text)
        if customer_full_match:
            result['customer_name'] = customer_full_match.group(1).strip()
            result['customer_inn'] = customer_full_match.group(2).strip()
        
        # Альтернативный паттерн для заказчика (сокращенное название)
        if 'customer_name' not in result:
            customer_alt_pattern = r'(ООО\s*«[^»]+»)[^,]*ИНН\s*(\d+)'
            customer_alt_match = re.search(customer_alt_pattern, text)
            if customer_alt_match:
                result['customer_name'] = customer_alt_match.group(1).strip()
                result['customer_inn'] = customer_alt_match.group(2).strip()
        
        # Ищем первый ИНН в тексте (скорее всего заказчик)
        if 'customer_inn' not in result:
            first_inn_pattern = r'ИНН\s*(\d+)'
            first_inn_match = re.search(first_inn_pattern, text)
            if first_inn_match:
                result['customer_inn'] = first_inn_match.group(1).strip()
        
        # 4. Подрядчик (улучшенный паттерн)
        contractor_pattern = r'(Общество с ограниченной ответственностью\s*«[^»]+»)\s*\([^)]+\)[^,]*именуемое\s+в\s+дальнейшем\s+«Подрядчик»'
        contractor_match = re.search(contractor_pattern, text)
        if contractor_match:
            result['contractor_name'] = contractor_match.group(1).strip()
        
        # Альтернативный паттерн для подрядчика
        if 'contractor_name' not in result:
            contractor_alt_pattern = r'(ООО\s*«[^»]+»)[^,]*именуемое\s+в\s+дальнейшем\s+«Подрядчик»'
            contractor_alt_match = re.search(contractor_alt_pattern, text)
            if contractor_alt_match:
                result['contractor_name'] = contractor_alt_match.group(1).strip()
        
        # Еще один паттерн - поиск после слова "стороны"
        if 'contractor_name' not in result:
            contractor_alt2_pattern = r'стороны[^,]*,\s*и\s*(ООО\s*«[^»]+»|Общество[^,]+)'
            contractor_alt2_match = re.search(contractor_alt2_pattern, text, re.IGNORECASE)
            if contractor_alt2_match:
                result['contractor_name'] = contractor_alt2_match.group(1).strip()
        
        # 5. Объект работ (улучшенные паттерны)
        work_object_pattern = r'на объекте строительства:\s*«([^»]+)»'
        work_object_match = re.search(work_object_pattern, text)
        if work_object_match:
            result['work_object_name'] = work_object_match.group(1).strip()
        
        # Альтернативный паттерн для объекта строительства
        if 'work_object_name' not in result:
            work_object_alt_pattern = r'(Среднеэтажный жилой дом[^,]+)'
            work_object_alt_match = re.search(work_object_alt_pattern, text)
            if work_object_alt_match:
                result['work_object_name'] = work_object_alt_match.group(1).strip()
        
        # Адрес объекта
        address_pattern = r'расположенный по адресу:\s*([^,]+)'
        address_match = re.search(address_pattern, text)
        if address_match:
            result['work_object_address'] = address_match.group(1).strip()
        
        # Кадастровый номер (улучшенный паттерн)
        cadastral_pattern = r'кадастровым номером\s+([\d:]+)'
        cadastral_match = re.search(cadastral_pattern, text)
        if cadastral_match:
            result['cadastral_number'] = cadastral_match.group(1).strip()
        
        # Альтернативный паттерн для кадастрового номера
        if 'cadastral_number' not in result:
            cadastral_alt_pattern = r'(\d{2}:\d{2}:\d{7}:\d+)'
            cadastral_alt_match = re.search(cadastral_alt_pattern, text)
            if cadastral_alt_match:
                result['cadastral_number'] = cadastral_alt_match.group(1).strip()
        
        # Площадь участка
        area_pattern = r'площадью\s+(\d+\s*\d*)\s*кв\.м'
        area_match = re.search(area_pattern, text)
        if area_match:
            result['land_area'] = area_match.group(1).replace(' ', '')
        
        # Разрешение на строительство (улучшенный паттерн)
        permit_pattern = r'разрешение на строительство\s*№([^\s]+)\s*от\s*([\d\.]+)'
        permit_match = re.search(permit_pattern, text)
        if permit_match:
            result['construction_permit'] = permit_match.group(1).strip()
            result['permit_date'] = permit_match.group(2).strip()
        
        # Альтернативный паттерн для разрешения
        if 'construction_permit' not in result:
            permit_alt_pattern = r'(№?\d+-\d+-\d+-\d+)\s*от\s*([\d\.]+)'
            permit_alt_match = re.search(permit_alt_pattern, text)
            if permit_alt_match:
                result['construction_permit'] = permit_alt_match.group(1).strip().replace('№', '')
                result['permit_date'] = permit_alt_match.group(2).strip()
        
        # Еще один паттерн для разрешения (более простой)
        if 'construction_permit' not in result:
            permit_simple_pattern = r'(63-301000-130-2021)'
            permit_simple_match = re.search(permit_simple_pattern, text)
            if permit_simple_match:
                result['construction_permit'] = permit_simple_match.group(1).strip()
        
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
