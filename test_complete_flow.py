"""
MediLink PHC - End-to-End Testing Script
Tests complete user flow from multilingual input to AI triage to backend integration
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add src directory to path
sys.path.insert(0, 'src')

# Import our modules
from multilingual_translator import MultilingualTranslator
from backend_prediction_service import BackendPredictionService

class EndToEndTester:
    """Test the complete MediLink PHC workflow"""
    
    def __init__(self):
        self.translator = MultilingualTranslator()
        self.prediction_service = BackendPredictionService()
        self.test_results = []
    
    def test_complete_flow(self, test_scenarios: List[Dict]) -> Dict:
        """
        Test complete user flow for multiple scenarios
        
        Args:
            test_scenarios: List of test scenarios
        
        Returns:
            Complete test results
        """
        print("\n" + "="*80)
        print("🧪 MEDILINK PHC - END-TO-END TESTING")
        print("="*80 + "\n")
        
        total_tests = len(test_scenarios)
        passed_tests = 0
        failed_tests = 0
        total_time = 0
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'─'*80}")
            print(f"🔬 SCENARIO {i}: {scenario['name']}")
            print(f"{'─'*80}")
            
            # Test the complete flow
            result = self._test_single_scenario(scenario, i)
            self.test_results.append(result)
            
            if result['overall_success']:
                passed_tests += 1
                print(f"✅ SCENARIO {i} PASSED")
            else:
                failed_tests += 1
                print(f"❌ SCENARIO {i} FAILED")
            
            total_time += result['total_time']
            
            # Show summary
            print(f"\n📊 SCENARIO {i} SUMMARY:")
            print(f"   Total Time: {result['total_time']:.2f}s")
            print(f"   Translation: {'✅' if result['translation_success'] else '❌'}")
            print(f"   AI Triage: {'✅' if result['triage_success'] else '❌'}")
            print(f"   Backend Integration: {'✅' if result['backend_success'] else '❌'}")
            
            if result['errors']:
                print(f"   Errors: {len(result['errors'])}")
                for error in result['errors'][:2]:  # Show first 2 errors
                    print(f"     • {error}")
        
        # Overall summary
        print(f"\n{'='*80}")
        print(f"📊 END-TO-END TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Scenarios: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"Average Time per Scenario: {(total_time/total_tests):.2f}s")
        
        # Performance evaluation
        print(f"\n⏱️  PERFORMANCE EVALUATION:")
        avg_time = total_time / total_tests
        if avg_time < 5.0:
            print(f"   ✅ Excellent: {avg_time:.2f}s average")
        elif avg_time < 10.0:
            print(f"   ✅ Good: {avg_time:.2f}s average")
        else:
            print(f"   ⚠️  Needs Optimization: {avg_time:.2f}s average")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "average_time": avg_time,
            "detailed_results": self.test_results
        }
    
    def _test_single_scenario(self, scenario: Dict, scenario_num: int) -> Dict:
        """Test a single scenario end-to-end"""
        start_time = time.time()
        errors = []
        
        # Step 1: Multilingual Translation
        print(f"\n🗣️  STEP 1: Multilingual Translation")
        translation_start = time.time()
        
        try:
            original_symptoms = scenario['patient_data']['symptoms']
            translated_symptoms, translation_map = self.translator.translate_symptoms(original_symptoms)
            
            translation_time = time.time() - translation_start
            
            print(f"   Original: {original_symptoms}")
            print(f"   Translated: {translated_symptoms}")
            
            if translation_map:
                print(f"   Translations Made:")
                for orig, trans in translation_map.items():
                    print(f"     • '{orig}' → '{trans}'")
            else:
                print(f"   No translation needed")
            
            translation_success = True
            
        except Exception as e:
            translation_time = time.time() - translation_start
            translation_success = False
            errors.append(f"Translation failed: {str(e)}")
            print(f"   ❌ Translation failed: {e}")
        
        # Step 2: AI Triage Analysis
        print(f"\n🤖 STEP 2: AI Triage Analysis")
        triage_start = time.time()
        
        try:
            # Update patient data with translated symptoms
            patient_data = scenario['patient_data'].copy()
            patient_data['symptoms'] = translated_symptoms
            
            # Use backend service for triage
            triage_result = self.prediction_service.analyze_triage(patient_data)
            
            triage_time = time.time() - triage_start
            
            if triage_result.get('success'):
                triage_data = triage_result['data']
                print(f"   ✅ Triage Level: {triage_data['triage_level']} - {triage_data['triage_label']}")
                print(f"   Confidence: {triage_data.get('confidence', 'N/A')}")
                print(f"   Response Time: {triage_data['response_time']:.2f}s")
                
                if 'conditions' in triage_data and triage_data['conditions']:
                    print(f"   Top Condition: {triage_data['conditions'][0]['name']}")
                
                triage_success = True
            else:
                triage_success = False
                errors.append(f"Triage failed: {triage_result.get('error', {}).get('message', 'Unknown error')}")
                print(f"   ❌ Triage failed: {triage_result.get('error', {}).get('message', 'Unknown error')}")
            
        except Exception as e:
            triage_time = time.time() - triage_start
            triage_success = False
            errors.append(f"Triage analysis failed: {str(e)}")
            print(f"   ❌ Triage analysis failed: {e}")
        
        # Step 3: Backend Integration Test
        print(f"\n🔗 STEP 3: Backend Integration Test")
        backend_start = time.time()
        
        try:
            # Test other backend services
            forecast_result = self.prediction_service.get_patient_forecast("TEST_PHC", days_ahead=7)
            outbreak_result = self.prediction_service.check_outbreak(
                "Malaria", "Test Region", 25, [20, 22, 18, 25, 21]
            )
            resource_result = self.prediction_service.recommend_resources(
                100, {"nurses": 3, "doctors": 1, "pharmacists": 1}
            )
            
            backend_time = time.time() - backend_start
            
            # Check if all services are working
            services_working = all([
                forecast_result.get('success', False),
                outbreak_result.get('success', False),
                resource_result.get('success', False)
            ])
            
            if services_working:
                print(f"   ✅ All backend services working")
                print(f"   Forecast: Available")
                print(f"   Outbreak Detection: Available")
                print(f"   Resource Optimization: Available")
                backend_success = True
            else:
                backend_success = False
                errors.append("Some backend services failed")
                print(f"   ⚠️  Some backend services failed")
            
        except Exception as e:
            backend_time = time.time() - backend_start
            backend_success = False
            errors.append(f"Backend integration failed: {str(e)}")
            print(f"   ❌ Backend integration failed: {e}")
        
        total_time = time.time() - start_time
        
        return {
            "scenario_num": scenario_num,
            "scenario_name": scenario['name'],
            "total_time": total_time,
            "translation_success": translation_success,
            "translation_time": translation_time,
            "triage_success": triage_success,
            "triage_time": triage_time,
            "backend_success": backend_success,
            "backend_time": backend_time,
            "overall_success": translation_success and triage_success and backend_success,
            "errors": errors
        }
    
    def generate_test_report(self, results: Dict) -> str:
        """Generate a comprehensive test report"""
        report = f"""
