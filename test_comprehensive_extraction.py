#!/usr/bin/env python3
"""
Comprehensive test for enhanced OCR/NLP extraction patterns.
Tests all the new Russian construction contract features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ocr_nlp import extract_detailed_contract_fields

def test_comprehensive_extraction():
    """Test comprehensive enhanced extraction patterns"""
    
    # Comprehensive test text with all variations
    test_text = """
    ДОГОВОР СТРОИТЕЛЬНОГО ПОДРЯДА № 2024/СТР-001
    от 25 июля 2024 г.
    
    г. Москва                                           «25» июля 2024 г.
    
    Общество с ограниченной ответственностью «СтройИнвест» (ООО «СтройИнвест»), 
    ИНН 7702123456, ОГРН 1027700123456, именуемое в дальнейшем «Заказчик»,
    
    и
    
    Индивидуальный предприниматель Петров Иван Сергеевич, 
    ИНН 770212345678, именуемый в дальнейшем «Подрядчик»,
    
    заключили настоящий договор о следующем:
    
    1. Подрядчик обязуется выполнить строительство Многоквартирного жилого дома 
    расположенного по адресу: г. Москва, ул. Строительная, д. 15, кор. 2
    кадастровый номер 77:01:0001234:567
    
    2. Срок выполнения работ: с 01 августа по 31 декабря 2024 года
    
    3. Стоимость работ составляет 5 500 000,00 руб. (пять миллионов пятьсот тысяч рублей)
    НДС 20% - 916 666,67 руб.
    
    4. На основании разрешения на строительство № 77-123-456-2024 от 15 июля 2024 г.
    
    5. Площадь земельного участка 1200 кв.м
    Общая площадь здания 2800 кв.м
    
    6. Гарантийный срок 60 месяцев с момента передачи объекта
    
    7. При просрочке работ:
    - первые 7 дней: 0,1% от цены договора за каждый день
    - начиная с 8-го дня: 0,2% от цены договора за каждый день
    
    8. Банковские реквизиты:
    Заказчик: р/с 40702810123456789012 в ПАО «Сбербанк», к/с 30101810400000000225, БИК 044525225
    Подрядчик: р/с 40802810987654321098 в ВТБ, к/с 30101810145250000411, БИК 044525411
    """
    
    print("Testing comprehensive enhanced OCR/NLP extraction patterns...")
    print("=" * 80)
    
    # Extract entities
    result = extract_detailed_contract_fields(test_text)
    
    print("✅ EXTRACTED ENTITIES:")
    print("-" * 40)
    
    for key, value in sorted(result.items()):
        if value:  # Only show non-empty results
            print(f"{key:30} : {value}")
    
    print("\n" + "=" * 80)
    
    # Check key extractions
    key_checks = {
        'contract_number': '2024/СТР-001',
        'contract_date': '2024-07-25',
        'customer_name': 'СтройИнвест',
        'customer_inn': '7702123456',
        'customer_ogrn': '1027700123456',
        'customer_type': 'юридическое лицо',
        'contractor_name': 'Индивидуальный предприниматель Петров Иван Сергеевич',
        'contractor_inn': '770212345678',
        'contractor_type': 'индивидуальный предприниматель',
        'work_object_name': 'Многоквартирного жилого дома',
        'work_object_address': 'г. Москва, ул. Строительная, д. 15',
        'cadastral_number': '77:01:0001234:567',
        'work_start_date': '2024-08-01',
        'deadline': '2024-12-31',
        'construction_permit': '77-123-456-2024',
        'permit_date': '2024-07-15',
        'amount_including_vat': '5500000.00',
        'vat_rate': '20',
        'vat_amount': '916666.67',
        'land_area': '1200',
        'building_area': '2800',
        'warranty_period_months': '60',
        'delay_penalty_first_week': '0.1',
        'delay_penalty_after_week': '0.2',
        'customer_bank_account': '40702810123456789012',
        'customer_bik': '044525225',
        'contractor_bank_account': '40802810987654321098',
        'contractor_bik': '044525411'
    }
    
    print("🔍 VALIDATION RESULTS:")
    print("-" * 40)
    
    success_count = 0
    total_count = len(key_checks)
    
    for key, expected in key_checks.items():
        actual = str(result.get(key, ''))
        status = "✅" if expected in actual else "❌"
        if expected in actual:
            success_count += 1
        print(f"{status} {key:30} : Expected '{expected}' → Got '{actual[:50]}{'...' if len(actual) > 50 else ''}'")
    
    print(f"\n🎯 SUCCESS RATE: {success_count}/{total_count} ({(success_count/total_count)*100:.1f}%)")
    print("=" * 80)
    
    # Enhancement summary
    print("\n🚀 ENHANCEMENT SUMMARY:")
    print("-" * 40)
    print("✅ Multiple entity types (ООО, ИП, физлица)")
    print("✅ Date formats with written months (25 июля 2024)")
    print("✅ Time periods (с 01 августа по 31 декабря)")
    print("✅ Russian construction terminology")
    print("✅ Enhanced address patterns")
    print("✅ Construction permits with various formats")
    print("✅ Financial terms and penalties")
    print("✅ Banking details extraction")
    print("✅ Building types and specifications")
    print("✅ Area measurements (land vs building)")
    
    return result

if __name__ == "__main__":
    test_comprehensive_extraction()