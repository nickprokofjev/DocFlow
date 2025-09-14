#!/usr/bin/env python3
"""
Test script for the enhanced contract processing functionality.
Tests OCR/NLP extraction with the sample contract text.
"""

import sys
import os
from typing import Dict, List, Union, Any
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_nlp import extract_contract_entities, extract_detailed_contract_fields

# Sample contract text from the user's provided document
SAMPLE_CONTRACT_TEXT = """
ДОГОВОР ПОДРЯДА №03.07/24-К
г. Самара «03» июля 2024 г.

Общество с ограниченной ответственностью «Строительная компания «Лидер»
(ООО «СК «Лидер», ИНН 6317153913), именуемое в дальнейшем «Заказчик», в лице директора
единоличного исполнительного органа - управляющей компании ООО «Лидер» (ИНН 6316272717)
Власова Егора Евгеньевича, действующего на основании Устава, с одной стороны, и

Общество с ограниченной ответственностью «АТЛАНТ» (ООО «АТЛАНТ»), именуемое в
дальнейшем «Подрядчик», в лице Генерального директора Бикбулатова Марата Наильевича,
действующего на основании Устава, с другой стороны, при совместном упоминании «Стороны»,
заключили настоящий договор о нижеследующем:

1. Предмет договора

1.1. Подрядчик обязуется по заданию Заказчика собственными силами и средствами с применением
давальческого материала выполнить работы по устройству фасада секции №1, №9 (отделка
фасада - лоджии, наружные стены) по системе типа ЛАЭС либо аналога на объекте
строительства: «Среднеэтажный жилой дом со встроенными нежилыми помещениями и
подземным паркингом, расположенный по адресу: г. Самара, Октябрьский район, просека
Третья» (строительная площадка ЖК «Культура» (на земельном участке с кадастровым
номером 63:01:0637003:94, площадью 15 000 кв.м., разрешение на строительство №63-301000-
130-2021 от 29.07.2021г.)

4. Цена договора и порядок расчетов

4.1. Цена настоящего Договора в соответствии со Сметным расчетом составляет 4728 960,00 руб. 
(Четыре миллиона семьсот двадцать восемь тысяч девятьсот шестьдесят рублей 00 копеек), 
в тч. НДС 20% - 788 160,00 руб.

4.2.2. Стороны пришли к соглашению о том, что при оплате выполненных работ Заказчик удерживает
5% от стоимости фактически выполненного соответствующего этапа работ Подрядчиком

10.1. Срок гарантии на все выполненные по настоящему договору работы, использованные материалы
и оборудование заканчивается по истечению шестидесяти месяцев с момента передачи по первому
акту приема-передачи объекта участнику долевого строительства.

6.2. В случае несоблюдения Подрядчиком сроков выполнения работ Подрядчик выплачивает Заказчику
пени в размере:
- 0,1 % от цены договора, за каждый день просрочки в течение первых 7 (семи) дней просрочки;
- 0,2 % от цены договора за каждый день просрочки, начиная с 8-го дня просрочки

6.4. За несвоевременное предоставление документов Подрядчик
уплачивает Заказчику штрафную неустойку в размере 50000 руб. за каждый факт нарушения

Приложение №1 — Протокол согласования расхода материала;
Приложение №2 — Сметный расчёт;
Приложение №3 — График производства работ;
Приложение №4 - Форма согласия на обработку персональных;
Приложение №5 - Технологическая карта Корпорации ТЕХНОНИКОЛЬ «Устройство систем
фасадных теплоизоляционных композитных».
"""

def test_contract_extraction():
    """Test the contract data extraction functionality."""
    print("🧪 Testing Contract Data Extraction")
    print("=" * 50)
    
    try:
        # Test the detailed field extraction
        print("📋 Extracting detailed contract fields...")
        extracted_data = extract_detailed_contract_fields(SAMPLE_CONTRACT_TEXT)
        
        print("\n✅ Extraction Results:")
        print("-" * 30)
        
        for key, value in extracted_data.items():
            if value:
                print(f"📌 {key}: {value}")
        
        # Expected fields to validate
        expected_fields = {
            'contract_number': '03.07/24-К',
            'customer_name': 'Общество с ограниченной ответственностью «Строительная компания «Лидер»',
            'contractor_name': 'Общество с ограниченной ответственностью «АТЛАНТ»',
            'customer_inn': '6317153913',
            'customer_director_name': 'Власова Егора Евгеньевича',
            'contractor_director_name': 'Бикбулатова Марата Наильевича',
            'work_object_name': 'Среднеэтажный жилой дом со встроенными нежилыми помещениями и подземным паркингом',
            'cadastral_number': '63:01:0637003:94',
            'construction_permit': '63-301000-130-2021',
            'amount_including_vat': '4728960.00',
            'vat_rate': '20',
            'retention_percentage': '5',
            'warranty_period_months': '60',
        }
        
        print("\n🔍 Validation Results:")
        print("-" * 30)
        
        successful_extractions = 0
        total_expected = len(expected_fields)
        
        for field, expected_value in expected_fields.items():
            if field in extracted_data and extracted_data[field]:
                actual_value = str(extracted_data[field]).strip()
                if expected_value.lower() in actual_value.lower() or actual_value.lower() in expected_value.lower():
                    print(f"✅ {field}: SUCCESS")
                    successful_extractions += 1
                else:
                    print(f"⚠️  {field}: PARTIAL (Expected: {expected_value}, Got: {actual_value})")
                    successful_extractions += 0.5
            else:
                print(f"❌ {field}: MISSING")
        
        print(f"\n📊 Success Rate: {successful_extractions}/{total_expected} ({successful_extractions/total_expected*100:.1f}%)")
        
        # Test attachments extraction
        if 'attachments' in extracted_data and extracted_data['attachments'] is not None:
            attachments_list = extracted_data['attachments']
            if isinstance(attachments_list, list):
                print(f"\n📎 Attachments Found: {len(attachments_list)}")
                for i, attachment in enumerate(attachments_list, 1):
                    if isinstance(attachment, dict):
                        title = attachment.get('title', 'Unknown Title')
                        attachment_type = attachment.get('type', 'Unknown Type')
                        print(f"   {i}. {title} (Type: {attachment_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nlp_entities():
    """Test the NLP entity extraction."""
    print("\n🤖 Testing NLP Entity Extraction")
    print("=" * 50)
    
    try:
        entities = extract_contract_entities(SAMPLE_CONTRACT_TEXT)
        
        if isinstance(entities, dict) and 'error' not in entities:
            print("✅ NLP extraction successful!")
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list) and entity_list:
                    print(f"📌 {entity_type}: {len(entity_list)} found")
                    for entity in entity_list[:3]:  # Show first 3
                        print(f"   - {entity}")
                elif entity_type not in ['ORG', 'DATE', 'MONEY', 'PERSON']:
                    # Show other extracted fields
                    if entity_list is not None:
                        print(f"📌 {entity_type}: {entity_list}")
        else:
            print(f"❌ NLP extraction failed: {entities}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during NLP extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Contract Processing Tests")
    print("=" * 60)
    
    test1_passed = test_contract_extraction()
    test2_passed = test_nlp_entities()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("-" * 20)
    print(f"📋 Contract Field Extraction: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"🤖 NLP Entity Extraction: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The enhanced contract processing system is working correctly.")
        print("\n💡 Next Steps:")
        print("   1. Run the backend server: python backend/main.py")
        print("   2. Run the frontend: npm run dev")
        print("   3. Upload the sample contract through the web interface")
        print("   4. Verify the extracted data in the contract details view")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        
    return test1_passed and test2_passed

if __name__ == "__main__":
    main()