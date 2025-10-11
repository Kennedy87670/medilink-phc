"""
MediLink PHC - Enhanced AI Triage Service (Version 3)
With multilingual support (Pidgin, Hausa, Igbo, Yoruba) and edge case handling
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Import multilingual translator
from multilingual_translator_improved import EnhancedMultilingualTranslator

# AI Provider imports
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AITriageServiceV3:
    """Enhanced AI Triage Service with multilingual support and edge case handling"""
    
    # Critical symptom keywords for fallback triage
    CRITICAL_KEYWORDS = [
        'convulsion', 'seizure', 'unconscious', 'unresponsive', 'not breathing',
        'severe bleeding', 'blue lips', 'cyanosis', 'shock', 'stiff neck',
        'unable to drink', 'gasping', 'very weak pulse'
    ]
    
    URGENT_KEYWORDS = [
        'high fever', 'very hot', 'difficulty breathing', 'fast breathing',
        'severe pain', 'bloody stool', 'bloody diarrhea', 'persistent vomiting',
        'severe dehydration', 'sunken eyes', 'suspected meningitis'
    ]
    
    def __init__(self, provider: str = None, timeout: int = None, max_retries: int = None):
        """
        Initialize Enhanced AI Triage Service with multilingual support
        
        Args:
            provider: 'groq' or 'gemini'. If None, uses PRIMARY_AI_PROVIDER from env
            timeout: Maximum seconds to wait for AI response (default 5)
            max_retries: Number of retry attempts if AI fails (default 2)
        """
        self.provider = provider or os.getenv('PRIMARY_AI_PROVIDER', 'groq')
        # Allow env-based overrides with sensible defaults
        timeout_env = int(os.getenv('TIMEOUT_SECONDS', '10'))
        retries_env = int(os.getenv('MAX_RETRIES', '2'))
        self.timeout = timeout if timeout is not None else timeout_env
        self.max_retries = max_retries if max_retries is not None else retries_env
        self.groq_client = None
        self.gemini_model = None
        # Use the enhanced translator for better Igbo/Yoruba detection
        self.translator = EnhancedMultilingualTranslator()
        
        # Initialize provider
        if self.provider == 'groq' and GROQ_AVAILABLE:
            self._init_groq()
        elif self.provider == 'gemini' and GEMINI_AVAILABLE:
            self._init_gemini()
        else:
            raise ValueError(f"Provider {self.provider} not available or not supported")
    
    def _init_groq(self):
        """Initialize Groq client"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=api_key)
        except TypeError:
            from groq import Client
            self.groq_client = Client(api_key=api_key)
        
        print(f"✅ Groq initialized (timeout: {self.timeout}s, retries: {self.max_retries})")
    
    def _init_gemini(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.gemini_model = genai.GenerativeModel(model_name)
        print(f"✅ Gemini initialized (timeout: {self.timeout}s, retries: {self.max_retries})")
    
    def build_triage_prompt_v3(self, patient_data: Dict) -> str:
        """
        Build the enhanced V3 triage prompt with edge case handling
        
        Args:
            patient_data: Dictionary with patient information
        
        Returns:
            Formatted prompt string
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
        prompt += "\n\n**CRITICAL: Your response must be ONLY valid JSON. Do not include markdown code blocks, explanations, or any text outside the JSON object.**"
      

        return prompt
    
    def analyze_patient(self, patient_data: Dict, use_fallback_on_error: bool = True) -> Dict:
        """
        Analyze patient with multilingual support, retry logic and fallback
        
        Args:
            patient_data: Patient information dictionary
            use_fallback_on_error: Use rule-based fallback if AI fails
        
        Returns:
            Triage assessment dictionary
        """
        start_time = time.time()
        
        # Validate input
        if not patient_data.get('symptoms') or not patient_data.get('age'):
            return {
                "error": "Missing required fields: symptoms and age",
                "triage_level": 3,
                "triage_label": "Standard",
                "message": "Insufficient information. Default to standard triage.",
                "response_time": round(time.time() - start_time, 2)
            }
        
        # Handle multilingual symptoms
        original_symptoms = patient_data.get('symptoms', []).copy()
        translated_symptoms, translation_map = self.translator.translate_symptoms(original_symptoms)
        
        # Update patient data with translated symptoms
        patient_data_translated = patient_data.copy()
        patient_data_translated['symptoms'] = translated_symptoms
        
        # Add translation info to result
        translation_info = {
            "original_symptoms": original_symptoms,
            "translated_symptoms": translated_symptoms,
            "translation_map": translation_map,
            "languages_detected": [self.translator.detect_language(s) for s in original_symptoms]
        }
        
        # Try AI analysis with retries
        for attempt in range(self.max_retries + 1):
            try:
                # Build prompt
                prompt = self.build_triage_prompt_v3(patient_data_translated)
                
                # Call AI with timeout
                if self.provider == 'groq':
                    response = self._call_groq_with_timeout(prompt)
                elif self.provider == 'gemini':
                    response = self._call_gemini_with_timeout(prompt)
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")
                
                # Parse response
                result = self._parse_response(response)
                
                # Validate result
                if not self._validate_result(result):
                    raise ValueError("AI response missing required fields")
                
                # Add metadata
                result['response_time'] = round(time.time() - start_time, 2)
                result['provider'] = self.provider
                result['attempt'] = attempt + 1
                result['patient_data'] = patient_data_translated
                result['translation_info'] = translation_info
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Log the error
                print(f"⚠️  Attempt {attempt + 1}/{self.max_retries + 1} failed: {error_msg}")
                
                # If last attempt, use fallback or return error
                if attempt == self.max_retries:
                    if use_fallback_on_error:
                        print("🔄 Using rule-based fallback triage...")
                        fallback_result = self.fallback_triage(patient_data_translated)
                        fallback_result['response_time'] = round(time.time() - start_time, 2)
                        fallback_result['ai_failed'] = True
                        fallback_result['ai_error'] = error_msg
                        fallback_result['translation_info'] = translation_info
                        return fallback_result
                    else:
                        return {
                            "error": error_msg,
                            "triage_level": 3,
                            "triage_label": "Standard",
                            "message": "AI analysis failed. Default to standard triage for safety.",
                            "response_time": round(time.time() - start_time, 2),
                            "attempts": attempt + 1,
                            "translation_info": translation_info
                        }
                
                # Wait before retry
                time.sleep(0.5 * (attempt + 1))
    
    def _run_with_timeout(self, func, *args, **kwargs):
        """Cross-platform timeout runner using threading fallback when SIGALRM is unavailable."""
        import threading

        result_container = {'result': None, 'error': None}

        def target():
            try:
                result_container['result'] = func(*args, **kwargs)
            except Exception as e:
                result_container['error'] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(self.timeout)

        if thread.is_alive():
            raise TimeoutError(f"Operation exceeded {self.timeout}s timeout")

        if result_container['error'] is not None:
            raise result_container['error']

        return result_container['result']

    def _call_groq_with_timeout(self, prompt: str) -> str:
        """Call Groq API with cross-platform timeout handling"""
        model = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        max_tokens = int(os.getenv('MAX_TOKENS', 1024))
        temperature = float(os.getenv('TEMPERATURE', 0.2))

        def _do_call():
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content

        return self._run_with_timeout(_do_call)
    
    def _call_gemini_with_timeout(self, prompt: str) -> str:
        """Call Gemini API with cross-platform timeout handling"""
        generation_config = {
            "temperature": float(os.getenv('TEMPERATURE', 0.2)),
            "max_output_tokens": int(os.getenv('MAX_TOKENS', 1024)),
            # "response_mime_type": "application/json"
        }

        def _do_call():
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text

        return self._run_with_timeout(_do_call)
    
    def _parse_response(self, response: str) -> Dict:
        """
        Parse AI response with robust handling of markdown and malformed JSON
        
        Args:
            response: Raw AI response string
        
        Returns:
            Parsed dictionary
        """
        try:
            # Remove markdown code blocks if present
            # Handles: ```json\n{...}\n```
            cleaned = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            cleaned = re.sub(r'^```\s*$', '', cleaned, flags=re.MULTILINE)
            cleaned = cleaned.strip()
            
            # Try to parse
            result = json.loads(cleaned)
            
            return result
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            raise ValueError(f"Invalid JSON response from AI: {e}")
    
    def _validate_result(self, result: Dict) -> bool:
        """
        Validate that AI result has required fields
        
        Args:
            result: Parsed AI response
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['triage_level', 'triage_label']
        
        for field in required_fields:
            if field not in result:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate triage level is 1-4
        if result['triage_level'] not in [1, 2, 3, 4]:
            print(f"❌ Invalid triage level: {result['triage_level']}")
            return False
        
        return True
    
    def fallback_triage(self, patient_data: Dict) -> Dict:
        """
        Rule-based fallback triage when AI fails
        Uses symptom keywords and age to determine triage level
        
        Args:
            patient_data: Patient information
        
        Returns:
            Basic triage assessment
        """
        symptoms = patient_data.get('symptoms', [])
        age = patient_data.get('age', 30)
        
        # Convert symptoms to lowercase string for matching
        symptoms_text = ' '.join([str(s).lower() for s in symptoms])
        
        # Check for critical keywords
        is_critical = any(keyword in symptoms_text for keyword in self.CRITICAL_KEYWORDS)
        is_urgent = any(keyword in symptoms_text for keyword in self.URGENT_KEYWORDS)
        
        # Determine triage level
        if is_critical:
            level = 1
            label = "Critical"
            actions = ["Immediate medical attention required", "Prepare for emergency care"]
            referral = True
            referral_reason = "Critical emergency signs detected"
            
        elif is_urgent or (age < 5 and 'fever' in symptoms_text):
            level = 2
            label = "Urgent"
            actions = ["Assess within 1 hour", "Check vital signs"]
            referral = False
            referral_reason = ""
            
        elif 'fever' in symptoms_text or 'pain' in symptoms_text:
            level = 3
            label = "Standard"
            actions = ["Standard assessment", "Basic diagnostic tests if needed"]
            referral = False
            referral_reason = ""
            
        else:
            level = 4
            label = "Minor"
            actions = ["Routine care", "Health education"]
            referral = False
            referral_reason = ""
        
        return {
            "triage_level": level,
            "triage_label": label,
            "confidence_score": 0.6,
            "confidence_explanation": "Rule-based fallback - moderate confidence",
            "method": "rule-based-fallback",
            "reasoning": f"AI unavailable. Rule-based triage based on symptom keywords.",
            "conditions": [{
                "name": "Unable to diagnose without AI",
                "confidence": 0,
                "reasoning": "Fallback mode - clinical assessment recommended"
            }],
            "immediate_actions": actions,
            "referral_needed": referral,
            "referral_reason": referral_reason,
            "recommended_tests": ["Clinical assessment by healthcare provider"],
            "warning_signs": ["Any worsening of symptoms", "New concerning symptoms"],
            "patient_advice": "This is an automated initial assessment. Please see a healthcare provider for proper diagnosis.",
            "disclaimer": "AI-assisted suggestion. Verify with clinical examination."
        }


def test_multilingual_triage():
    """Test the multilingual triage service"""
    print("\n" + "="*80)
    print("🧪 TESTING MULTILINGUAL AI TRIAGE SERVICE")
    print("="*80 + "\n")
    
    # Initialize service
    service = AITriageServiceV3()
    
    # Test cases with different languages
    test_cases = [
        {
            "name": "Hausa Fever Case",
            "patient_data": {
                "age": 28,
                "gender": "Female",
                "symptoms": ["zazzabi", "ciwon kai", "rashin kuzari"],
                "duration": "2 days",
                "vital_signs": {"temperature": 38.5}
            }
        },
        {
            "name": "Igbo Diarrhea Case",
            "patient_data": {
                "age": 4,
                "gender": "Male",
                "symptoms": ["mgbawa", "agba", "adighi ike"],
                "duration": "1 day",
                "vital_signs": {"temperature": 37.8}
            }
        },
        {
            "name": "Yoruba Breathing Problem",
            "patient_data": {
                "age": 45,
                "gender": "Female",
                "symptoms": ["ipalara emi", "aya n dun", "ikọ"],
                "duration": "3 days",
                "vital_signs": {"temperature": 38.7, "respiratory_rate": 28}
            }
        },
        {
            "name": "Pidgin Emergency",
            "patient_data": {
                "age": 6,
                "gender": "Male",
                "symptoms": ["e don faint", "im body dey shake", "breath dey hard"],
                "duration": "1 hour ago",
                "vital_signs": {"temperature": 40.5}
            }
        },
        {
            "name": "Mixed Languages",
            "patient_data": {
                "age": 30,
                "gender": "Female",
                "symptoms": ["zazzabi", "body dey pain", "mgbawa"],
                "duration": "2 days",
                "vital_signs": {"temperature": 39.0}
            }
        },
        {
            "name": "Edge Case - Vague Symptoms",
            "patient_data": {
                "age": 40,
                "gender": "Male",
                "symptoms": ["not feeling well", "tired", "weak"],
                "duration": "1 day",
                "vital_signs": {}
            }
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
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"🔬 Test {i}: {test['name']}")
        print(f"{'─'*80}")
        
        patient = test['patient_data']
        
        # Display original input
        print(f"\n👤 Original Input:")
        print(f"   Age: {patient['age']}, Gender: {patient['gender']}")
        print(f"   Symptoms: {', '.join(patient['symptoms'])}")
        print(f"   Duration: {patient['duration']}")
        
        # Run analysis
        print(f"\n⏳ Analyzing with multilingual AI...")
        start_time = time.time()
        result = service.analyze_patient(patient)
        analysis_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ AI Response ({result['response_time']:.2f}s):")
        
        if result.get('ai_failed'):
            print(f"   ⚠️  AI Failed - Using Fallback Triage")
            print(f"   Error: {result.get('ai_error', 'Unknown')}")
        
        print(f"   Triage: Level {result['triage_level']} - {result['triage_label']}")
        
        if 'confidence_score' in result:
            confidence = result['confidence_score']
            confidence_icon = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
            print(f"   Confidence: {confidence_icon} {confidence:.2f}")
            if 'confidence_explanation' in result:
                print(f"   Explanation: {result['confidence_explanation']}")
        
        # Show translation info
        if 'translation_info' in result:
            trans_info = result['translation_info']
            if trans_info['translation_map']:
                print(f"\n   🗣️  Translation:")
                for orig, trans in trans_info['translation_map'].items():
                    print(f"      • '{orig}' → '{trans}'")
            else:
                print(f"\n   🗣️  No translation needed (English)")
        
        # Show edge cases handled
        if 'edge_cases_handled' in result and result['edge_cases_handled']:
            print(f"\n   ⚠️  Edge Cases: {', '.join(result['edge_cases_handled'])}")
        
        # Show conditions
        if 'conditions' in result and result['conditions']:
            print(f"\n   🔍 Top Conditions:")
            for j, condition in enumerate(result['conditions'][:2], 1):
                conf = condition.get('confidence', 'N/A')
                print(f"      {j}. {condition['name']} ({conf}%)")
        
        # Show actions
        if 'immediate_actions' in result and result['immediate_actions']:
            print(f"\n   ⚡ Actions: {result['immediate_actions'][0]}")
        
        # Referral info
        referral_status = "✅ YES" if result.get('referral_needed') else "❌ NO"
        print(f"\n   🏥 Referral: {referral_status}")
        if result.get('referral_reason'):
            print(f"      Reason: {result['referral_reason'][:60]}...")
    
    print(f"\n{'='*80}")
    print("✅ Multilingual AI triage testing complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_multilingual_triage()
