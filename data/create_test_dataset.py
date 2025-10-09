"""
MediLink PHC - Day 5 Evaluation Dataset Generator
Creates comprehensive test dataset with ground truth for AI evaluation
"""

import pandas as pd
import random
from typing import List, Dict

def create_test_dataset() -> pd.DataFrame:
    """
    Create comprehensive test dataset with 50 cases and ground truth
    Based on WHO IMCI guidelines and Nigerian healthcare context
    """
    
    test_cases = [
        # CRITICAL CASES (Level 1) - 5 cases
        {
            "case_id": 1,
            "age": 5,
            "gender": "male",
            "symptoms": "high_fever,convulsions,unconscious",
            "duration": "1 hour",
            "vital_signs": "temperature_40.5,heart_rate_140",
            "medical_history": "none",
            "correct_triage_level": 1,
            "correct_triage_label": "Critical",
            "correct_diagnosis": "Febrile Seizure/Meningitis",
            "correct_action": "Immediate referral to hospital",
            "correct_referral": True,
            "case_type": "critical"
        },
        {
            "case_id": 2,
            "age": 3,
            "gender": "female",
            "symptoms": "difficulty_breathing,chest_indrawing,cyanosis",
            "duration": "2 hours",
            "vital_signs": "respiratory_rate_60,oxygen_saturation_85",
            "medical_history": "none",
            "correct_triage_level": 1,
            "correct_triage_label": "Critical",
            "correct_diagnosis": "Severe Pneumonia/Respiratory Distress",
            "correct_action": "Immediate oxygen, referral to hospital",
            "correct_referral": True,
            "case_type": "critical"
        },
        {
            "case_id": 3,
            "age": 8,
            "gender": "male",
            "symptoms": "severe_dehydration,sunken_eyes,unable_to_drink",
            "duration": "1 day",
            "vital_signs": "capillary_refill_4_seconds,weak_pulse",
            "medical_history": "diarrhea_3_days",
            "correct_triage_level": 1,
            "correct_triage_label": "Critical",
            "correct_diagnosis": "Severe Dehydration",
            "correct_action": "Immediate IV fluids, referral",
            "correct_referral": True,
            "case_type": "critical"
        },
        {
            "case_id": 4,
            "age": 25,
            "gender": "female",
            "symptoms": "severe_headache,stiff_neck,fever,vomiting",
            "duration": "1 day",
            "vital_signs": "temperature_39.5,blood_pressure_140_90",
            "medical_history": "none",
            "correct_triage_level": 1,
            "correct_triage_label": "Critical",
            "correct_diagnosis": "Meningitis",
            "correct_action": "Immediate referral, lumbar puncture",
            "correct_referral": True,
            "case_type": "critical"
        },
        {
            "case_id": 5,
            "age": 6,
            "gender": "male",
            "symptoms": "severe_bleeding,shock,pale_skin",
            "duration": "30 minutes",
            "vital_signs": "heart_rate_160,blood_pressure_80_50",
            "medical_history": "trauma_fall",
            "correct_triage_level": 1,
            "correct_triage_label": "Critical",
            "correct_diagnosis": "Hemorrhagic Shock",
            "correct_action": "Immediate blood transfusion, surgery",
            "correct_referral": True,
            "case_type": "critical"
        },
        
        # URGENT CASES (Level 2) - 25 cases
        {
            "case_id": 6,
            "age": 30,
            "gender": "male",
            "symptoms": "fever,headache,body_aches",
            "duration": "3 days",
            "vital_signs": "temperature_38.5",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Malaria",
            "correct_action": "Malaria RDT, start antimalarial",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 7,
            "age": 25,
            "gender": "female",
            "symptoms": "prolonged_fever,stomach_pain,weakness",
            "duration": "7 days",
            "vital_signs": "temperature_38.8",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Typhoid Fever",
            "correct_action": "Typhoid test, antibiotics",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 8,
            "age": 4,
            "gender": "male",
            "symptoms": "diarrhea,vomiting,dehydration_signs",
            "duration": "2 days",
            "vital_signs": "temperature_37.8,heart_rate_120",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Gastroenteritis/Cholera",
            "correct_action": "ORS, zinc, monitor hydration",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 9,
            "age": 28,
            "gender": "female",
            "symptoms": "fever,cough,chest_pain",
            "duration": "5 days",
            "vital_signs": "temperature_38.2,respiratory_rate_28",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Pneumonia",
            "correct_action": "Chest X-ray, antibiotics",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 10,
            "age": 35,
            "gender": "male",
            "symptoms": "severe_abdominal_pain,nausea,vomiting",
            "duration": "1 day",
            "vital_signs": "temperature_37.5,heart_rate_110",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Acute Appendicitis",
            "correct_action": "Surgical consultation",
            "correct_referral": True,
            "case_type": "urgent"
        },
        {
            "case_id": 11,
            "age": 22,
            "gender": "female",
            "symptoms": "fever,headache",
            "duration": "1 day",
            "vital_signs": "temperature_38.2",
            "medical_history": "20_weeks_pregnant",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Pregnancy-related Fever",
            "correct_action": "Pregnancy test, careful monitoring",
            "correct_referral": False,
            "case_type": "urgent_pregnant"
        },
        {
            "case_id": 12,
            "age": 6,
            "gender": "male",
            "symptoms": "fever,cough,fast_breathing",
            "duration": "3 days",
            "vital_signs": "temperature_38.5,respiratory_rate_45",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Pneumonia",
            "correct_action": "Antibiotics, monitor breathing",
            "correct_referral": False,
            "case_type": "urgent_child"
        },
        {
            "case_id": 13,
            "age": 45,
            "gender": "female",
            "symptoms": "high_fever,severe_headache,body_aches",
            "duration": "2 days",
            "vital_signs": "temperature_39.2",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Severe Malaria",
            "correct_action": "Malaria RDT, IV antimalarial",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 14,
            "age": 18,
            "gender": "male",
            "symptoms": "bloody_diarrhea,fever,abdominal_cramps",
            "duration": "2 days",
            "vital_signs": "temperature_38.0",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Dysentery",
            "correct_action": "Stool test, antibiotics",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 15,
            "age": 32,
            "gender": "female",
            "symptoms": "severe_headache,visual_disturbances",
            "duration": "1 day",
            "vital_signs": "blood_pressure_160_100",
            "medical_history": "hypertension",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Hypertensive Crisis",
            "correct_action": "Blood pressure control",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 16,
            "age": 7,
            "gender": "female",
            "symptoms": "fever,rash,cough",
            "duration": "4 days",
            "vital_signs": "temperature_38.8",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Measles",
            "correct_action": "Vitamin A, supportive care",
            "correct_referral": False,
            "case_type": "urgent_child"
        },
        {
            "case_id": 17,
            "age": 40,
            "gender": "male",
            "symptoms": "chest_pain,shortness_of_breath",
            "duration": "2 hours",
            "vital_signs": "heart_rate_120,blood_pressure_140_90",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Possible Heart Attack",
            "correct_action": "ECG, cardiac enzymes",
            "correct_referral": True,
            "case_type": "urgent"
        },
        {
            "case_id": 18,
            "age": 26,
            "gender": "female",
            "symptoms": "severe_vomiting,dehydration",
            "duration": "1 day",
            "vital_signs": "heart_rate_110,capillary_refill_3_seconds",
            "medical_history": "early_pregnancy",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Hyperemesis Gravidarum",
            "correct_action": "IV fluids, antiemetics",
            "correct_referral": False,
            "case_type": "urgent_pregnant"
        },
        {
            "case_id": 19,
            "age": 55,
            "gender": "male",
            "symptoms": "fever,cough,weight_loss",
            "duration": "2 weeks",
            "vital_signs": "temperature_37.8",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Tuberculosis",
            "correct_action": "Sputum test, chest X-ray",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 20,
            "age": 9,
            "gender": "male",
            "symptoms": "fever,severe_headache,neck_stiffness",
            "duration": "1 day",
            "vital_signs": "temperature_39.0",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Meningitis",
            "correct_action": "Immediate antibiotics, referral",
            "correct_referral": True,
            "case_type": "urgent_child"
        },
        {
            "case_id": 21,
            "age": 33,
            "gender": "female",
            "symptoms": "fever,abdominal_pain,vaginal_discharge",
            "duration": "3 days",
            "vital_signs": "temperature_38.5",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Pelvic Inflammatory Disease",
            "correct_action": "Antibiotics, pelvic exam",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 22,
            "age": 12,
            "gender": "female",
            "symptoms": "fever,joint_pain,rash",
            "duration": "5 days",
            "vital_signs": "temperature_38.2",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Rheumatic Fever",
            "correct_action": "Antibiotics, cardiac evaluation",
            "correct_referral": True,
            "case_type": "urgent_child"
        },
        {
            "case_id": 23,
            "age": 38,
            "gender": "male",
            "symptoms": "severe_back_pain,blood_in_urine",
            "duration": "1 day",
            "vital_signs": "blood_pressure_150_95",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Kidney Stones",
            "correct_action": "Pain management, imaging",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 24,
            "age": 15,
            "gender": "male",
            "symptoms": "fever,sore_throat,swollen_lymph_nodes",
            "duration": "4 days",
            "vital_signs": "temperature_38.5",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Infectious Mononucleosis",
            "correct_action": "Supportive care, monitor spleen",
            "correct_referral": False,
            "case_type": "urgent_child"
        },
        {
            "case_id": 25,
            "age": 29,
            "gender": "female",
            "symptoms": "fever,severe_headache,photophobia",
            "duration": "2 days",
            "vital_signs": "temperature_38.8",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Meningitis",
            "correct_action": "Immediate antibiotics",
            "correct_referral": True,
            "case_type": "urgent"
        },
        {
            "case_id": 26,
            "age": 42,
            "gender": "male",
            "symptoms": "fever,cough,night_sweats",
            "duration": "3 weeks",
            "vital_signs": "temperature_37.5",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Tuberculosis",
            "correct_action": "Sputum test, chest X-ray",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 27,
            "age": 11,
            "gender": "male",
            "symptoms": "fever,abdominal_pain,vomiting",
            "duration": "2 days",
            "vital_signs": "temperature_38.3",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Appendicitis",
            "correct_action": "Surgical consultation",
            "correct_referral": True,
            "case_type": "urgent_child"
        },
        {
            "case_id": 28,
            "age": 36,
            "gender": "female",
            "symptoms": "fever,severe_headache,neck_pain",
            "duration": "1 day",
            "vital_signs": "temperature_39.1",
            "medical_history": "none",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Meningitis",
            "correct_action": "Immediate antibiotics",
            "correct_referral": True,
            "case_type": "urgent"
        },
        {
            "case_id": 29,
            "age": 48,
            "gender": "male",
            "symptoms": "fever,cough,chest_pain",
            "duration": "1 week",
            "vital_signs": "temperature_38.0,respiratory_rate_30",
            "medical_history": "smoker",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Pneumonia",
            "correct_action": "Chest X-ray, antibiotics",
            "correct_referral": False,
            "case_type": "urgent"
        },
        {
            "case_id": 30,
            "age": 19,
            "gender": "female",
            "symptoms": "fever,abdominal_pain,vaginal_bleeding",
            "duration": "1 day",
            "vital_signs": "temperature_38.5",
            "medical_history": "pregnant_8_weeks",
            "correct_triage_level": 2,
            "correct_triage_label": "Urgent",
            "correct_diagnosis": "Threatened Miscarriage",
            "correct_action": "Bed rest, monitoring",
            "correct_referral": False,
            "case_type": "urgent_pregnant"
        },
        
        # STANDARD CASES (Level 3) - 15 cases
        {
            "case_id": 31,
            "age": 25,
            "gender": "male",
            "symptoms": "mild_fever,cough,runny_nose",
            "duration": "3 days",
            "vital_signs": "temperature_37.8",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Upper Respiratory Infection",
            "correct_action": "Symptomatic treatment",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 32,
            "age": 35,
            "gender": "female",
            "symptoms": "headache,fatigue",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Tension Headache",
            "correct_action": "Pain relief, rest",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 33,
            "age": 28,
            "gender": "male",
            "symptoms": "mild_diarrhea,stomach_cramps",
            "duration": "1 day",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Mild Gastroenteritis",
            "correct_action": "ORS, dietary advice",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 34,
            "age": 45,
            "gender": "female",
            "symptoms": "back_pain,stiffness",
            "duration": "3 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Muscle Strain",
            "correct_action": "Pain relief, physiotherapy",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 35,
            "age": 22,
            "gender": "male",
            "symptoms": "skin_rash,itching",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Allergic Dermatitis",
            "correct_action": "Antihistamines, topical cream",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 36,
            "age": 50,
            "gender": "female",
            "symptoms": "joint_pain,swelling",
            "duration": "1 week",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Arthritis",
            "correct_action": "Pain relief, anti-inflammatories",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 37,
            "age": 30,
            "gender": "male",
            "symptoms": "mild_cough,sore_throat",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Pharyngitis",
            "correct_action": "Throat lozenges, rest",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 38,
            "age": 40,
            "gender": "female",
            "symptoms": "not_feeling_well,tired",
            "duration": "1 day",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Vague Symptoms",
            "correct_action": "General assessment, rest",
            "correct_referral": False,
            "case_type": "standard_vague"
        },
        {
            "case_id": 39,
            "age": 33,
            "gender": "male",
            "symptoms": "mild_fever,body_aches",
            "duration": "1 day",
            "vital_signs": "temperature_37.5",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Viral Syndrome",
            "correct_action": "Symptomatic treatment",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 40,
            "age": 26,
            "gender": "female",
            "symptoms": "abdominal_pain,bloating",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Indigestion",
            "correct_action": "Dietary advice, antacids",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 41,
            "age": 55,
            "gender": "male",
            "symptoms": "mild_headache,dizziness",
            "duration": "1 day",
            "vital_signs": "blood_pressure_140_85",
            "medical_history": "hypertension",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Hypertension",
            "correct_action": "Blood pressure monitoring",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 42,
            "age": 38,
            "gender": "female",
            "symptoms": "fatigue,weakness",
            "duration": "3 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Fatigue Syndrome",
            "correct_action": "Rest, nutritional advice",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 43,
            "age": 29,
            "gender": "male",
            "symptoms": "mild_cough,congestion",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Common Cold",
            "correct_action": "Decongestants, rest",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 44,
            "age": 44,
            "gender": "female",
            "symptoms": "mild_fever,headache",
            "duration": "1 day",
            "vital_signs": "temperature_37.6",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Mild Viral Infection",
            "correct_action": "Symptomatic treatment",
            "correct_referral": False,
            "case_type": "standard"
        },
        {
            "case_id": 45,
            "age": 31,
            "gender": "male",
            "symptoms": "muscle_pain,stiffness",
            "duration": "2 days",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 3,
            "correct_triage_label": "Standard",
            "correct_diagnosis": "Muscle Strain",
            "correct_action": "Pain relief, rest",
            "correct_referral": False,
            "case_type": "standard"
        },
        
        # MINOR CASES (Level 4) - 5 cases
        {
            "case_id": 46,
            "age": 20,
            "gender": "male",
            "symptoms": "mild_cough,runny_nose",
            "duration": "1 day",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 4,
            "correct_triage_label": "Minor",
            "correct_diagnosis": "Common Cold",
            "correct_action": "Rest, fluids",
            "correct_referral": False,
            "case_type": "minor"
        },
        {
            "case_id": 47,
            "age": 35,
            "gender": "female",
            "symptoms": "minor_skin_irritation",
            "duration": "1 day",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 4,
            "correct_triage_label": "Minor",
            "correct_diagnosis": "Skin Irritation",
            "correct_action": "Topical cream",
            "correct_referral": False,
            "case_type": "minor"
        },
        {
            "case_id": 48,
            "age": 25,
            "gender": "male",
            "symptoms": "mild_headache",
            "duration": "few_hours",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 4,
            "correct_triage_label": "Minor",
            "correct_diagnosis": "Tension Headache",
            "correct_action": "Pain relief",
            "correct_referral": False,
            "case_type": "minor"
        },
        {
            "case_id": 49,
            "age": 42,
            "gender": "female",
            "symptoms": "mild_indigestion",
            "duration": "few_hours",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 4,
            "correct_triage_label": "Minor",
            "correct_diagnosis": "Indigestion",
            "correct_action": "Antacids",
            "correct_referral": False,
            "case_type": "minor"
        },
        {
            "case_id": 50,
            "age": 30,
            "gender": "male",
            "symptoms": "mild_fatigue",
            "duration": "1 day",
            "vital_signs": "normal",
            "medical_history": "none",
            "correct_triage_level": 4,
            "correct_triage_label": "Minor",
            "correct_diagnosis": "Fatigue",
            "correct_action": "Rest, fluids",
            "correct_referral": False,
            "case_type": "minor"
        }
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(test_cases)
    
    return df


def save_test_dataset():
    """Save the test dataset to CSV"""
    df = create_test_dataset()
    df.to_csv('test_dataset.csv', index=False)
    print(f"✅ Test dataset saved: test_dataset.csv")
    print(f"📊 Dataset contains {len(df)} test cases:")
    print(f"   - Critical (Level 1): {len(df[df['correct_triage_level'] == 1])} cases")
    print(f"   - Urgent (Level 2): {len(df[df['correct_triage_level'] == 2])} cases")
    print(f"   - Standard (Level 3): {len(df[df['correct_triage_level'] == 3])} cases")
    print(f"   - Minor (Level 4): {len(df[df['correct_triage_level'] == 4])} cases")
    print(f"   - Pregnant patients: {len(df[df['case_type'].str.contains('pregnant')])} cases")
    print(f"   - Children (<18): {len(df[df['age'] < 18])} cases")
    print(f"   - Elderly (>65): {len(df[df['age'] > 65])} cases")
    print(f"   - Vague symptoms: {len(df[df['case_type'].str.contains('vague')])} cases")
    
    return df


if __name__ == "__main__":
    df = save_test_dataset()
    
    # Show sample cases
    print(f"\n📋 Sample Critical Case:")
    critical_case = df[df['correct_triage_level'] == 1].iloc[0]
    print(f"   Case {critical_case['case_id']}: {critical_case['symptoms']}")
    print(f"   Expected: Level {critical_case['correct_triage_level']} - {critical_case['correct_diagnosis']}")
    
    print(f"\n📋 Sample Urgent Case:")
    urgent_case = df[df['correct_triage_level'] == 2].iloc[0]
    print(f"   Case {urgent_case['case_id']}: {urgent_case['symptoms']}")
    print(f"   Expected: Level {urgent_case['correct_triage_level']} - {urgent_case['correct_diagnosis']}")
    
    print(f"\n📋 Sample Standard Case:")
    standard_case = df[df['correct_triage_level'] == 3].iloc[0]
    print(f"   Case {standard_case['case_id']}: {standard_case['symptoms']}")
    print(f"   Expected: Level {standard_case['correct_triage_level']} - {standard_case['correct_diagnosis']}")
    
    print(f"\n📋 Sample Minor Case:")
    minor_case = df[df['correct_triage_level'] == 4].iloc[0]
    print(f"   Case {minor_case['case_id']}: {minor_case['symptoms']}")
    print(f"   Expected: Level {minor_case['correct_triage_level']} - {minor_case['correct_diagnosis']}")
