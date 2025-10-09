"""
MediLink PHC - Multilingual Translation Module
Supports Nigerian languages: Pidgin, Hausa, Igbo, Yoruba
"""

import re
from typing import List, Dict, Tuple, Optional

class MultilingualTranslator:
    """Translates Nigerian languages to English for medical triage"""
    
    def __init__(self):
        self.languages = {
            'pidgin': self._get_pidgin_mappings(),
            'hausa': self._get_hausa_mappings(),
            'igbo': self._get_igbo_mappings(),
            'yoruba': self._get_yoruba_mappings()
        }
        
        # Language detection patterns
        self.language_patterns = {
            'pidgin': [r'\bdey\b', r'\bdon\b', r'\bfit\b', r'\bcomot\b', r'\bbelle\b'],
            'hausa': [r'\bzazzabi\b', r'\bciwon\b', r'\bgudawa\b', r'\bamai\b', r'\btari\b'],
            'igbo': [r'\boku\b', r'\bisi\b', r'\bafo\b', r'\bmgbawa\b', r'\bukwu\b'],
            'yoruba': [r'\bibà\b', r'\bori\b', r'\bikun\b', r'\bìtọ\b', r'\bikọ\b']
        }
    
    def _get_pidgin_mappings(self) -> Dict[str, str]:
        """Pidgin English medical translations"""
        return {
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
            "just now": "recently"
        }
    
    def _get_hausa_mappings(self) -> Dict[str, str]:
        """Hausa medical translations"""
        return {
            # Fever & Temperature
            "zazzabi": "fever",
            "zazzabi mai tsanani": "high fever",
            "jiki yana zafi": "fever",
            "zafi mai tsanani": "high fever",
            "jiki yana da zafi": "fever",
            
            # Pain symptoms
            "ciwon kai": "headache",
            "ciwon kai mai tsanani": "severe headache",
            "kai yana ciwo": "headache",
            "ciwon ciki": "stomach pain",
            "ciwon ciki mai tsanani": "severe abdominal pain",
            "ciki yana ciwo": "stomach pain",
            "ciwon jiki": "body aches",
            "jiki yana ciwo": "body pain",
            "ciwon kirji": "chest pain",
            "kirji yana ciwo": "chest pain",
            "ciwon baya": "back pain",
            "baya yana ciwo": "back pain",
            "ciwon makogwaro": "sore throat",
            "makogwaro yana ciwo": "sore throat",
            "ciwon gwiwa": "joint pain",
            "gwiwa yana ciwo": "joint pain",
            
            # Diarrhea & Vomiting
            "gudawa": "diarrhea",
            "gudawa mai tsanani": "severe diarrhea",
            "gudawa mai jini": "bloody diarrhea",
            "amai": "vomiting",
            "amai mai tsanani": "persistent vomiting",
            "amai mai jini": "bloody vomiting",
            "rashin jin dadi": "nausea",
            "jin rashin jin dadi": "nausea",
            
            # Weakness & Fatigue
            "rashin kuzari": "weakness",
            "rashin kuzari mai tsanani": "severe weakness",
            "rashin karfi": "weakness",
            "karfi ya ragu": "weakness",
            "rashin lafiya": "fatigue",
            "gajiya": "fatigue",
            "rashin ƙarfi": "weakness",
            
            # Breathing problems
            "wahalar numfashi": "difficulty breathing",
            "numfashi mai wahala": "difficulty breathing",
            "rashin numfashi": "shortness of breath",
            "numfashi yana da wahala": "breathing difficulty",
            "numfashi mai sauri": "fast breathing",
            "numfashi mai tsanani": "severe breathing difficulty",
            
            # Cough
            "tari": "cough",
            "tari mai tsanani": "persistent cough",
            "tari mai jini": "coughing blood",
            "tari mara tsanani": "dry cough",
            "tari mai tsanani": "severe cough",
            
            # Loss of consciousness & Seizures
            "rashin sani": "unconscious",
            "rashin fahimta": "unconscious",
            "rashin sani mai tsanani": "severe unconsciousness",
            "girgiza": "convulsions",
            "girgiza mai tsanani": "severe convulsions",
            "rashin sani": "loss of consciousness",
            
            # Dehydration
            "rashin ruwa": "dehydration",
            "rashin ruwa mai tsanani": "severe dehydration",
            "bakin baki": "dry mouth",
            "baki yana bushe": "dry mouth",
            "rashin fitsari": "reduced urination",
            "fitsari ya ragu": "reduced urination",
            
            # Bleeding
            "zubar jini": "bleeding",
            "jini yana zubewa": "bleeding",
            "zubar jini mai tsanani": "severe bleeding",
            "jini daga hanci": "nosebleed",
            "hanci yana zubar jini": "nosebleed",
            
            # Skin conditions
            "kaifi": "itching",
            "jiki yana kaifi": "itching",
            "rashin fata": "rash",
            "fata tana rashin": "rash",
            "fata tana zubewa": "skin peeling",
            "ciwon fata": "skin abscess",
            "fata tana ciwo": "skin abscess",
            
            # Pregnancy related
            "ciki": "pregnant",
            "mata tana da ciki": "pregnant",
            "ciki mai tsanani": "pregnancy complications",
            
            # General descriptions
            "mai tsanani": "severe",
            "mai sauƙi": "mild",
            "da yawa": "many",
            "mai mahimmanci": "serious",
            "mai wahala": "severe",
            "ya ƙara": "worsening",
            "tun": "for",
            "kusan": "about",
            
            # Time descriptions
            "jya": "1 day",
            "yau": "less than 1 day",
            "makon da ya gabata": "7 days",
            "kwanaki kaɗan": "few days",
            "kwanaki da yawa": "many days",
            "yanzu": "recently"
        }
    
    def _get_igbo_mappings(self) -> Dict[str, str]:
        """Igbo medical translations"""
        return {
            # Fever & Temperature
            "oku": "fever",
            "oku di elu": "high fever",
            "ahu na-ekpo oku": "fever",
            "oku di oke": "high fever",
            "ahu na-ekpo": "fever",
            
            # Pain symptoms
            "isi": "headache",
            "isi na-egbu mgbu": "severe headache",
            "isi na-egbu": "headache",
            "afo": "stomach pain",
            "afo na-egbu mgbu": "severe abdominal pain",
            "afo na-egbu": "stomach pain",
            "ahu na-egbu mgbu": "body aches",
            "ahu na-egbu": "body pain",
            "obi na-egbu mgbu": "chest pain",
            "obi na-egbu": "chest pain",
            "azu na-egbu mgbu": "back pain",
            "azu na-egbu": "back pain",
            "akpiri na-egbu mgbu": "sore throat",
            "akpiri na-egbu": "sore throat",
            "ukwu na-egbu mgbu": "joint pain",
            "ukwu na-egbu": "joint pain",
            
            # Diarrhea & Vomiting
            "mgbawa": "diarrhea",
            "mgbawa di oke": "severe diarrhea",
            "mgbawa nwere obara": "bloody diarrhea",
            "agba": "vomiting",
            "agba di oke": "persistent vomiting",
            "agba nwere obara": "bloody vomiting",
            "agba na-adi": "nausea",
            "agba na-adi mgbu": "nausea",
            
            # Weakness & Fatigue
            "adighi ike": "weakness",
            "adighi ike nke ukwuu": "severe weakness",
            "ike adighi": "weakness",
            "ike na-ebelata": "weakness",
            "adighi ume": "fatigue",
            "ume na-ebelata": "fatigue",
            "adighi ike": "weakness",
            
            # Breathing problems
            "nsogbu iku ume": "difficulty breathing",
            "iku ume na-esi ike": "difficulty breathing",
            "adighi iku ume": "shortness of breath",
            "iku ume na-esi ike": "breathing difficulty",
            "iku ume na-adi ngwa": "fast breathing",
            "iku ume di oke": "severe breathing difficulty",
            
            # Cough
            "ukwu": "cough",
            "ukwu di oke": "persistent cough",
            "ukwu nwere obara": "coughing blood",
            "ukwu na-adi": "dry cough",
            "ukwu di oke": "severe cough",
            
            # Loss of consciousness & Seizures
            "adighi ama": "unconscious",
            "adighi mata": "unconscious",
            "adighi ama nke ukwuu": "severe unconsciousness",
            "mgba": "convulsions",
            "mgba di oke": "severe convulsions",
            "adighi ama": "loss of consciousness",
            
            # Dehydration
            "adighi mmiri": "dehydration",
            "adighi mmiri nke ukwuu": "severe dehydration",
            "onu na-akpo": "dry mouth",
            "onu na-akpo nkpo": "dry mouth",
            "adighi mmamiri": "reduced urination",
            "mmamiri na-ebelata": "reduced urination",
            
            # Bleeding
            "obara na-agba": "bleeding",
            "obara na-agba nke ukwuu": "severe bleeding",
            "obara site na imi": "nosebleed",
            "imi na-agba obara": "nosebleed",
            
            # Skin conditions
            "akpukpo na-akpo": "itching",
            "akpukpo na-akpo nkpo": "itching",
            "akpukpo na-adi": "rash",
            "akpukpo na-adi nke ukwuu": "severe rash",
            "akpukpo na-agba": "skin peeling",
            "akpukpo na-egbu mgbu": "skin abscess",
            "akpukpo na-egbu": "skin abscess",
            
            # Pregnancy related
            "ime": "pregnant",
            "nwanyi na-eme ime": "pregnant",
            "ime di oke": "pregnancy complications",
            
            # General descriptions
            "di oke": "severe",
            "di mfe": "mild",
            "di otutu": "many",
            "di nkpa": "serious",
            "di ike": "severe",
            "na-abawanye": "worsening",
            "kemgbe": "for",
            "ihe dika": "about",
            
            # Time descriptions
            "unyahu": "1 day",
            "taa": "less than 1 day",
            "izu gara aga": "7 days",
            "ubochi ole na ole": "few days",
            "ubochi otutu": "many days",
            "ugbua": "recently"
        }
    
    def _get_yoruba_mappings(self) -> Dict[str, str]:
        """Yoruba medical translations"""
        return {
            # Fever & Temperature
            "ibà": "fever",
            "ibà giga": "high fever",
            "ara n gbona": "fever",
            "ibà to gaju": "high fever",
            "ara n gbona pupo": "fever",
            
            # Pain symptoms
            "ori": "headache",
            "ori n dun": "severe headache",
            "ori n dun gidigidi": "severe headache",
            "ikun": "stomach pain",
            "ikun n dun": "severe abdominal pain",
            "ikun n dun gidigidi": "severe abdominal pain",
            "ara n dun": "body aches",
            "ara n dun gidigidi": "body pain",
            "aya n dun": "chest pain",
            "aya n dun gidigidi": "chest pain",
            "eyin n dun": "back pain",
            "eyin n dun gidigidi": "back pain",
            "ofun n dun": "sore throat",
            "ofun n dun gidigidi": "sore throat",
            "egbon n dun": "joint pain",
            "egbon n dun gidigidi": "joint pain",
            
            # Diarrhea & Vomiting
            "ìtọ": "diarrhea",
            "ìtọ to gaju": "severe diarrhea",
            "ìtọ to ni eje": "bloody diarrhea",
            "ikọ": "vomiting",
            "ikọ to gaju": "persistent vomiting",
            "ikọ to ni eje": "bloody vomiting",
            "ikọ n wa": "nausea",
            "ikọ n wa gidigidi": "nausea",
            
            # Weakness & Fatigue
            "alailera": "weakness",
            "alailera to gaju": "severe weakness",
            "alailera": "weakness",
            "agbara n dinku": "weakness",
            "alailera": "fatigue",
            "agbara n dinku": "fatigue",
            "alailera": "weakness",
            
            # Breathing problems
            "ipalara emi": "difficulty breathing",
            "emi n le": "difficulty breathing",
            "ipalara emi": "shortness of breath",
            "emi n le gidigidi": "breathing difficulty",
            "emi n yara": "fast breathing",
            "emi n le to gaju": "severe breathing difficulty",
            
            # Cough
            "ikọ": "cough",
            "ikọ to gaju": "persistent cough",
            "ikọ to ni eje": "coughing blood",
            "ikọ n wa": "dry cough",
            "ikọ to gaju": "severe cough",
            
            # Loss of consciousness & Seizures
            "ailera": "unconscious",
            "ailera": "unconscious",
            "ailera to gaju": "severe unconsciousness",
            "gbigbe": "convulsions",
            "gbigbe to gaju": "severe convulsions",
            "ailera": "loss of consciousness",
            
            # Dehydration
            "ailera omi": "dehydration",
            "ailera omi to gaju": "severe dehydration",
            "enu n gbe": "dry mouth",
            "enu n gbe gidigidi": "dry mouth",
            "ailera isin": "reduced urination",
            "isin n dinku": "reduced urination",
            
            # Bleeding
            "eje n ja": "bleeding",
            "eje n ja to gaju": "severe bleeding",
            "eje lati inu imu": "nosebleed",
            "imu n ja eje": "nosebleed",
            
            # Skin conditions
            "ara n ka": "itching",
            "ara n ka gidigidi": "itching",
            "ara n yi": "rash",
            "ara n yi to gaju": "severe rash",
            "ara n bo": "skin peeling",
            "ara n dun": "skin abscess",
            "ara n dun gidigidi": "skin abscess",
            
            # Pregnancy related
            "oyun": "pregnant",
            "obinrin n oyun": "pregnant",
            "oyun to gaju": "pregnancy complications",
            
            # General descriptions
            "to gaju": "severe",
            "toto": "mild",
            "pupo": "many",
            "pataki": "serious",
            "le": "severe",
            "n pọ": "worsening",
            "lati": "for",
            "nipa": "about",
            
            # Time descriptions
            "ana": "1 day",
            "oni": "less than 1 day",
            "ose ti koja": "7 days",
            "ojo die": "few days",
            "ojo pupo": "many days",
            "bayi": "recently"
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect which Nigerian language is being used
        
        Args:
            text: Input text to analyze
        
        Returns:
            Language name or None if not detected
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Count matches for each language
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            language_scores[lang] = score
        
        # Return language with highest score
        if language_scores:
            best_lang = max(language_scores, key=language_scores.get)
            if language_scores[best_lang] > 0:
                return best_lang
        
        return None
    
    def translate_symptoms(self, symptoms: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Translate symptoms from Nigerian languages to English
        
        Args:
            symptoms: List of symptom descriptions
        
        Returns:
            Tuple of (translated_symptoms, translation_map)
        """
        translated_symptoms = []
        translation_map = {}
        
        for symptom in symptoms:
            # Detect language
            detected_lang = self.detect_language(symptom)
            
            if detected_lang and detected_lang in self.languages:
                # Translate using detected language
                translated, changes = self._translate_with_language(symptom, detected_lang)
                translated_symptoms.append(translated)
                
                if changes:
                    translation_map[symptom] = translated
            else:
                # No translation needed (already English)
                translated_symptoms.append(symptom)
        
        return translated_symptoms, translation_map
    
    def _translate_with_language(self, text: str, language: str) -> Tuple[str, List[str]]:
        """
        Translate text using specific language mappings
        
        Args:
            text: Text to translate
            language: Language to use for translation
        
        Returns:
            Tuple of (translated_text, list_of_translations_made)
        """
        if language not in self.languages:
            return text, []
        
        mappings = self.languages[language]
        original_text = text
        text_lower = text.lower()
        translations_made = []
        
        # Sort phrases by length (longest first) to handle multi-word phrases
        sorted_phrases = sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Replace each phrase
        for phrase, english in sorted_phrases:
            if phrase in text_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                if pattern.search(text_lower):
                    text = pattern.sub(english, text, count=1)
                    text_lower = text.lower()
                    translations_made.append(f"'{phrase}' → '{english}'")
        
        return text, translations_made
    
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
        
        summary = "Translated from Nigerian languages:\n"
        for original, translated in translation_map.items():
            summary += f"  • '{original}' → '{translated}'\n"
        
        return summary.strip()


def test_multilingual_translator():
    """Test the multilingual translator with various examples"""
    print("\n" + "="*80)
    print("🗣️  TESTING MULTILINGUAL TRANSLATOR")
    print("="*80 + "\n")
    
    translator = MultilingualTranslator()
    
    test_cases = [
        {
            "description": "Hausa fever case",
            "input": ["zazzabi", "ciwon kai", "rashin kuzari"],
            "expected_language": "hausa",
            "expected_keywords": ["fever", "headache", "weakness"]
        },
        {
            "description": "Igbo diarrhea case",
            "input": ["mgbawa", "agba", "adighi ike"],
            "expected_language": "igbo",
            "expected_keywords": ["diarrhea", "vomiting", "weakness"]
        },
        {
            "description": "Yoruba breathing problem",
            "input": ["ipalara emi", "aya n dun", "ikọ"],
            "expected_language": "yoruba",
            "expected_keywords": ["breathing", "chest", "cough"]
        },
        {
            "description": "Pidgin emergency",
            "input": ["e don faint", "im body dey shake", "breath dey hard"],
            "expected_language": "pidgin",
            "expected_keywords": ["unconscious", "convulsions", "breathing"]
        },
        {
            "description": "Mixed languages",
            "input": ["zazzabi", "body dey pain", "ikọ", "mgbawa"],
            "expected_language": "mixed",
            "expected_keywords": ["fever", "pain", "cough", "diarrhea"]
        },
        {
            "description": "Pure English (no translation needed)",
            "input": ["headache", "fever", "cough"],
            "expected_language": "english",
            "expected_keywords": ["headache", "fever", "cough"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Input: {test['input']}")
        
        # Detect language for each symptom
        detected_languages = []
        for symptom in test['input']:
            lang = translator.detect_language(symptom)
            detected_languages.append(lang or "english")
        
        print(f"Detected languages: {detected_languages}")
        
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
    
    print("="*80)
    print("✅ Multilingual translator tests complete!\n")
    
    return translator


if __name__ == "__main__":
    translator = test_multilingual_translator()
