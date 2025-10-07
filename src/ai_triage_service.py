"""
MediLink PHC - AI Triage Service
Analyzes patient symptoms and provides triage recommendations
"""

import os
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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


class AITriageService:
    """Main service for AI-powered patient triage"""
    
    def __init__(self, provider: str = None):
        """
        Initialize AI Triage Service
        
        Args:
            provider: 'groq' or 'gemini'. If None, uses PRIMARY_AI_PROVIDER from env
        """
        self.provider = provider or os.getenv('PRIMARY_AI_PROVIDER', 'groq')
        self.groq_client = None
        self.gemini_model = None
        
        # Initialize chosen provider
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
            # Newer versions (>=0.4.1)
            from groq import Client
            self.groq_client = Client(api_key=api_key)

        print(f"✅ Groq initialized with model: {os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')}")

    def _init_gemini(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.gemini_model = genai.GenerativeModel(model_name)
        print(f"✅ Gemini initialized with model: {model_name}")
    
    def build_triage_prompt(self, patient_data: Dict) -> str:
        """
        Build the AI triage prompt based on patient information
        
        Args:
            patient_data: Dictionary with patient information
                - age: int
                - gender: str
                - symptoms: List[str]
                - duration: str (optional)
                - vital_signs: Dict (optional)
        
        Returns:
            Formatted prompt string
        """
        age = patient_data.get('age')
        gender = patient_data.get('gender', 'Unknown')
        symptoms = patient_data.get('symptoms', [])
        duration = patient_data.get('duration', 'Not specified')
        vitals = patient_data.get('vital_signs', {})
        
        # Format vital signs if available
        vitals_str = ""
        if vitals:
            vitals_str = "\n**Vital Signs:**\n"
            if 'temperature' in vitals:
                vitals_str += f"- Temperature: {vitals['temperature']}°C\n"
            if 'blood_pressure' in vitals:
                vitals_str += f"- Blood Pressure: {vitals['blood_pressure']}\n"
            if 'heart_rate' in vitals:
                vitals_str += f"- Heart Rate: {vitals['heart_rate']} bpm\n"
            if 'respiratory_rate' in vitals:
                vitals_str += f"- Respiratory Rate: {vitals['respiratory_rate']}/min\n"
        
        prompt = f"""You are an expert medical triage AI assistant for a Nigerian Primary Health Care (PHC) center. Analyze this patient and provide a triage assessment following WHO IMCI protocols.

**PATIENT INFORMATION:**
- Age: {age} years old
- Gender: {gender}
- Symptoms: {', '.join(symptoms)}
- Duration: {duration}{vitals_str}

**YOUR TASK:**
Analyze the patient's condition and provide a triage assessment. Consider:

1. **TRIAGE LEVELS (WHO IMCI Protocol):**
   - Level 1 (CRITICAL): Emergency signs - convulsions, unconscious, severe respiratory distress, unable to drink, signs of shock, severe dehydration
   - Level 2 (URGENT): Needs attention within 1 hour - high fever with concerning symptoms, moderate dehydration, persistent vomiting, difficulty breathing, bloody diarrhea, suspected meningitis
   - Level 3 (STANDARD): Routine care within 2-4 hours - fever with common symptoms, manageable illness, requires investigation
   - Level 4 (MINOR): Low priority - minor ailments, mild symptoms, short duration

2. **COMMON DISEASES IN NIGERIAN PHCs:**
   - Malaria (most common)
   - Typhoid Fever
   - Acute Respiratory Infections
   - Diarrheal Diseases (Cholera, Gastroenteritis)
   - Meningitis (CRITICAL if suspected)
   - Pneumonia
   - Urinary Tract Infections
   - Skin Infections

3. **PHC LIMITATIONS:**
   - Basic laboratory only (malaria test, urine test, basic blood work)
   - No advanced imaging
   - Limited emergency equipment
   - Must refer complex cases to hospital

**RESPONSE FORMAT:**
Respond with a valid JSON object (no markdown, no code blocks, just the JSON):

{{
  "triage_level": 1,
  "triage_label": "Critical",
  "confidence": 85,
  "conditions": [
    {{"name": "Disease Name", "confidence": 90, "reasoning": "Brief explanation"}},
    {{"name": "Alternative Disease", "confidence": 60, "reasoning": "Brief explanation"}}
  ],
  "immediate_actions": [
    "Action 1",
    "Action 2"
  ],
  "referral_needed": true,
  "referral_reason": "Explanation if referral needed",
  "recommended_tests": ["Test 1", "Test 2"],
  "warning_signs": ["Sign to watch for"],
  "patient_advice": "Clear advice in simple language"
}}

Respond ONLY with the JSON object. Be practical, accurate, and prioritize patient safety."""

        return prompt
    
    def analyze_patient(self, patient_data: Dict) -> Dict:
        """
        Analyze patient and return triage assessment
        
        Args:
            patient_data: Patient information dictionary
        
        Returns:
            Triage assessment dictionary
        """
        start_time = time.time()
        
        # Build prompt
        prompt = self.build_triage_prompt(patient_data)
        
        # Get AI response
        try:
            if self.provider == 'groq':
                response = self._call_groq(prompt)
            elif self.provider == 'gemini':
                response = self._call_gemini(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Parse JSON response
            result = self._parse_response(response)
            
            # Add metadata
            result['response_time'] = round(time.time() - start_time, 2)
            result['provider'] = self.provider
            result['patient_data'] = patient_data
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "triage_level": 3,
                "triage_label": "Standard",
                "message": "Error in AI analysis. Default to standard triage for safety.",
                "response_time": round(time.time() - start_time, 2)
            }
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        model = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        max_tokens = int(os.getenv('MAX_TOKENS', 1024))
        temperature = float(os.getenv('TEMPERATURE', 0.2))
        
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        generation_config = {
            "temperature": float(os.getenv('TEMPERATURE', 0.2)),
            "max_output_tokens": int(os.getenv('MAX_TOKENS', 1024)),
            "response_mime_type": "application/json"
        }
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def _parse_response(self, response: str) -> Dict:
        """Parse AI response to dictionary"""
        try:
            # Try to parse as JSON
            result = json.loads(response)
            
            # Validate required fields
            required_fields = ['triage_level', 'triage_label', 'conditions']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")


def test_api_connection():
    """Test API connection with both providers"""
    print("\n🧪 Testing API Connections...\n")
    
    # Test Groq
    if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
        try:
            service = AITriageService(provider='groq')
            test_patient = {
                'age': 30,
                'gender': 'Male',
                'symptoms': ['fever', 'headache'],
                'duration': '2 days'
            }
            result = service.analyze_patient(test_patient)
            print(f"✅ Groq API: Working ({result['response_time']}s)")
            print(f"   Triage: Level {result['triage_level']} - {result['triage_label']}\n")
        except Exception as e:
            print(f"❌ Groq API: Failed - {e}\n")
    else:
        print("⚠️  Groq: Not configured\n")
    
    # Test Gemini
    if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
        try:
            service = AITriageService(provider='gemini')
            test_patient = {
                'age': 30,
                'gender': 'Male',
                'symptoms': ['fever', 'headache'],
                'duration': '2 days'
            }
            result = service.analyze_patient(test_patient)
            print(f"✅ Gemini API: Working ({result['response_time']}s)")
            print(f"   Triage: Level {result['triage_level']} - {result['triage_label']}\n")
        except Exception as e:
            print(f"❌ Gemini API: Failed - {e}\n")
    else:
        print("⚠️  Gemini: Not configured\n")


if __name__ == "__main__":
    # Run API connection test
    test_api_connection()