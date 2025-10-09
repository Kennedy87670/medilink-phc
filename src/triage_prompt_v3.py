"""
MediLink PHC - Enhanced Triage Prompt (Version 3)
Handles edge cases, confidence scoring, and multilingual support
"""

def build_enhanced_triage_prompt_v3(patient_data: dict) -> str:
    """
    Build enhanced triage prompt with edge case handling and confidence scoring
    
    Improvements over V2:
    - Edge case handling (vague, contradictory, multiple severe symptoms)
    - Special population considerations (pregnant, infants, elderly)
    - Confidence scoring system
    - Enhanced reasoning requirements
    - Better PHC resource context
    """
    
    age = patient_data.get('age')
    gender = patient_data.get('gender', 'Unknown')
    symptoms = patient_data.get('symptoms', [])
    duration = patient_data.get('duration', 'Not specified')
    vitals = patient_data.get('vital_signs', {})
    history = patient_data.get('medical_history', None)
    
    # Format vital signs
    vitals_str = ""
    if vitals:
        vitals_str = "\n**Vital Signs:**"
        if 'temperature' in vitals:
            temp = vitals['temperature']
            temp_note = ""
            if temp >= 39.5:
                temp_note = " (HIGH - concerning)"
            elif temp >= 38.0:
                temp_note = " (Elevated)"
            vitals_str += f"\n- Temperature: {temp}°C{temp_note}"
        if 'blood_pressure' in vitals:
            vitals_str += f"\n- Blood Pressure: {vitals['blood_pressure']}"
        if 'heart_rate' in vitals:
            vitals_str += f"\n- Heart Rate: {vitals['heart_rate']} bpm"
        if 'respiratory_rate' in vitals:
            rr = vitals['respiratory_rate']
            rr_note = ""
            if age and age < 5 and rr > 50:
                rr_note = " (CRITICAL for child)"
            elif age and age >= 5 and rr > 30:
                rr_note = " (Elevated)"
            vitals_str += f"\n- Respiratory Rate: {rr}/min{rr_note}"
        if 'oxygen_saturation' in vitals:
            vitals_str += f"\n- SpO2: {vitals['oxygen_saturation']}%"
    
    # Format medical history
    history_str = ""
    if history:
        history_str = f"\n**Medical History:** {history}"
    
    # Format symptoms list
    symptoms_str = ', '.join(symptoms) if symptoms else "None specified"
    
    prompt = f"""You are an expert medical triage AI for a Nigerian Primary Health Care center. Analyze this patient using WHO IMCI protocols and Nigerian disease epidemiology.

**PATIENT INFORMATION:**
- Age: {age} years old
- Gender: {gender}
- Chief Complaints: {symptoms_str}
- Duration: {duration}{vitals_str}{history_str}

**CRITICAL CONTEXT - NIGERIAN PHC EPIDEMIOLOGY:**

**Disease Prevalence in Nigeria:**
- Malaria: ~60% of all fever cases (endemic year-round)
- Typhoid Fever: ~15-20% of prolonged fevers
- Acute Respiratory Infections: ~25% of PHC visits
- Diarrheal Diseases: ~20% of pediatric visits
- Meningitis: Seasonal (Dec-June), ALWAYS critical
- Pneumonia: Leading cause of child mortality
- HIV/AIDS: High prevalence, affects immune response

**EDGE CASE HANDLING:**

**1. Vague Symptoms:**
- If symptoms are vague (e.g., "not feeling well", "tired", "weak"):
  → Ask for specific symptoms OR default to Level 3 (Standard) for safety
  → Add note: "Vague symptoms - clinical assessment recommended"

**2. Contradictory Symptoms:**
- If contradictory inputs (e.g., "fever" but "temperature normal"):
  → Flag the contradiction in reasoning
  → Make safest assumption (err on side of caution)
  → Add note: "Contradictory symptoms noted - verify vital signs"

**3. Multiple Severe Symptoms:**
- If 3+ severe symptoms present:
  → Automatic Level 1 (Critical) regardless of individual symptoms
  → Immediate referral required
  → Add note: "Multiple severe symptoms - emergency protocol"

**4. Special Populations:**

**Pregnant Women:**
- ANY fever/bleeding = Minimum Level 2 (Urgent)
- Consider pregnancy complications
- Add note: "Pregnant patient - increased monitoring required"

**Infants (<6 months):**
- ANY fever = Minimum Level 2 (Urgent)
- Rapid dehydration risk
- Add note: "Infant patient - high dehydration risk"

**Elderly (>65 years):**
- Lower threshold for referral
- Consider comorbidities
- Add note: "Elderly patient - consider comorbidities"

**5. Confidence Assessment:**
- High Confidence (0.8-0.95): Symptoms clearly match one disease
- Medium Confidence (0.6-0.79): Symptoms match multiple diseases
- Low Confidence (0.4-0.59): Vague or contradictory symptoms

**TRIAGE LEVELS - BE CONSERVATIVE (Prioritize Safety):**

**Level 1 - CRITICAL (Immediate Attention):**
⚠️ ANY of these signs = Automatic Level 1:
- Convulsions (ongoing or recent)
- Unconscious or lethargic/difficult to wake
- Unable to drink/breastfeed
- Severe respiratory distress (gasping, grunting, chest indrawing)
- Signs of shock (cold hands, weak pulse, delayed capillary refill)
- Severe dehydration (sunken eyes, very dry mouth, no tears)
- Stiff neck + fever (possible meningitis)
- Temperature >40°C in any patient
- Cyanosis (blue lips/fingers)
- Severe malnutrition with complications
- Multiple severe symptoms (3+)

**Level 2 - URGENT (Within 1 hour):**
- High fever (>39°C) with ANY concerning symptom
- Moderate dehydration (some sunken eyes, reduced urine)
- Persistent vomiting (>3 times in 6 hours)
- Difficulty breathing (fast breathing, mild chest indrawing)
- Bloody diarrhea or bloody urine
- Severe abdominal pain
- Fever >7 days (likely typhoid or other serious infection)
- Suspected meningitis (fever + severe headache + vomiting)
- Measles with complications
- Fever in infant <6 months old
- Pregnant woman with ANY fever/bleeding

**Level 3 - STANDARD (Within 2-4 hours):**
- Fever 38-39°C with typical malaria/flu symptoms
- Moderate illness requiring investigation
- Cough with fever but no respiratory distress
- Diarrhea without dehydration
- Suspected uncomplicated malaria
- Suspected uncomplicated typhoid
- Skin infections
- Urinary symptoms
- Vague symptoms (default to Level 3)

**Level 4 - MINOR (Routine Care):**
- Mild cough/cold without fever
- Minor injuries
- Skin rashes (non-severe)
- Mild symptoms <48 hours
- Health education visits

**PHC LIMITATIONS - MUST CONSIDER:**
✓ Available: Malaria RDT, pregnancy test, basic urinalysis, blood glucose, HIV rapid test
✓ Basic meds: Antimalarials, antibiotics, ORS, zinc, vitamins
✗ NOT Available: CT/MRI, X-rays (limited/none), advanced lab tests, ICU care, surgical facilities
→ Must refer complex cases to secondary/tertiary hospital

**YOUR TASK:**
Provide a structured triage assessment with DETAILED reasoning and confidence scoring.

**RESPONSE FORMAT (JSON ONLY - NO MARKDOWN):**

{{
  "triage_level": 1,
  "triage_label": "Critical",
  "confidence_score": 0.85,
  "confidence_explanation": "High confidence due to classic symptom triad and clear vital signs",
  "reasoning": "Detailed explanation of why this triage level was chosen, referencing specific symptoms and protocols",
  "red_flags": ["List any emergency signs found"],
  "edge_cases_handled": ["List any edge cases identified and how they were handled"],
  "conditions": [
    {{
      "name": "Most Likely Disease",
      "confidence": 85,
      "reasoning": "Why this is suspected - reference symptoms, epidemiology, patient factors",
      "typical_in_nigeria": true
    }},
    {{
      "name": "Alternative Diagnosis",
      "confidence": 50,
      "reasoning": "Why this is possible but less likely"
    }}
  ],
  "immediate_actions": [
    "Specific action 1 (e.g., Start ORS immediately)",
    "Specific action 2 (e.g., Perform malaria RDT)"
  ],
  "referral_needed": false,
  "referral_reason": "If true: specific reason for referral (e.g., requires imaging not available at PHC)",
  "referral_urgency": "immediate/urgent/routine",
  "recommended_tests": [
    "Test 1 available at PHC",
    "Test 2"
  ],
  "warning_signs": [
    "Sign to watch for that requires immediate return",
    "Another warning sign"
  ],
  "patient_advice": "Clear, simple advice in language a non-medical person understands. Include when to return immediately.",
  "special_population_note": "If applicable: note about pregnancy, infant, or elderly considerations",
  "disclaimer": "AI-assisted suggestion. Verify with clinical examination."
}}

**IMPORTANT RULES:**
1. When uncertain between two levels, ALWAYS choose the higher (more urgent) level
2. ANY mention of convulsions, unconsciousness, or severe breathing problems = Automatic Level 1
3. Fever >7 days = Minimum Level 2 (likely typhoid or serious infection)
4. Child <6 months with fever = Minimum Level 2
5. Pregnant woman with fever/bleeding = Minimum Level 2
6. Elderly patient = Consider higher triage level
7. Multiple severe symptoms = Automatic Level 1
8. Vague symptoms = Default to Level 3 with note
9. Contradictory symptoms = Flag contradiction, err on side of caution
10. Provide specific, actionable recommendations
11. Use Nigerian disease prevalence to inform differential diagnosis
12. Be honest about PHC limitations - refer when necessary
13. Response must be ONLY valid JSON - no markdown, no code blocks, no extra text

Analyze this patient now."""

    return prompt


