"""
MediLink PHC - AI Triage Evaluation Script
Evaluates AI triage accuracy against ground truth test dataset
"""

import pandas as pd
import time
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add src directory to path
sys.path.insert(0, 'src')

# Import our modules
from ai_triage_service_v2 import AITriageService
from multilingual_translator import MultilingualTranslator

class AITriageEvaluator:
    """Evaluates AI triage performance against ground truth"""
    
    def __init__(self):
        self.translator = MultilingualTranslator()
        self.triage_service = AITriageService()
        self.results = []
        
    def load_test_dataset(self, csv_path: str = 'test_dataset.csv') -> pd.DataFrame:
        """Load the test dataset"""
        if not os.path.exists(csv_path):
            print(f"❌ Test dataset not found: {csv_path}")
            print("Please run data/create_test_dataset.py first")
            return None
        
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded test dataset: {len(df)} cases")
        return df
    
    def evaluate_single_case(self, case: pd.Series) -> Dict[str, Any]:
        """Evaluate a single test case"""
        case_id = case['case_id']
        
        # Prepare patient data
        symptoms = case['symptoms'].split(',')
        patient_data = {
            'age': case['age'],
            'gender': case['gender'],
            'symptoms': symptoms,
            'duration': case['duration'],
            'vital_signs': self._parse_vital_signs(case['vital_signs']),
            'medical_history': case['medical_history'] if pd.notna(case['medical_history']) else None
        }
        
        # Ground truth
        ground_truth = {
            'triage_level': case['correct_triage_level'],
            'triage_label': case['correct_triage_label'],
            'diagnosis': case['correct_diagnosis'],
            'action': case['correct_action'],
            'referral': case['correct_referral']
        }
        
        # Run AI analysis
        start_time = time.time()
        try:
            ai_result = self.triage_service.analyze_patient(patient_data)
            response_time = time.time() - start_time
            
            # Parse AI result
            ai_triage_level = ai_result.get('triage_level')
            ai_triage_label = ai_result.get('triage_label', 'Unknown')
            ai_conditions = ai_result.get('conditions', [])
            ai_referral = ai_result.get('referral_needed', False)
            ai_confidence = ai_result.get('confidence', 0)
            
            # Calculate accuracy metrics
            triage_accuracy = self._calculate_triage_accuracy(ai_triage_level, ground_truth['triage_level'])
            diagnosis_accuracy = self._calculate_diagnosis_accuracy(ai_conditions, ground_truth['diagnosis'])
            referral_accuracy = ai_referral == ground_truth['referral']
            
            result = {
                'case_id': case_id,
                'age': case['age'],
                'gender': case['gender'],
                'case_type': case['case_type'],
                'symptoms': symptoms,
                'ground_truth': ground_truth,
                'ai_result': {
                    'triage_level': ai_triage_level,
                    'triage_label': ai_triage_label,
                    'conditions': ai_conditions,
                    'referral_needed': ai_referral,
                    'confidence': ai_confidence,
                    'response_time': response_time
                },
                'accuracy_metrics': {
                    'triage_accuracy': triage_accuracy,
                    'diagnosis_accuracy': diagnosis_accuracy,
                    'referral_accuracy': referral_accuracy,
                    'overall_accuracy': (triage_accuracy + diagnosis_accuracy + referral_accuracy) / 3
                },
                'success': True,
                'error': None
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'case_id': case_id,
                'age': case['age'],
                'gender': case['gender'],
                'case_type': case['case_type'],
                'symptoms': symptoms,
                'ground_truth': ground_truth,
                'ai_result': None,
                'accuracy_metrics': {
                    'triage_accuracy': 0,
                    'diagnosis_accuracy': 0,
                    'referral_accuracy': 0,
                    'overall_accuracy': 0
                },
                'success': False,
                'error': str(e),
                'response_time': response_time
            }
        
        return result
    
    def _parse_vital_signs(self, vital_signs_str: str) -> Dict[str, Any]:
        """Parse vital signs string into dictionary"""
        if pd.isna(vital_signs_str) or vital_signs_str == 'normal':
            return {}
        
        vitals = {}
        parts = vital_signs_str.split(',')
        
        for part in parts:
            part = part.strip()
            if 'temperature' in part:
                try:
                    temp = float(part.split('_')[1])
                    vitals['temperature'] = temp
                except:
                    pass
            elif 'heart_rate' in part:
                try:
                    hr = int(part.split('_')[2])
                    vitals['heart_rate'] = hr
                except:
                    pass
            elif 'respiratory_rate' in part:
                try:
                    rr = int(part.split('_')[2])
                    vitals['respiratory_rate'] = rr
                except:
                    pass
            elif 'blood_pressure' in part:
                try:
                    bp_parts = part.split('_')
                    systolic = int(bp_parts[2])
                    diastolic = int(bp_parts[3])
                    vitals['blood_pressure'] = f"{systolic}/{diastolic}"
                except:
                    pass
            elif 'oxygen_saturation' in part:
                try:
                    spo2 = int(part.split('_')[2])
                    vitals['oxygen_saturation'] = spo2
                except:
                    pass
        
        return vitals
    
    def _calculate_triage_accuracy(self, ai_level: int, ground_truth_level: int) -> float:
        """Calculate triage accuracy with tolerance"""
        if ai_level is None:
            return 0.0
        
        # Allow ±1 level tolerance
        if abs(ai_level - ground_truth_level) <= 1:
            if ai_level == ground_truth_level:
                return 1.0  # Perfect match
            else:
                return 0.7  # Close match
        else:
            return 0.0  # Poor match
    
    def _calculate_diagnosis_accuracy(self, ai_conditions: List[Dict], ground_truth_diagnosis: str) -> float:
        """Calculate diagnosis accuracy"""
        if not ai_conditions:
            return 0.0
        
        # Check if ground truth diagnosis appears in AI conditions
        ground_truth_lower = ground_truth_diagnosis.lower()
        
        for condition in ai_conditions:
            condition_name = condition.get('name', '').lower()
            if ground_truth_lower in condition_name or condition_name in ground_truth_lower:
                return 1.0
        
        # Check for partial matches
        ground_truth_words = set(ground_truth_lower.split())
        for condition in ai_conditions:
            condition_words = set(condition.get('name', '').lower().split())
            if len(ground_truth_words.intersection(condition_words)) >= 2:
                return 0.5
        
        return 0.0
    
    def evaluate_all_cases(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate all test cases"""
        print(f"\n🧪 EVALUATING AI TRIAGE AGAINST {len(df)} TEST CASES")
        print("=" * 60)
        
        total_cases = len(df)
        successful_cases = 0
        failed_cases = 0
        
        # Initialize counters
        triage_correct = 0
        triage_close = 0
        triage_wrong = 0
        diagnosis_correct = 0
        referral_correct = 0
        
        total_response_time = 0
        
        # Breakdown by triage level
        level_stats = {1: {'correct': 0, 'close': 0, 'wrong': 0, 'total': 0},
                      2: {'correct': 0, 'close': 0, 'wrong': 0, 'total': 0},
                      3: {'correct': 0, 'close': 0, 'wrong': 0, 'total': 0},
                      4: {'correct': 0, 'close': 0, 'wrong': 0, 'total': 0}}
        
        # Breakdown by case type
        type_stats = {}
        
        for idx, case in df.iterrows():
            print(f"\n🔬 Case {case['case_id']}: {case['case_type']} - {case['symptoms'][:50]}...")
            
            result = self.evaluate_single_case(case)
            self.results.append(result)
            
            if result['success']:
                successful_cases += 1
                total_response_time += result['ai_result']['response_time']
                
                # Triage accuracy
                triage_acc = result['accuracy_metrics']['triage_accuracy']
                if triage_acc == 1.0:
                    triage_correct += 1
                    level_stats[case['correct_triage_level']]['correct'] += 1
                elif triage_acc == 0.7:
                    triage_close += 1
                    level_stats[case['correct_triage_level']]['close'] += 1
                else:
                    triage_wrong += 1
                    level_stats[case['correct_triage_level']]['wrong'] += 1
                
                level_stats[case['correct_triage_level']]['total'] += 1
                
                # Diagnosis accuracy
                if result['accuracy_metrics']['diagnosis_accuracy'] > 0:
                    diagnosis_correct += 1
                
                # Referral accuracy
                if result['accuracy_metrics']['referral_accuracy']:
                    referral_correct += 1
                
                # Case type stats
                case_type = case['case_type']
                if case_type not in type_stats:
                    type_stats[case_type] = {'correct': 0, 'total': 0}
                type_stats[case_type]['total'] += 1
                if triage_acc >= 0.7:
                    type_stats[case_type]['correct'] += 1
                
                print(f"   ✅ AI Level: {result['ai_result']['triage_level']} vs Expected: {case['correct_triage_level']}")
                print(f"   📊 Triage Accuracy: {triage_acc:.1f}")
                print(f"   ⏱️  Response Time: {result['ai_result']['response_time']:.2f}s")
                
            else:
                failed_cases += 1
                print(f"   ❌ Failed: {result['error']}")
        
        # Calculate overall metrics
        avg_response_time = total_response_time / successful_cases if successful_cases > 0 else 0
        
        # Triage accuracy (with tolerance)
        triage_accuracy_with_tolerance = (triage_correct + triage_close) / total_cases
        
        # Diagnosis accuracy
        diagnosis_accuracy = diagnosis_correct / total_cases
        
        # Referral accuracy
        referral_accuracy = referral_correct / total_cases
        
        # Overall accuracy
        overall_accuracy = (triage_accuracy_with_tolerance + diagnosis_accuracy + referral_accuracy) / 3
        
        # Compile results
        evaluation_results = {
            'summary': {
                'total_cases': total_cases,
                'successful_cases': successful_cases,
                'failed_cases': failed_cases,
                'success_rate': successful_cases / total_cases,
                'avg_response_time': avg_response_time,
                'triage_accuracy': triage_accuracy_with_tolerance,
                'diagnosis_accuracy': diagnosis_accuracy,
                'referral_accuracy': referral_accuracy,
                'overall_accuracy': overall_accuracy
            },
            'triage_breakdown': {
                'perfect_matches': triage_correct,
                'close_matches': triage_close,
                'wrong_matches': triage_wrong,
                'perfect_rate': triage_correct / total_cases,
                'close_rate': triage_close / total_cases,
                'wrong_rate': triage_wrong / total_cases
            },
            'level_stats': level_stats,
            'type_stats': type_stats,
            'detailed_results': self.results
        }
        
        return evaluation_results
    
    def generate_evaluation_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive evaluation report"""
        summary = results['summary']
        triage_breakdown = results['triage_breakdown']
        level_stats = results['level_stats']
        type_stats = results['type_stats']
        
        report = f"""
🏥 MEDILINK PHC - AI TRIAGE EVALUATION REPORT
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RESULTS:
{'─'*40}
Total Test Cases: {summary['total_cases']}
Successful Cases: {summary['successful_cases']} ({summary['success_rate']:.1%})
Failed Cases: {summary['failed_cases']}
Average Response Time: {summary['avg_response_time']:.2f}s

ACCURACY METRICS:
{'─'*40}
Triage Accuracy (±1 level): {summary['triage_accuracy']:.1%}
Diagnosis Accuracy: {summary['diagnosis_accuracy']:.1%}
Referral Accuracy: {summary['referral_accuracy']:.1%}
Overall Accuracy: {summary['overall_accuracy']:.1%}

TRIAGE BREAKDOWN:
{'─'*40}
Perfect Matches: {triage_breakdown['perfect_matches']} ({triage_breakdown['perfect_rate']:.1%})
Close Matches (±1): {triage_breakdown['close_matches']} ({triage_breakdown['close_rate']:.1%})
Wrong Matches (>±1): {triage_breakdown['wrong_matches']} ({triage_breakdown['wrong_rate']:.1%})

BY TRIAGE LEVEL:
{'─'*40}
"""
        
        for level in [1, 2, 3, 4]:
            stats = level_stats[level]
            if stats['total'] > 0:
                accuracy = (stats['correct'] + stats['close']) / stats['total']
                report += f"Level {level}: {stats['correct']}/{stats['total']} correct ({accuracy:.1%})\n"
        
        report += f"""
BY CASE TYPE:
{'─'*40}
"""
        
        for case_type, stats in type_stats.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                report += f"{case_type.replace('_', ' ').title()}: {stats['correct']}/{stats['total']} correct ({accuracy:.1%})\n"
        
        # Performance evaluation
        report += f"""
PERFORMANCE EVALUATION:
{'─'*40}
"""
        
        if summary['avg_response_time'] < 3.0:
            report += "✅ Response Time: EXCELLENT (<3s target met)\n"
        elif summary['avg_response_time'] < 5.0:
            report += "✅ Response Time: GOOD (<5s acceptable)\n"
        else:
            report += "⚠️  Response Time: NEEDS IMPROVEMENT (>5s)\n"
        
        if summary['triage_accuracy'] >= 0.8:
            report += "✅ Triage Accuracy: EXCELLENT (≥80% target met)\n"
        elif summary['triage_accuracy'] >= 0.7:
            report += "✅ Triage Accuracy: GOOD (≥70%)\n"
        else:
            report += "⚠️  Triage Accuracy: NEEDS IMPROVEMENT (<70%)\n"
        
        if summary['overall_accuracy'] >= 0.8:
            report += "✅ Overall Performance: EXCELLENT\n"
        elif summary['overall_accuracy'] >= 0.7:
            report += "✅ Overall Performance: GOOD\n"
        else:
            report += "⚠️  Overall Performance: NEEDS IMPROVEMENT\n"
        
        # Common errors analysis
        report += f"""
COMMON ERRORS ANALYSIS:
{'─'*40}
"""
        
        wrong_cases = [r for r in results['detailed_results'] if r['success'] and r['accuracy_metrics']['triage_accuracy'] == 0]
        
        if wrong_cases:
            report += f"Cases with wrong triage levels ({len(wrong_cases)}):\n"
            for case in wrong_cases[:5]:  # Show first 5
                ai_level = case['ai_result']['triage_level']
                expected_level = case['ground_truth']['triage_level']
                report += f"  • Case {case['case_id']}: AI={ai_level}, Expected={expected_level} ({case['symptoms'][:30]}...)\n"
        else:
            report += "No cases with completely wrong triage levels.\n"
        
        # Recommendations
        report += f"""
RECOMMENDATIONS:
{'─'*40}
"""
        
        if summary['triage_accuracy'] < 0.8:
            report += "• Improve triage prompt for better accuracy\n"
        
        if summary['avg_response_time'] > 3.0:
            report += "• Optimize AI provider settings for faster response\n"
        
        if triage_breakdown['wrong_rate'] > 0.1:
            report += "• Review cases with wrong triage levels\n"
        
        if summary['diagnosis_accuracy'] < 0.7:
            report += "• Enhance disease diagnosis accuracy\n"
        
        report += "• Continue monitoring performance with more test cases\n"
        report += "• Regular retraining with new data\n"
        
        report += f"""
READY FOR PRODUCTION: {'YES' if summary['overall_accuracy'] >= 0.8 and summary['avg_response_time'] <= 3.0 else 'NEEDS REVIEW'}
"""
        
        return report
    
    def save_results(self, results: Dict[str, Any], report: str):
        """Save evaluation results"""
        # Save detailed results as JSON
        with open('ai_evaluation_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save report as text
        with open('ai_evaluation_report.txt', 'w') as f:
            f.write(report)
        
        print(f"\n💾 Results saved:")
        print(f"   📄 ai_evaluation_results.json")
        print(f"   📄 ai_evaluation_report.txt")


def main():
    """Run AI triage evaluation"""
    print("🚀 Starting MediLink PHC AI Triage Evaluation...")
    
    # Create evaluator
    evaluator = AITriageEvaluator()
    
    # Load test dataset
    df = evaluator.load_test_dataset()
    if df is None:
        return
    
    # Run evaluation
    results = evaluator.evaluate_all_cases(df)
    
    # Generate report
    report = evaluator.generate_evaluation_report(results)
    
    # Save results
    evaluator.save_results(results, report)
    
    # Print summary
    print(f"\n📊 EVALUATION SUMMARY:")
    print(f"   Total Cases: {results['summary']['total_cases']}")
    print(f"   Success Rate: {results['summary']['success_rate']:.1%}")
    print(f"   Triage Accuracy: {results['summary']['triage_accuracy']:.1%}")
    print(f"   Diagnosis Accuracy: {results['summary']['diagnosis_accuracy']:.1%}")
    print(f"   Average Response Time: {results['summary']['avg_response_time']:.2f}s")
    print(f"   Overall Accuracy: {results['summary']['overall_accuracy']:.1%}")
    
    print(f"\n🎯 EVALUATION COMPLETE!")
    
    return results


if __name__ == "__main__":
    results = main()
