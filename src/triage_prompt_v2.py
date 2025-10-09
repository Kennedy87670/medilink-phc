"""
MediLink PHC - Improved Triage Prompt (Version 2)
Enhanced with Nigerian disease context, better edge case handling, and conservative triage
"""

def build_improved_triage_prompt(patient_data: dict) -> str:
    """
    Build enhanced triage prompt with Nigerian PHC context
    
    Improvements over V1:
    - More specific Nigerian disease prevalence data
    - Better edge case handling
    - Conservative triage approach
    - Clearer PHC resource limitations
    - More detailed reasoning requirements
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
- Fever in infant <2 months old

**Level 3 - STANDARD (Within 2-4 hours):**
- Fever 38-39°C with typical malaria/flu symptoms
- Moderate illness requiring investigation
- Cough with fever but no respiratory distress
- Diarrhea without dehydration
- Suspected uncomplicated malaria
- Suspected uncomplicated typhoid
- Skin infections
- Urinary symptoms

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

**SPECIAL CONSIDERATIONS:**

1. **Children <5 years:** Be MORE conservative - pediatric emergencies deteriorate rapidly
2. **Pregnant women:** Any fever/bleeding = Urgent minimum (Level 2)
3. **Elderly:** Lower threshold for referral
4. **Vague symptoms:** When in doubt, triage UP one level for safety
5. **Contradictory symptoms:** Request vital signs, err on side of caution
6. **No vital signs provided:** Make conservative assumptions based on symptoms

**EDGE CASE HANDLING:**
- If symptoms are vague/unclear → Ask what specific symptoms are most concerning
- If contradictory inputs → Note the contradiction, make safest assumption
- If minimal information → Default to Level 3 (Standard) minimum
- If patient seems very sick but symptoms don't match → Trust clinical appearance, triage UP

**YOUR TASK:**
Provide a structured triage assessment with DETAILED reasoning.

**RESPONSE FORMAT (JSON ONLY - NO MARKDOWN):**

{{
  "triage_level": 1,
  "triage_label": "Critical",
  "confidence": 85,
  "reasoning": "Detailed explanation of why this triage level was chosen, referencing specific symptoms and protocols",
  "red_flags": ["List any emergency signs found"],
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
  "conservative_note": "If you increased triage level for safety, explain why"
}}

**IMPORTANT RULES:**
1. When uncertain between two levels, ALWAYS choose the higher (more urgent) level
2. ANY mention of convulsions, unconsciousness, or severe breathing problems = Automatic Level 1
3. Fever >7 days = Minimum Level 2 (likely typhoid or serious infection)
4. Child <5 with fever + any other symptom = Minimum Level 2
5. If symptoms suggest meningitis = Always Level 1 with immediate referral
6. Provide specific, actionable recommendations
7. Use Nigerian disease prevalence to inform differential diagnosis
8. Be honest about PHC limitations - refer when necessary
9. Response must be ONLY valid JSON - no markdown, no code blocks, no extra text

Analyze this patient now."""

    return prompt