# Test the enhanced prompt
def test_enhanced_prompt():
    """Test the enhanced prompt with edge cases"""
    print("\n" + "="*80)
    print("🧪 TESTING ENHANCED TRIAGE PROMPT V3")
    print("="*80 + "\n")
    
    test_cases = [
        {
            "name": "Vague Symptoms",
            "patient_data": {
                "age": 40,
                "gender": "Male",
                "symptoms": ["not feeling well", "tired", "weak"],
                "duration": "1 day",
                "vital_signs": {}
            },
            "expected_edge_case": "vague_symptoms"
        },
        {
            "name": "Contradictory Symptoms",
            "patient_data": {
                "age": 30,
                "gender": "Female",
                "symptoms": ["fever", "chills", "feeling cold"],
                "duration": "4 hours",
                "vital_signs": {"temperature": 36.5}  # Normal temp but fever symptoms
            },
            "expected_edge_case": "contradictory_symptoms"
        },
        {
            "name": "Multiple Severe Symptoms",
            "patient_data": {
                "age": 25,
                "gender": "Male",
                "symptoms": ["difficulty breathing", "chest pain", "unconscious", "severe bleeding"],
                "duration": "30 minutes",
                "vital_signs": {"temperature": 40.1, "respiratory_rate": 45}
            },
            "expected_edge_case": "multiple_severe"
        },
        {
            "name": "Pregnant Patient",
            "patient_data": {
                "age": 25,
                "gender": "Female",
                "symptoms": ["fever", "headache"],
                "duration": "1 day",
                "vital_signs": {"temperature": 38.2},
                "medical_history": "20 weeks pregnant"
            },
            "expected_edge_case": "pregnant_patient"
        },
        {
            "name": "Infant Patient",
            "patient_data": {
                "age": 3,  # 3 months old
                "gender": "Male",
                "symptoms": ["fever", "irritability"],
                "duration": "6 hours",
                "vital_signs": {"temperature": 38.8}
            },
            "expected_edge_case": "infant_patient"
        },
        {
            "name": "Elderly Patient",
            "patient_data": {
                "age": 75,
                "gender": "Female",
                "symptoms": ["mild cough", "fatigue"],
                "duration": "3 days",
                "vital_signs": {"temperature": 37.5}
            },
            "expected_edge_case": "elderly_patient"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"🔬 Test {i}: {test['name']}")
        print(f"{'─'*60}")
        
        patient = test['patient_data']
        print(f"Age: {patient['age']}, Gender: {patient['gender']}")
        print(f"Symptoms: {', '.join(patient['symptoms'])}")
        print(f"Duration: {patient['duration']}")
        if patient.get('medical_history'):
            print(f"History: {patient['medical_history']}")
        
        print(f"Expected Edge Case: {test['expected_edge_case']}")
        
        # Generate prompt
        prompt = build_enhanced_triage_prompt_v3(patient)
        
        print(f"\n✅ Enhanced prompt generated successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        
        # Check if prompt contains edge case handling
        edge_case_handling = [
            "Vague symptoms",
            "Contradictory symptoms", 
            "Multiple severe symptoms",
            "Pregnant Women",
            "Infants",
            "Elderly"
        ]
        
        found_handling = []
        for handling in edge_case_handling:
            if handling.lower() in prompt.lower():
                found_handling.append(handling)
        
        print(f"Edge case handling found: {found_handling}")
    
    print(f"\n{'='*80}")
    print("✅ Enhanced triage prompt V3 testing complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_enhanced_prompt()