🏥 MEDILINK PHC - END-TO-END TEST REPORT
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RESULTS:
{'─'*40}
Total Scenarios Tested: {results['total_tests']}
Passed: {results['passed_tests']} ({(results['passed_tests']/results['total_tests']*100):.1f}%)
Failed: {results['failed_tests']}
Average Time per Scenario: {results['average_time']:.2f}s

PERFORMANCE EVALUATION:
{'─'*40}
"""
        
        if results['average_time'] < 5.0:
            report += "✅ EXCELLENT: System responds quickly\n"
        elif results['average_time'] < 10.0:
            report += "✅ GOOD: System performance is acceptable\n"
        else:
            report += "⚠️  NEEDS OPTIMIZATION: System is slow\n"
        
        report += f"""
DETAILED RESULTS:
{'─'*40}
"""
        
        for result in results['detailed_results']:
            status = "✅ PASSED" if result['overall_success'] else "❌ FAILED"
            report += f"""
Scenario {result['scenario_num']}: {result['scenario_name']} - {status}
  Total Time: {result['total_time']:.2f}s
  Translation: {'✅' if result['translation_success'] else '❌'} ({result['translation_time']:.2f}s)
  AI Triage: {'✅' if result['triage_success'] else '❌'} ({result['triage_time']:.2f}s)
  Backend: {'✅' if result['backend_success'] else '❌'} ({result['backend_time']:.2f}s)
