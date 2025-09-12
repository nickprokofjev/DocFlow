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
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import spacy
from typing import List

# Настройка логгирования для OCR/NLP
logger = logging.getLogger(__name__)

# Загрузка русской модели spaCy
try:
    nlp = spacy.load("ru_core_news_lg")
    logger.info("spaCy модель ru_core_news_lg успешно загружена")
except OSError:
    from spacy.cli import download
    logger.info("spaCy модель не найдена, скачиваем...")
    download("ru_core_news_lg")
    nlp = spacy.load("ru_core_news_lg")
    logger.info("spaCy модель ru_core_news_lg успешно скачана и загружена")

def extract_text_from_file(file_path: str) -> str:
    """
    Извлекает текст из файла (PDF или изображения) с помощью OCR.
    Возвращает распознанный текст.
    """
    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"Начало OCR для файла: {file_path}")
    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="rus")
        elif ext == ".pdf":
            images = convert_from_path(file_path)
            text = "\n".join([pytesseract.image_to_string(img, lang="rus") for img in images])
        else:
            logger.warning(f"Неподдерживаемый формат файла: {ext}")
            text = ""
        logger.info(f"OCR завершён, длина текста: {len(text)} символов")
        return text
    except Exception as e:
        logger.error(f"Ошибка OCR: {e}")
        return ""

def extract_contract_entities(text: str) -> dict:
    """
    Извлекает сущности из текста договора с помощью spaCy (организации, даты, суммы, лица).
    Возвращает словарь найденных сущностей.
    """
    logger.info("Начало NLP-извлечения сущностей из текста")
    try:
        doc = nlp(text)
        # Простейшее извлечение сущностей (можно доработать под задачу)
        entities = {"ORG": [], "DATE": [], "MONEY": [], "PERSON": []}
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        logger.info(f"NLP завершён, найдено: {entities}")
        return entities
    except Exception as e:
        logger.error(f"Ошибка NLP: {e}")
        return {}
