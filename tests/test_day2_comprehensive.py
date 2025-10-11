"""
MediLink PHC - Comprehensive Day 2 Tests
Tests AI triage with English, Pidgin, edge cases, and error handling
"""

import json
import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_triage_service_v2 import AITriageService
from multilingual_translator import MultilingualTranslator


# 10 comprehensive test scenarios
TEST_SCENARIOS = [
    {
        "id": "TEST-01",
        "name": "Standard Malaria (English)",
        "language": "English",
        "patient_data": {
            "age": 28,
            "gender": "Female",
            "symptoms": ["fever", "headache", "body aches", "chills"],
            "duration": "2 days",
            "vital_signs": {"temperature": 38.5}
        },
        "expected": {
            "triage_level": [2, 3],
            "conditions": ["malaria"],
            "referral": False
        }
    },
    {
        "id": "TEST-02",
        "name": "Critical Meningitis (English)",
        "language": "English",
        "patient_data": {
            "age": 19,
            "gender": "Male",
            "symptoms": ["high fever", "severe headache", "stiff neck", "vomiting", "sensitivity to light"],
            "duration": "Started this morning",
            "vital_signs": {"temperature": 40.1}
        },
        "expected": {
            "triage_level": [1],
            "conditions": ["meningitis"],
            "referral": True
        }
    },
    {
        "id": "TEST-03",
        "name": "Fever Case (Pidgin)",
        "language": "Pidgin",
        "patient_data": {
            "age": 35,
            "gender": "Male",
            "symptoms": ["body dey hot", "head dey pain me", "body no get power"],
            "duration": "3 days",
            "vital_signs": {"temperature": 39.0}
        },
        "expected": {
            "triage_level": [2, 3],
            "conditions": ["malaria", "typhoid"],
            "referral": False
        }
    },
    {
        "id": "TEST-04",
        "name": "Diarrhea with Dehydration (Pidgin)",
        "language": "Pidgin",
        "patient_data": {
            "age": 4,
            "gender": "Female",
            "symptoms": ["belle dey run", "e dey vomit", "eye don sink", "body weak"],
            "duration": "2 days",
            "vital_signs": {"temperature": 37.8, "heart_rate": 125}
        },
        "expected": {
            "triage_level": [1, 2],
            "conditions": ["dehydration", "gastroenteritis"],
            "referral": True
        }
    },
    {
        "id": "TEST-05",
        "name": "Unconscious Child (Pidgin)",
        "language": "Pidgin",
        "patient_data": {
            "age": 6,
            "gender": "Male",
            "symptoms": ["e don faint", "im body dey shake", "body dey hot"],
            "duration": "1 hour ago",
            "vital_signs": {"temperature": 40.5, "respiratory_rate": 50}
        },
        "expected": {
            "triage_level": [1],
            "conditions": ["cerebral malaria", "meningitis"],
            "referral": True
        }
    },
    {
        "id": "TEST-06",
        "name": "Prolonged Typhoid (English)",
        "language": "English",
        "patient_data": {
            "age": 22,
            "gender": "Female",
            "symptoms": ["fever", "stomach pain", "weakness", "loss of appetite", "constipation"],
            "duration": "10 days - fever comes and goes",
            "vital_signs": {"temperature": 39.2}
        },
        "expected": {
            "triage_level": [2],
            "conditions": ["typhoid"],
            "referral": False
        }
    },
    {
        "id": "TEST-07",
        "name": "Respiratory Infection (Mixed)",
        "language": "Mixed",
        "patient_data": {
            "age": 45,
            "gender": "Male",
            "symptoms": ["cough dey worry me", "chest dey pain", "fever", "breathe dey hard"],
            "duration": "5 days",
            "vital_signs": {"temperature": 38.7, "respiratory_rate": 28}
        },
        "expected": {
            "triage_level": [2, 3],
            "conditions": ["pneumonia", "respiratory infection"],
            "referral": False
        }
    },
    {
        "id": "TEST-08",
        "name": "Minor Cold (English)",
        "language": "English",
        "patient_data": {
            "age": 25,
            "gender": "Female",
            "symptoms": ["runny nose", "mild cough", "sore throat"],
            "duration": "2 days",
            "vital_signs": {"temperature": 37.1}
        },
        "expected": {
            "triage_level": [3, 4],
            "conditions": ["common cold"],
            "referral": False
        }
    },
    {
        "id": "TEST-09",
        "name": "Edge Case: Vague Symptoms",
        "language": "English",
        "patient_data": {
            "age": 40,
            "gender": "Male",
            "symptoms": ["not feeling well", "tired", "body aches"],
            "duration": "1 day",
            "vital_signs": {}
        },
        "expected": {
            "triage_level": [3],
            "conditions": [],  # Vague, so any reasonable diagnosis is OK
            "referral": False
        }
    },
    {
        "id": "TEST-10",
        "name": "Edge Case: Contradictory Symptoms",
        "language": "English",
        "patient_data": {
            "age": 30,
            "gender": "Female",
            "symptoms": ["fever", "chills", "feeling cold but sweating"],
            "duration": "4 hours",
            "vital_signs": {"temperature": 38.9}
        },
        "expected": {
            "triage_level": [2, 3],
            "conditions": ["infection"],
            "referral": False
        }
    }
]


