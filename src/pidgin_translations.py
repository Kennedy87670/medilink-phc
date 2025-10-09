"""
MediLink PHC - Pidgin English Translation Module
Translates Nigerian Pidgin medical phrases to Standard English
"""

import re
from typing import List, Dict, Tuple


class PidginTranslator:
    """Translates Nigerian Pidgin to English for medical triage"""
    
    # Comprehensive Pidgin to English mapping
    PIDGIN_TO_ENGLISH = {
        # Fever & Temperature
        "body dey hot": "fever",
        "body dey burn": "high fever",
        "temperature high": "fever",
        "e dey hot": "fever",
        "im body hot": "fever",
        "hot body": "fever",
        
        # Pain symptoms
        "head dey pain me": "headache",
        "head dey hammer me": "severe headache",
        "my head dey burst": "severe headache",
        "belle dey pain": "stomach pain",
        "belle dey pain me": "abdominal pain",
        "stomach dey do me": "stomach pain",
        "body dey pain": "body aches",
        "body dey ache": "body pain",
        "chest dey pain": "chest pain",
        "back dey pain": "back pain",
        "throat dey pain": "sore throat",
        "joint dey pain": "joint pain",
        
        # Diarrhea & Vomiting
        "shit dey run": "diarrhea",
        "belle dey run": "diarrhea",
        "shit dey comot": "diarrhea",
        "running belle": "diarrhea",
        "purge": "diarrhea",
        "e dey purge": "diarrhea",
        "e dey vomit": "vomiting",
        "im dey throw up": "vomiting",
        "e wan comot": "nausea",
        "belle wan comot": "nausea",
        
        # Weakness & Fatigue
        "body no get power": "weakness",
        "body weak": "fatigue",
        "no strength": "weakness",
        "e no fit stand": "severe weakness",
        "im body don weak": "fatigue",
        "no energy": "fatigue",
        "body don tire": "exhaustion",
        
        # Breathing problems
        "i no fit breathe well": "difficulty breathing",
        "breath dey hard": "shortness of breath",
        "chest dey tight": "chest tightness",
        "e no fit breath": "respiratory distress",
        "breath dey fast": "fast breathing",
        
        # Cough
        "cough dey worry me": "persistent cough",
        "e dey cough": "coughing",
        "im dey cough blood": "coughing blood",
        "dry cough": "dry cough",
        
        # Loss of consciousness & Seizures
        "e don faint": "unconscious",
        "e loss consciousness": "unconscious",
        "im body dey shake": "convulsions",
        "e dey shake": "seizures",
        "fit dey catch am": "seizures",
        
        # Dehydration
        "eye don sink": "sunken eyes",
        "mouth dry": "dry mouth",
        "no urine": "reduced urination",
        "body don dry": "dehydration",
        
        # Bleeding
        "blood dey comot": "bleeding",
        "blood dey run": "bleeding",
        "im dey shit blood": "bloody stool",
        "blood dey come from nose": "nosebleed",
        
        # Skin conditions
        "body dey scratch": "itching",
        "rash dey": "rash",
        "skin dey peel": "skin peeling",
        "boil": "skin abscess",
        
        # Pregnancy related
        "belle": "pregnant",
        "im get belle": "pregnant",
        "pregnancy": "pregnant",
        
        # General descriptions
        "very bad": "severe",
        "small small": "mild",
        "plenty": "many",
        "no be small": "serious",
        "e serious": "severe",
        "e don worse": "worsening",
        "since": "for",
        "done reach": "about",
        
        # Time descriptions
        "yesterday": "1 day",
        "today": "less than 1 day",
        "last week": "7 days",
        "some days": "few days",
        "long time": "many days",
        "just now": "recently",
        
        # Common verbs
        "dey": "is",
        "no dey": "not",
        "e dey": "it is",
        "im dey": "he/she is",
        "comot": "out",
        "enter": "in"
    }
    
    # Common Pidgin patterns to recognize
    PIDGIN_PATTERNS = [
        r'\bdey\b', r'\bdon\b', r'\bfit\b', r'\bcomot\b',
        r'\bbelle\b', r'\bwaka\b', r'\bam\b', r'\bim\b'
    ]
    
    def __init__(self):
        """Initialize translator with mappings"""
        self.mappings = self.PIDGIN_TO_ENGLISH
    
    def is_pidgin(self, text: str) -> bool:
        """
        Detect if text contains Pidgin English
        
        Args:
            text: Input text to check
        
        Returns:
            True if Pidgin detected, False otherwise
        """
        text_lower = text.lower()
        
        # Check for common Pidgin patterns
        for pattern in self.PIDGIN_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        
        # Check for exact phrase matches
        for pidgin_phrase in self.mappings.keys():
            if pidgin_phrase in text_lower:
                return True
        
        return False
    
    def translate(self, text: str) -> Tuple[str, List[str]]:
        """
        Translate Pidgin text to English
        
        Args:
            text: Input text (can be Pidgin or English)
        
        Returns:
            Tuple of (translated_text, list of translations made)
        """
        if not text:
            return text, []
        
        original_text = text
        text_lower = text.lower()
        translations_made = []
        
        # Sort phrases by length (longest first) to handle multi-word phrases
        sorted_phrases = sorted(self.mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Replace each Pidgin phrase
        for pidgin, english in sorted_phrases:
            if pidgin in text_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(pidgin), re.IGNORECASE)
                if pattern.search(text_lower):
                    text = pattern.sub(english, text, count=1)
                    text_lower = text.lower()
                    translations_made.append(f"'{pidgin}' → '{english}'")
        
        return text, translations_made
    
    def translate_symptoms(self, symptoms: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Translate a list of symptoms from Pidgin to English
        
        Args:
            symptoms: List of symptom descriptions (may contain Pidgin)
        
        Returns:
            Tuple of (translated_symptoms_list, translation_map_dict)
        """
        translated_symptoms = []
        translation_map = {}
        
        for symptom in symptoms:
            translated, changes = self.translate(symptom)
            translated_symptoms.append(translated)
            
            if changes:
                translation_map[symptom] = translated
        
        return translated_symptoms, translation_map
    
    def get_translation_summary(self, translation_map: Dict[str, str]) -> str:
        """
        Create a human-readable summary of translations
        
        Args:
            translation_map: Dictionary of original → translated phrases
        
        Returns:
            Summary string
        """
        if not translation_map:
            return "No translations needed (standard English)"
        
        summary = "Translated from Pidgin:\n"
        for original, translated in translation_map.items():
            summary += f"  • '{original}' → '{translated}'\n"
        
        return summary.strip()


# Example usage and testing
def test_pidgin_translator():
    """Test the Pidgin translator with various examples"""
    print("\n" + "="*70)
    print("🗣️  TESTING PIDGIN TRANSLATOR")
    print("="*70 + "\n")
    
    translator = PidginTranslator()
    
    test_cases = [
        {
            "description": "Common fever case",
            "input": ["body dey hot", "head dey pain me", "body no get power"],
            "expected_keywords": ["fever", "headache", "weakness"]
        },
        {
            "description": "Diarrhea case",
            "input": ["belle dey run", "e dey vomit", "body weak"],
            "expected_keywords": ["diarrhea", "vomiting", "weak"]
        },
        {
            "description": "Severe emergency",
            "input": ["e don faint", "im body dey shake", "breath dey hard"],
            "expected_keywords": ["unconscious", "convulsions", "breathing"]
        },
        {
            "description": "Mixed Pidgin and English",
            "input": ["fever", "body dey pain", "cough", "weakness"],
            "expected_keywords": ["fever", "pain", "cough", "weakness"]
        },
        {
            "description": "Pure English (no translation needed)",
            "input": ["headache", "fever", "cough"],
            "expected_keywords": ["headache", "fever", "cough"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Input: {test['input']}")
        
        # Check if Pidgin detected
        is_pidgin = any(translator.is_pidgin(s) for s in test['input'])
        print(f"Pidgin detected: {'Yes' if is_pidgin else 'No'}")
        
        # Translate
        translated, translation_map = translator.translate_symptoms(test['input'])
        print(f"Translated: {translated}")
        
        if translation_map:
            print(f"Translations made:")
            for orig, trans in translation_map.items():
                print(f"  • {orig} → {trans}")
        
        # Check if expected keywords present
        translated_text = ' '.join(translated).lower()
        found_keywords = [kw for kw in test['expected_keywords'] if kw in translated_text]
        print(f"✅ Found expected keywords: {found_keywords}")
        
        print()
    
    print("="*70)
    print("✅ Pidgin translator tests complete!\n")


if __name__ == "__main__":
    test_pidgin_translator()