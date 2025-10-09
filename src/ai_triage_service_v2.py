"""
MediLink PHC - Enhanced AI Triage Service (Version 2)
Production-ready with retry logic, fallback, and robust error handling
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

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
    """Enhanced AI Triage Service with robust error handling"""
    
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
    
    def __init__(self, provider: str = None, timeout: int = 5, max_retries: int = 2):
        """
        Initialize Enhanced AI Triage Service
        
        Args:
            provider: 'groq' or 'gemini'. If None, uses PRIMARY_AI_PROVIDER from env
            timeout: Maximum seconds to wait for AI response (default 5)
            max_retries: Number of retry attempts if AI fails (default 2)
        """
        self.provider = provider or os.getenv('PRIMARY_AI_PROVIDER', 'groq')
        self.timeout = timeout
        self.max_retries = max_retries
        self.groq_client = None
        self.gemini_model = None
        
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
    
    def build_triage_prompt(self, patient_data: Dict) -> str:
        """
        Build the improved V2 triage prompt
        
        Args:
            patient_data: Dictionary with patient information
        
        Returns:
            Formatted prompt string
        """
        # Import the improved prompt function
        from triage_prompt_v2 import build_improved_triage_prompt
        return build_improved_triage_prompt(patient_data)
    
    def analyze_patient(self, patient_data: Dict, use_fallback_on_error: bool = True) -> Dict:
        """
        Analyze patient with retry logic and fallback
        
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
        
        # Try AI analysis with retries
        for attempt in range(self.max_retries + 1):
            try:
                # Build prompt
                prompt = self.build_triage_prompt(patient_data)
                
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
                result['patient_data'] = patient_data
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Log the error
                print(f"⚠️  Attempt {attempt + 1}/{self.max_retries + 1} failed: {error_msg}")
                
                # If last attempt, use fallback or return error
                if attempt == self.max_retries:
                    if use_fallback_on_error:
                        print("🔄 Using rule-based fallback triage...")
                        fallback_result = self.fallback_triage(patient_data)
                        fallback_result['response_time'] = round(time.time() - start_time, 2)
                        fallback_result['ai_failed'] = True
                        fallback_result['ai_error'] = error_msg
                        return fallback_result
                    else:
                        return {
                            "error": error_msg,
                            "triage_level": 3,
                            "triage_label": "Standard",
                            "message": "AI analysis failed. Default to standard triage for safety.",
                            "response_time": round(time.time() - start_time, 2),
                            "attempts": attempt + 1
                        }
                
                # Wait before retry
                time.sleep(0.5 * (attempt + 1))
    
    def _call_groq_with_timeout(self, prompt: str) -> str:
        """Call Groq API with timeout handling"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Groq API call exceeded {self.timeout}s timeout")
        
        # Set timeout (Unix only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
        
        try:
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
            
        finally:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
    
    def _call_gemini_with_timeout(self, prompt: str) -> str:
        """Call Gemini API with timeout handling"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Gemini API call exceeded {self.timeout}s timeout")
        
        # Set timeout (Unix only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
        
        try:
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
            
        finally:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
    
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
            "confidence": 60,
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
            "patient_advice": "This is an automated initial assessment. Please see a healthcare provider for proper diagnosis."
        }


def compare_providers(patient_data: Dict) -> Dict:
    """
    Compare Groq vs Gemini performance on same patient
    
    Args:
        patient_data: Patient information to test
    
    Returns:
        Comparison results
    """
    print("\n" + "="*70)
    print("⚖️  COMPARING GROQ vs GEMINI PERFORMANCE")
    print("="*70 + "\n")
    
    results = {}
    
    # Test Groq
    if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
        print("Testing Groq...")
        try:
            service = AITriageService(provider='groq')
            start = time.time()
            groq_result = service.analyze_patient(patient_data)
            groq_time = time.time() - start
            
            results['groq'] = {
                'available': True,
                'response_time': round(groq_time, 2),
                'triage_level': groq_result.get('triage_level'),
                'triage_label': groq_result.get('triage_label'),
                'confidence': groq_result.get('confidence'),
                'error': groq_result.get('error'),
                'full_result': groq_result
            }
            print(f"✅ Groq: {groq_time:.2f}s - Level {groq_result.get('triage_level')}\n")
        except Exception as e:
            results['groq'] = {'available': False, 'error': str(e)}
            print(f"❌ Groq failed: {e}\n")
    else:
        results['groq'] = {'available': False, 'error': 'Not configured'}
        print("⚠️  Groq: Not configured\n")
    
    # Test Gemini
    if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
        print("Testing Gemini...")
        try:
            service = AITriageService(provider='gemini')
            start = time.time()
            gemini_result = service.analyze_patient(patient_data)
            gemini_time = time.time() - start
            
            results['gemini'] = {
                'available': True,
                'response_time': round(gemini_time, 2),
                'triage_level': gemini_result.get('triage_level'),
                'triage_label': gemini_result.get('triage_label'),
                'confidence': gemini_result.get('confidence'),
                'error': gemini_result.get('error'),
                'full_result': gemini_result
            }
            print(f"✅ Gemini: {gemini_time:.2f}s - Level {gemini_result.get('triage_level')}\n")
        except Exception as e:
            results['gemini'] = {'available': False, 'error': str(e)}
            print(f"❌ Gemini failed: {e}\n")
    else:
        results['gemini'] = {'available': False, 'error': 'Not configured'}
        print("⚠️  Gemini: Not configured\n")
    
    # Comparison summary
    print("="*70)
    print("📊 COMPARISON SUMMARY")
    print("="*70)
    
    if results.get('groq', {}).get('available') and results.get('gemini', {}).get('available'):
        groq_time = results['groq']['response_time']
        gemini_time = results['gemini']['response_time']
        
        print(f"\n⏱️  Speed:")
        print(f"   Groq: {groq_time}s")
        print(f"   Gemini: {gemini_time}s")
        print(f"   Winner: {'Groq' if groq_time < gemini_time else 'Gemini'} ({abs(groq_time - gemini_time):.2f}s faster)")
        
        print(f"\n🎯 Accuracy:")
        print(f"   Groq Confidence: {results['groq']['confidence']}%")
        print(f"   Gemini Confidence: {results['gemini']['confidence']}%")
        
        print(f"\n🏥 Triage Agreement:")
        if results['groq']['triage_level'] == results['gemini']['triage_level']:
            print(f"   ✅ Both agree: Level {results['groq']['triage_level']}")
        else:
            print(f"   ⚠️  Disagree: Groq={results['groq']['triage_level']}, Gemini={results['gemini']['triage_level']}")
        
        # Recommendation
        print(f"\n💡 RECOMMENDATION:")
        if groq_time < 2.0 and groq_time < gemini_time:
            print("   Use GROQ - Faster and under 2s response time")
        elif gemini_time < 2.0:
            print("   Use GEMINI - Fast enough and good accuracy")
        else:
            print("   Use GROQ - Generally faster for real-time triage")
    
    return results


if __name__ == "__main__":
    # Test patient for comparison
    test_patient = {
        'age': 30,
        'gender': 'Male',
        'symptoms': ['fever', 'headache', 'body aches'],
        'duration': '3 days',
        'vital_signs': {'temperature': 38.5}
    }
    
    compare_providers(test_patient)