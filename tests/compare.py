# Create compare.py
import sys
sys.path.insert(0, 'src')

from ai_triage_service_v2 import compare_providers

test_patient = {
    'age': 30,
    'gender': 'Male',
    'symptoms': ['fever', 'headache', 'body aches'],
    'duration': '3 days',
    'vital_signs': {'temperature': 38.5}
}

results = compare_providers(test_patient)