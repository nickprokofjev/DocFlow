#!/usr/bin/env python3
"""
Простая диагностика OCR для DocFlow
Проверяет доступность всех компонентов OCR
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ocr_components():
    """Тестирует все компоненты OCR"""
    print("DocFlow OCR Диагностика")
    print("=" * 30)
    
    try:
        from ocr_nlp import OCR_AVAILABLE, TESSERACT_AVAILABLE, POPPLER_PATH, TESSERACT_PATH
        print(f"OCR библиотеки доступны: {'✓' if OCR_AVAILABLE else '✗'}")
        print(f"Tesseract доступен: {'✓' if TESSERACT_AVAILABLE else '✗'}")
        
        if TESSERACT_PATH:
            print(f"Tesseract путь: {TESSERACT_PATH}")
        else:
            print("Tesseract путь: не настроен")
            
        if POPPLER_PATH:
            print(f"Poppler путь: {POPPLER_PATH}")
        else:
            print("Poppler путь: не настроен")
            
        # Тест извлечения текста
        print("\nТест функций OCR:")
        from ocr_nlp import extract_text_from_file
        
        # Создаем тестовое изображение с текстом
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 100), color='white')
            d = ImageDraw.Draw(img)
            d.text((10, 10), "Test OCR text", fill='black')
            
            test_image_path = "test_ocr_image.png"
            img.save(test_image_path)
            
            result = extract_text_from_file(test_image_path)
            print(f"Результат OCR теста: {result[:100]}...")
            
            # Удаляем тестовое изображение
            os.remove(test_image_path)
            
        except Exception as e:
            print(f"Ошибка теста OCR: {e}")
            
    except Exception as e:
        print(f"Ошибка импорта: {e}")

if __name__ == "__main__":
    test_ocr_components()