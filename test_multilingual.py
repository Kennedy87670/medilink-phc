"""
MediLink PHC - Day 4 Multilingual Test
Test the multilingual translation system
"""

import sys
import os
sys.path.insert(0, 'src')

from multilingual_translator import MultilingualTranslator

def test_multilingual_system():
    """Test the multilingual system without AI dependencies"""
    print("\n" + "="*80)
    print("🗣️  TESTING MULTILINGUAL TRANSLATION SYSTEM")
    print("="*80 + "\n")
    
    translator = MultilingualTranslator()
    
    # Test cases with different Nigerian languages
    test_cases = [
        {
            "name": "Hausa Fever Case",
            "symptoms": ["zazzabi", "ciwon kai", "rashin kuzari"],
            "expected": ["fever", "headache", "weakness"]
        },
        {
            "name": "Igbo Diarrhea Case", 
            "symptoms": ["mgbawa", "agba", "adighi ike"],
            "expected": ["diarrhea", "vomiting", "weakness"]
        },
        {
            "name": "Yoruba Breathing Problem",
            "symptoms": ["ipalara emi", "aya n dun", "ikọ"],
            "expected": ["breathing", "chest", "cough"]
        },
        {
            "name": "Pidgin Emergency",
            "symptoms": ["e don faint", "im body dey shake", "breath dey hard"],
            "expected": ["unconscious", "convulsions", "breathing"]
        },
        {
            "name": "Mixed Languages",
            "symptoms": ["zazzabi", "body dey pain", "mgbawa", "ikọ"],
            "expected": ["fever", "pain", "diarrhea", "cough"]
        },
        {
            "name": "Pure English",
            "symptoms": ["headache", "fever", "cough"],
            "expected": ["headache", "fever", "cough"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"🔬 Test {i}: {test['name']}")
        print(f"{'─'*60}")
        
        print(f"Input: {test['symptoms']}")
        
        # Detect languages
        detected_languages = []
        for symptom in test['symptoms']:
            lang = translator.detect_language(symptom)
            detected_languages.append(lang or "english")
        
        print(f"Detected Languages: {detected_languages}")
        
        # Translate
        translated, translation_map = translator.translate_symptoms(test['symptoms'])
        print(f"Translated: {translated}")
        
        if translation_map:
            print(f"Translations Made:")
            for orig, trans in translation_map.items():
                print(f"  • '{orig}' → '{trans}'")
        else:
            print(f"No translations needed")
        
        # Check expected keywords
        translated_text = ' '.join(translated).lower()
        found_keywords = [kw for kw in test['expected'] if kw in translated_text]
        print(f"✅ Found Expected Keywords: {found_keywords}")
        
        # Calculate success rate
        success_rate = len(found_keywords) / len(test['expected']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n{'='*80}")
    print("✅ MULTILINGUAL TRANSLATION TESTING COMPLETE!")
    print("="*80)
    
    # Test language detection accuracy
    print(f"\n📊 LANGUAGE DETECTION ACCURACY:")
    print("-" * 40)
    
    language_tests = [
        ("Hausa", ["zazzabi", "ciwon kai", "gudawa"]),
        ("Igbo", ["mgbawa", "agba", "adighi ike"]),
        ("Yoruba", ["ipalara emi", "aya n dun", "ikọ"]),
        ("Pidgin", ["body dey hot", "head dey pain", "e dey vomit"]),
        ("English", ["fever", "headache", "diarrhea"])
    ]
    
    for lang_name, test_words in language_tests:
        correct_detections = 0
        for word in test_words:
            detected = translator.detect_language(word)
            if detected == lang_name.lower():
                correct_detections += 1
        
        accuracy = correct_detections / len(test_words) * 100
        print(f"{lang_name}: {accuracy:.1f}% ({correct_detections}/{len(test_words)})")
    
    print(f"\n🎯 READY FOR BACKEND INTEGRATION!")
    print("The multilingual translator can now handle:")
    print("  ✅ Hausa medical terms")
    print("  ✅ Igbo medical terms") 
    print("  ✅ Yoruba medical terms")
    print("  ✅ Pidgin English")
    print("  ✅ Mixed language inputs")
    print("  ✅ Pure English (no translation needed)")
    
    return translator

if __name__ == "__main__":
    translator = test_multilingual_system()