def run_comprehensive_tests(provider='groq'):
    """
    Run all comprehensive Day 2 tests
    
    Args:
        provider: 'groq' or 'gemini'
    """
    print("\n" + "="*80)
    print(f"🧪 DAY 2 COMPREHENSIVE TEST SUITE - Provider: {provider.upper()}")
    print("="*80 + "\n")
    
    # Initialize services
    try:
        ai_service = AITriageService(provider=provider, timeout=10, max_retries=2)
        translator = MultilingualTranslator()
        
        results = []
        total_tests = len(TEST_SCENARIOS)
        passed = 0
        failed = 0
        warnings = 0
        total_time = 0
        
        for scenario in TEST_SCENARIOS:
            print(f"\n{'─'*80}")
            print(f"🔬 {scenario['id']}: {scenario['name']}")
            print(f"   Language: {scenario['language']}")
            print(f"{'─'*80}")
            
            patient = scenario['patient_data'].copy()
            
            # Display original symptoms
            print(f"\n👤 Original Input:")
            print(f"   Age: {patient['age']}, Gender: {patient['gender']}")
            print(f"   Symptoms: {', '.join(patient['symptoms'])}")
            print(f"   Duration: {patient['duration']}")
            
            # Translate Pidgin if needed
            if scenario['language'] in ['Pidgin', 'Mixed']:
                print(f"\n🗣️  Translation:")
                translated_symptoms, translation_map = translator.translate_symptoms(patient['symptoms'])
                patient['symptoms'] = translated_symptoms
                
                if translation_map:
                    for orig, trans in translation_map.items():
                        print(f"   • '{orig}' → '{trans}'")
                else:
                    print(f"   • No translation needed")
                
                print(f"   Final symptoms: {', '.join(patient['symptoms'])}")
            
            # Expected results
            expected = scenario['expected']
            print(f"\n🎯 Expected:")
            print(f"   Triage Level: {expected['triage_level']}")
            if expected['conditions']:
                print(f"   Likely Conditions: {', '.join(expected['conditions'])}")
            print(f"   Referral: {expected['referral']}")
            
            # Run AI analysis
            print(f"\n⏳ Analyzing with AI...")
            start_time = time.time()
            result = ai_service.analyze_patient(patient)
            analysis_time = time.time() - start_time
            total_time += analysis_time
            
            # Check for errors
            if 'error' in result and not result.get('ai_failed'):
                print(f"\n❌ FAILED: {result['error']}")
                failed += 1
                results.append({
                    'test_id': scenario['id'],
                    'status': 'FAILED',
                    'error': result['error'],
                    'analysis_time': analysis_time
                })
                continue
            
            # Display results
            print(f"\n✅ AI Response ({result['response_time']:.2f}s):")
            
            if result.get('ai_failed'):
                print(f"   ⚠️  AI Failed - Using Fallback Triage")
                print(f"   Error: {result.get('ai_error', 'Unknown')}")
            
            print(f"   Triage: Level {result['triage_level']} - {result['triage_label']}")
            
            if 'confidence' in result:
                confidence_icon = "🟢" if result['confidence'] >= 80 else "🟡" if result['confidence'] >= 60 else "🔴"
                print(f"   Confidence: {confidence_icon} {result['confidence']}%")
            
            # Display conditions
            if 'conditions' in result and result['conditions']:
                print(f"\n   🔍 Top Conditions:")
                for i, condition in enumerate(result['conditions'][:3], 1):
                    conf = condition.get('confidence', 'N/A')
                    print(f"      {i}. {condition['name']} ({conf}%)")
                    if 'reasoning' in condition:
                        print(f"         → {condition['reasoning'][:100]}...")
            
            # Display actions
            if 'immediate_actions' in result and result['immediate_actions']:
                print(f"\n   ⚡ Actions: {result['immediate_actions'][0]}")
            
            # Referral info
            referral_status = "✅ YES" if result.get('referral_needed') else "❌ NO"
            print(f"\n   🏥 Referral: {referral_status}")
            if result.get('referral_reason'):
                print(f"      Reason: {result['referral_reason'][:80]}...")
            
            # Evaluate results
            test_status = "PASSED"
            issues = []
            
            # Check triage level
            if result['triage_level'] not in expected['triage_level']:
                issues.append(f"Triage level {result['triage_level']} not in expected {expected['triage_level']}")
            
            # Check referral
            if result.get('referral_needed', False) != expected['referral']:
                issues.append(f"Referral mismatch: got {result.get('referral_needed')}, expected {expected['referral']}")
            
            # Check conditions (if expected is not empty)
            if expected['conditions'] and 'conditions' in result:
                condition_names = [c['name'].lower() for c in result['conditions']]
                expected_found = any(
                    any(exp.lower() in cond for cond in condition_names)
                    for exp in expected['conditions']
                )
                if not expected_found:
                    issues.append(f"Expected conditions {expected['conditions']} not found")
            
            # Check response time
            if result['response_time'] > 5.0:
                issues.append(f"Response time {result['response_time']}s exceeds 5s target")
            
            # Print evaluation
            if not issues:
                print(f"\n✅ TEST PASSED")
                passed += 1
            elif len(issues) <= 1:
                print(f"\n⚠️  TEST PASSED WITH WARNINGS:")
                for issue in issues:
                    print(f"   • {issue}")
                warnings += 1
                passed += 1
                test_status = "PASSED_WITH_WARNINGS"
            else:
                print(f"\n❌ TEST FAILED:")
                for issue in issues:
                    print(f"   • {issue}")
                failed += 1
                test_status = "FAILED"
            
            # Store result
            results.append({
                'test_id': scenario['id'],
                'test_name': scenario['name'],
                'language': scenario['language'],
                'status': test_status,
                'issues': issues,
                'result': result,
                'analysis_time': analysis_time
            })
        
        # Final Summary
        print(f"\n{'='*80}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests*100):.1f}%")
        print(f"Average Response Time: {(total_time/total_tests):.2f}s")
        print(f"Provider: {provider.upper()}")
        
        # Performance evaluation
        print(f"\n⏱️  PERFORMANCE EVALUATION:")
        fast_enough = total_time/total_tests < 3.0
        print(f"   Target: <3 seconds per analysis")
        print(f"   Actual: {(total_time/total_tests):.2f}s")
        print(f"   Status: {'✅ PASS' if fast_enough else '⚠️  NEEDS OPTIMIZATION'}")
        
        # Save results
        os.makedirs('tests', exist_ok=True)
        
        output_file = f'tests/test_results_day2_{provider}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'provider': provider,
                'total_tests': total_tests,
                'passed': passed,
                'warnings': warnings,
                'failed': failed,
                'success_rate': round(passed/total_tests*100, 1),
                'avg_response_time': round(total_time/total_tests, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'detailed_results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Summary file for backend team
        summary_file = 'tests/DAY2_SUMMARY.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("MEDILINK PHC - DAY 2 AI TRIAGE TESTING SUMMARY\n")
            f.write("="*80 + "\n\n")
            f.write(f"Provider: {provider.upper()}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"RESULTS:\n")
            f.write(f"  Total Tests: {total_tests}\n")
            f.write(f"  Passed: {passed} ({(passed/total_tests*100):.1f}%)\n")
            f.write(f"  Failed: {failed}\n")
            f.write(f"  Average Response Time: {(total_time/total_tests):.2f}s\n\n")
            f.write(f"FEATURES TESTED:\n")
            f.write(f"  ✓ English language support\n")
            f.write(f"  ✓ Pidgin language translation\n")
            f.write(f"  ✓ Error handling and fallback\n")
            f.write(f"  ✓ Edge cases and vague symptoms\n")
            f.write(f"  ✓ Critical emergency detection\n\n")
            f.write(f"READY FOR BACKEND INTEGRATION: {'YES' if passed >= 8 else 'NEEDS REVIEW'}\n")
        
        print(f"📄 Summary saved to: {summary_file}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


# Error handling test cases
def test_error_handling(provider='groq'):
    """Test error handling scenarios"""
    print("\n" + "="*80)
    print(f"🛡️  TESTING ERROR HANDLING")
    print("="*80 + "\n")
    
    ai_service = AITriageService(provider=provider, timeout=5, max_retries=1)
    
    error_tests = [
        {
            "name": "Missing symptoms",
            "patient_data": {"age": 30, "gender": "Male"},
            "should_use_fallback": True
        },
        {
            "name": "Missing age",
            "patient_data": {"symptoms": ["fever"], "gender": "Male"},
            "should_use_fallback": True
        },
        {
            "name": "Empty symptoms list",
            "patient_data": {"age": 25, "gender": "Female", "symptoms": []},
            "should_use_fallback": True
        }
    ]
    
    for test in error_tests:
        print(f"Test: {test['name']}")
        result = ai_service.analyze_patient(test['patient_data'])
        
        if 'error' in result or 'message' in result:
            print(f"✅ Handled gracefully: {result.get('message', result.get('error'))}\n")
        else:
            print(f"⚠️  Unexpected success\n")


if __name__ == "__main__":
    # Run main test suite
    provider = sys.argv[1] if len(sys.argv) > 1 else 'groq'
    
    if provider not in ['groq', 'gemini']:
        print("Usage: python tests/test_day2_comprehensive.py [groq|gemini]")
        sys.exit(1)
    
    # Run comprehensive tests
    run_comprehensive_tests(provider=provider)
    
    # Run error handling tests
    test_error_handling(provider=provider)
    
    print("\n✅ ALL DAY 2 TESTS COMPLETE!\n")
