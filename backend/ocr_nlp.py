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

def extract_text_from_file(file_path: str) -> str:
    """
    Извлекает текст из файла (PDF или изображения) с помощью OCR.
    Возвращает распознанный текст или сообщение об ошибке.
    """
    if not OCR_AVAILABLE or not pytesseract or not Image or not convert_from_path:
        logger.warning("Библиотеки OCR не установлены. Установите pytesseract, Pillow, pdf2image")
        return "Ошибка: OCR недоступен"

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
        logger.exception(f"Ошибка при OCR: {e}")
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
