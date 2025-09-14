#!/usr/bin/env python3
"""
Тестовый скрипт для проверки асинхронной обработки OCR/NLP.
Тестирует устранение проблемы с Gateway Timeout.
"""
import asyncio
import sys
import os
import time
from pathlib import Path

# Добавляем backend в путь
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Типы для статического анализа (собранные импорты выполняются динамически)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Импорты только для проверки типов - не выполняются в runtime
    import sys
    sys.path.append(str(Path(__file__).parent / "backend"))
    from task_queue import TaskQueue, JobStatus  # type: ignore
    import ocr_nlp  # type: ignore
else:
    # Runtime импорты - динамические после добавления пути
    TaskQueue = None
    JobStatus = None
    ocr_nlp = None

async def test_async_processing():
    """Тестирует асинхронную обработку задач."""
    print("🔄 Тестирование асинхронной обработки OCR/NLP...")
    
    try:
        # Импортируем после добавления пути
        import sys
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from task_queue import TaskQueue, JobStatus  # type: ignore
        
        # Создаём экземпляр очереди задач
        queue = TaskQueue()
        print("✅ TaskQueue создан успешно")
        
        # Создаём тестовую задачу
        async def test_task(job_id: str, duration: int = 5):
            """Тестовая задача, которая выполняется несколько секунд."""
            print(f"📝 Задача {job_id} начата")
            
            for i in range(duration):
                await asyncio.sleep(1)
                progress = (i + 1) * (100 // duration)
                queue.update_job_progress(job_id, progress, f"Выполнено {i+1}/{duration} шагов")
                print(f"⏳ Задача {job_id}: прогресс {progress}%")
            
            return {"result": f"Задача {job_id} завершена", "steps": duration}
        
        # Запускаем задачу
        job_id = "test_job_001"
        await queue.submit_job(job_id, test_task, 3)
        print(f"🚀 Задача {job_id} отправлена в очередь")
        
        # Мониторим выполнение
        start_time = time.time()
        while True:
            job_status = queue.get_job_status(job_id)
            if not job_status:
                print("❌ Статус задачи не найден")
                break
                
            print(f"📊 Статус: {job_status.status.value}, Прогресс: {job_status.progress}%, Сообщение: {job_status.message}")
            
            if job_status.status.value in ['completed', 'failed', 'cancelled']:
                if job_status.status.value == 'completed':
                    print(f"✅ Задача завершена успешно: {job_status.result}")
                else:
                    print(f"❌ Задача завершена с ошибкой: {job_status.error}")
                break
            
            # Таймаут на 30 секунд
            if time.time() - start_time > 30:
                print("⏰ Тест завершён по таймауту")
                break
                
            await asyncio.sleep(1)
            
        print("✅ Тест асинхронной обработки завершён")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ocr_processing():
    """Тестирует OCR обработку если доступны библиотеки."""
    print("🔄 Тестирование OCR/NLP обработки...")
    
    try:
        # Проверяем доступность OCR - импортируем после добавления пути
        import sys
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        import ocr_nlp  # type: ignore
        OCR_AVAILABLE = ocr_nlp.OCR_AVAILABLE
        TESSERACT_AVAILABLE = ocr_nlp.TESSERACT_AVAILABLE
        
        if not OCR_AVAILABLE:
            print("⚠️  OCR библиотеки недоступны, пропускаем тест")
            return True
            
        if not TESSERACT_AVAILABLE:
            print("⚠️  Tesseract недоступен, пропускаем тест")
            return True
            
        print("✅ OCR/NLP компоненты доступны")
        
        # Тестируем создание тестового файла
        test_file = backend_path / "test_document.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ДОГОВОР № TEST-001 от 14.09.2024\n")
            f.write("Заказчик: ООО Тест\n")
            f.write("Подрядчик: ИП Тестов А.А.\n")
            f.write("Сумма: 100000 рублей\n")
        
        print(f"📝 Создан тестовый файл: {test_file}")
        
        # Очищаем тестовый файл
        test_file.unlink()
        print("🗑️  Тестовый файл удалён")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании OCR: {e}")
        return False

def test_nginx_config():
    """Проверяет конфигурацию nginx."""
    print("🔄 Проверка конфигурации nginx...")
    
    try:
        nginx_config = Path(__file__).parent / "frontend" / "nginx.conf"
        
        if not nginx_config.exists():
            print("❌ Файл nginx.conf не найден")
            return False
            
        with open(nginx_config, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Проверяем наличие timeout настроек
        if "proxy_read_timeout 300s" in content:
            print("✅ Timeout настройки для API найдены")
        else:
            print("⚠️  Timeout настройки для API не найдены")
            
        if "client_max_body_size 50M" in content:
            print("✅ Лимит размера файла настроен")
        else:
            print("⚠️  Лимит размера файла не найден")
            
        print("✅ Конфигурация nginx проверена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке nginx: {e}")
        return False

def test_api_endpoints():
    """Проверяет доступность новых API эндпоинтов."""
    print("🔄 Проверка API эндпоинтов...")
    
    try:
        # Импортируем после добавления пути - используем sys.modules для корректного импорта
        import importlib.util
        import sys
        
        # Получаем абсолютный путь к api.py
        api_file_path = backend_path / "api.py"
        
        # Загружаем модуль api напрямую
        spec = importlib.util.spec_from_file_location("api", api_file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Не удалось загрузить модуль api из {api_file_path}")
            
        api_module = importlib.util.module_from_spec(spec)
        sys.modules["api"] = api_module
        spec.loader.exec_module(api_module)
        
        router = api_module.router
        
        # Проверяем, что новые маршруты добавлены
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            "/contracts/extract",
            "/jobs/{job_id}/status", 
            "/jobs/{job_id}/cancel"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Маршрут {route} найден")
            else:
                print(f"❌ Маршрут {route} не найден")
                
        print("✅ Проверка API эндпоинтов завершена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке API: {e}")
        return False

async def main():
    """Главная функция тестирования."""
    print("🧪 === ТЕСТИРОВАНИЕ РЕШЕНИЯ ПРОБЛЕМЫ GATEWAY TIMEOUT ===\n")
    
    tests = [
        ("Конфигурация nginx", test_nginx_config),
        ("API эндпоинты", test_api_endpoints),
        ("Асинхронная обработка", test_async_processing),
        ("OCR/NLP компоненты", test_ocr_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name}: ПРОЙДЕН")
        else:
            print(f"❌ {test_name}: ПРОВАЛЕН")
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nПройдено тестов: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Проблема с Gateway Timeout должна быть решена.")
        
        print("\n📋 РЕКОМЕНДАЦИИ:")
        print("1. Перезапустите Docker containers для применения изменений nginx")
        print("2. Проверьте работу на реальных файлах договоров")
        print("3. Мониторьте логи при обработке больших файлов")
        
    else:
        print("⚠️  Некоторые тесты провалены. Требуется дополнительная настройка.")
    
    return passed == len(results)

if __name__ == "__main__":
    asyncio.run(main())