"""
            
            if result['errors']:
                report += f"  Errors: {len(result['errors'])}\n"
                for error in result['errors']:
                    report += f"    • {error}\n"
        
        report += f"""
READY FOR PRODUCTION: {'YES' if results['success_rate'] >= 80 else 'NEEDS REVIEW'}
"""
        
        return report


def create_test_scenarios() -> List[Dict]:
    """Create comprehensive test scenarios"""
    return [
        {
            "name": "Hausa Fever Case",
            "patient_data": {
                "age": 28,
                "gender": "Female",
                "symptoms": ["zazzabi", "ciwon kai", "rashin kuzari"],
                "duration": "2 days",
                "vital_signs": {"temperature": 38.5}
            },
            "expected_language": "hausa",
            "expected_triage": [2, 3]
        },
        {
            "name": "Igbo Diarrhea Emergency",
            "patient_data": {
                "age": 4,
                "gender": "Male",
                "symptoms": ["mgbawa", "agba", "adighi ike"],
                "duration": "1 day",
                "vital_signs": {"temperature": 37.8, "heart_rate": 125}
            },
            "expected_language": "igbo",
            "expected_triage": [1, 2]
        },
        {
            "name": "Yoruba Breathing Problem",
            "patient_data": {
                "age": 45,
                "gender": "Female",
                "symptoms": ["ipalara emi", "aya n dun", "ikọ"],
                "duration": "3 days",
                "vital_signs": {"temperature": 38.7, "respiratory_rate": 28}
            },
            "expected_language": "yoruba",
            "expected_triage": [2, 3]
        },
        {
            "name": "Pidgin Emergency",
            "patient_data": {
                "age": 6,
                "gender": "Male",
                "symptoms": ["e don faint", "im body dey shake", "breath dey hard"],
                "duration": "1 hour ago",
                "vital_signs": {"temperature": 40.5, "respiratory_rate": 50}
            },
            "expected_language": "pidgin",
            "expected_triage": [1]
        },
        {
            "name": "Mixed Languages",
            "patient_data": {
                "age": 30,
                "gender": "Female",
                "symptoms": ["zazzabi", "body dey pain", "mgbawa"],
                "duration": "2 days",
                "vital_signs": {"temperature": 39.0}
            },
            "expected_language": "mixed",
            "expected_triage": [2, 3]
        },
        {
            "name": "English Standard Case",
            "patient_data": {
                "age": 25,
                "gender": "Male",
                "symptoms": ["headache", "fever", "cough"],
                "duration": "3 days",
                "vital_signs": {"temperature": 38.2}
            },
            "expected_language": "english",
            "expected_triage": [3, 4]
        },
        {
            "name": "Edge Case - Vague Symptoms",
            "patient_data": {
                "age": 40,
                "gender": "Male",
                "symptoms": ["not feeling well", "tired", "weak"],
                "duration": "1 day",
                "vital_signs": {}
            },
            "expected_language": "english",
            "expected_triage": [3]
        },
        {
            "name": "Edge Case - Pregnant Patient",
            "patient_data": {
                "age": 25,
                "gender": "Female",
                "symptoms": ["fever", "headache"],
                "duration": "1 day",
                "vital_signs": {"temperature": 38.2},
                "medical_history": "20 weeks pregnant"
            },
            "expected_language": "english",
            "expected_triage": [2]
        }
    ]


def main():
    """Run end-to-end testing"""
    print("🚀 Starting MediLink PHC End-to-End Testing...")
    
    # Create tester
    tester = EndToEndTester()
    
    # Create test scenarios
    scenarios = create_test_scenarios()
    
    # Run tests
    results = tester.test_complete_flow(scenarios)
    
    # Generate report
    report = tester.generate_test_report(results)
    
    # Save report
    with open('reports/end_to_end_test_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Test report saved to: reports/end_to_end_test_report.txt")
    print(f"\n🎯 END-TO-END TESTING COMPLETE!")
    
    return results


if __name__ == "__main__":
    results = main()
