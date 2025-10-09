"""
MediLink PHC - Enhanced Multilingual Translation Module
Improved Igbo and Yoruba detection accuracy
"""

import re
from typing import List, Dict, Tuple, Optional

class EnhancedMultilingualTranslator:
    """Enhanced translator with improved Igbo and Yoruba detection"""
    
    def __init__(self):
        self.languages = {
            'pidgin': self._get_pidgin_mappings(),
            'hausa': self._get_hausa_mappings(),
            'igbo': self._get_igbo_mappings(),
            'yoruba': self._get_yoruba_mappings()
        }
        
        # Enhanced language detection patterns with more comprehensive coverage
        self.language_patterns = {
            'pidgin': [
                r'\bdey\b', r'\bdon\b', r'\bfit\b', r'\bcomot\b', r'\bbelle\b',
                r'\bwan\b', r'\bna\b', r'\bim\b', r'\be\b', r'\bno\b'
            ],
            'hausa': [
                r'\bzazzabi\b', r'\bciwon\b', r'\bgudawa\b', r'\bamai\b', r'\btari\b',
                r'\bjiki\b', r'\byana\b', r'\bmai\b', r'\btsanani\b', r'\brashin\b',
                r'\bnumfashi\b', r'\bwahala\b', r'\bkarfi\b', r'\bkuzari\b'
            ],
            'igbo': [
                # Core medical terms
                r'\boku\b', r'\bisi\b', r'\bafo\b', r'\bmgbawa\b', r'\bukwu\b',
                r'\bagba\b', r'\bahu\b', r'\bobi\b', r'\bazu\b', r'\bakpiri\b',
                # Igbo grammatical patterns
                r'\bna-egbu\b', r'\bna-ekpo\b', r'\bna-adi\b', r'\bna-esi\b',
                r'\bdi\b', r'\bnwere\b', r'\badighi\b', r'\bike\b', r'\bume\b',
                r'\bmgbu\b', r'\boke\b', r'\bukwuu\b', r'\bmmiri\b', r'\bobara\b',
                r'\bnsogbu\b', r'\biku\b', r'\bimamiri\b', r'\bmmamiri\b'
            ],
            'yoruba': [
                # Core medical terms
                r'\bibà\b', r'\bori\b', r'\bikun\b', r'\bìtọ\b', r'\bikọ\b',
                r'\bara\b', r'\baya\b', r'\beyin\b', r'\bofun\b', r'\begbon\b',
                # Yoruba grammatical patterns
                r'\bn\s+gbona\b', r'\bn\s+dun\b', r'\bn\s+le\b', r'\bn\s+wa\b',
                r'\bn\s+yara\b', r'\bn\s+dinku\b', r'\bn\s+akpo\b', r'\bn\s+adi\b',
                r'\bto\s+gaju\b', r'\bto\s+ni\b', r'\bgidigidi\b', r'\bpupo\b',
                r'\bipalara\b', r'\bemi\b', r'\balailera\b', r'\bagbara\b',
                r'\beje\b', r'\bimu\b', r'\bisin\b', r'\bomi\b', r'\bailera\b'
            ]
        }
        
        # Additional context patterns for better detection
        self.context_patterns = {
            'igbo': [
                r'\bkemgbe\b', r'\bunyahu\b', r'\btaa\b', r'\bizu\b', r'\bubochi\b',
                r'\bmgbe\b', r'\bnaani\b', r'\bma\b', r'\bka\b', r'\bga\b'
            ],
            'yoruba': [
                r'\blati\b', r'\bana\b', r'\boni\b', r'\bose\b', r'\bojo\b',
                r'\bbayi\b', r'\bnipa\b', r'\bkoja\b', r'\bdie\b', r'\bpupo\b'
            ]
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
        """Enhanced Igbo medical translations with more comprehensive coverage"""
        return {
            # Fever & Temperature - Enhanced
            "oku": "fever",
            "oku di elu": "high fever",
            "oku di oke": "high fever",
            "oku ukwu": "high fever",
            "ahu na-ekpo oku": "fever",
            "ahu na-ekpo": "fever",
            "ahu na-ekpo ukwu": "high fever",
            "oku na-adi": "fever",
            "oku na-adi mgbu": "fever with pain",
            
            # Pain symptoms - Enhanced
            "isi": "headache",
            "isi na-egbu mgbu": "severe headache",
            "isi na-egbu": "headache",
            "isi na-adi mgbu": "headache",
            "isi na-adi": "headache",
            "isi ukwu": "severe headache",
            "isi na-egbu ukwu": "severe headache",
            
            "afo": "stomach pain",
            "afo na-egbu mgbu": "severe abdominal pain",
            "afo na-egbu": "stomach pain",
            "afo na-adi mgbu": "stomach pain",
            "afo na-adi": "stomach pain",
            "afo ukwu": "severe stomach pain",
            "afo na-egbu ukwu": "severe abdominal pain",
            
            "ahu na-egbu mgbu": "body aches",
            "ahu na-egbu": "body pain",
            "ahu na-adi mgbu": "body pain",
            "ahu na-adi": "body pain",
            "ahu ukwu": "severe body pain",
            "ahu na-egbu ukwu": "severe body aches",
            
            "obi na-egbu mgbu": "chest pain",
            "obi na-egbu": "chest pain",
            "obi na-adi mgbu": "chest pain",
            "obi na-adi": "chest pain",
            "obi ukwu": "severe chest pain",
            "obi na-egbu ukwu": "severe chest pain",
            
            "azu na-egbu mgbu": "back pain",
            "azu na-egbu": "back pain",
            "azu na-adi mgbu": "back pain",
            "azu na-adi": "back pain",
            "azu ukwu": "severe back pain",
            "azu na-egbu ukwu": "severe back pain",
            
            "akpiri na-egbu mgbu": "sore throat",
            "akpiri na-egbu": "sore throat",
            "akpiri na-adi mgbu": "sore throat",
            "akpiri na-adi": "sore throat",
            "akpiri ukwu": "severe sore throat",
            "akpiri na-egbu ukwu": "severe sore throat",
            
            "ukwu na-egbu mgbu": "joint pain",
            "ukwu na-egbu": "joint pain",
            "ukwu na-adi mgbu": "joint pain",
            "ukwu na-adi": "joint pain",
            "ukwu ukwu": "severe joint pain",
            "ukwu na-egbu ukwu": "severe joint pain",
            
            # Diarrhea & Vomiting - Enhanced
            "mgbawa": "diarrhea",
            "mgbawa di oke": "severe diarrhea",
            "mgbawa di ukwu": "severe diarrhea",
            "mgbawa nwere obara": "bloody diarrhea",
            "mgbawa na-adi": "diarrhea",
            "mgbawa na-adi mgbu": "painful diarrhea",
            "mgbawa ukwu": "severe diarrhea",
            "mgbawa na-adi ukwu": "severe diarrhea",
            
            "agba": "vomiting",
            "agba di oke": "persistent vomiting",
            "agba di ukwu": "severe vomiting",
            "agba nwere obara": "bloody vomiting",
            "agba na-adi": "vomiting",
            "agba na-adi mgbu": "painful vomiting",
            "agba ukwu": "severe vomiting",
            "agba na-adi ukwu": "severe vomiting",
            
            # Weakness & Fatigue - Enhanced
            "adighi ike": "weakness",
            "adighi ike nke ukwuu": "severe weakness",
            "adighi ike ukwu": "severe weakness",
            "ike adighi": "weakness",
            "ike na-ebelata": "weakness",
            "ike na-adi": "weakness",
            "ike ukwu": "severe weakness",
            "ike na-adi ukwu": "severe weakness",
            
            "adighi ume": "fatigue",
            "adighi ume nke ukwuu": "severe fatigue",
            "adighi ume ukwu": "severe fatigue",
            "ume na-ebelata": "fatigue",
            "ume na-adi": "fatigue",
            "ume ukwu": "severe fatigue",
            "ume na-adi ukwu": "severe fatigue",
            
            # Breathing problems - Enhanced
            "nsogbu iku ume": "difficulty breathing",
            "nsogbu iku ume ukwu": "severe breathing difficulty",
            "iku ume na-esi ike": "difficulty breathing",
            "iku ume na-esi ike ukwu": "severe breathing difficulty",
            "adighi iku ume": "shortness of breath",
            "adighi iku ume ukwu": "severe shortness of breath",
            "iku ume na-adi ngwa": "fast breathing",
            "iku ume na-adi ngwa ukwu": "very fast breathing",
            "iku ume di oke": "severe breathing difficulty",
            "iku ume di ukwu": "severe breathing difficulty",
            
            # Cough - Enhanced
            "ukwu": "cough",
            "ukwu di oke": "persistent cough",
            "ukwu di ukwu": "severe cough",
            "ukwu nwere obara": "coughing blood",
            "ukwu na-adi": "cough",
            "ukwu na-adi mgbu": "painful cough",
            "ukwu ukwu": "severe cough",
            "ukwu na-adi ukwu": "severe cough",
            
            # Loss of consciousness & Seizures - Enhanced
            "adighi ama": "unconscious",
            "adighi ama nke ukwuu": "severe unconsciousness",
            "adighi ama ukwu": "severe unconsciousness",
            "adighi mata": "unconscious",
            "adighi mata nke ukwuu": "severe unconsciousness",
            "adighi mata ukwu": "severe unconsciousness",
            "mgba": "convulsions",
            "mgba di oke": "severe convulsions",
            "mgba di ukwu": "severe convulsions",
            "mgba na-adi": "convulsions",
            "mgba na-adi ukwu": "severe convulsions",
            
            # Dehydration - Enhanced
            "adighi mmiri": "dehydration",
            "adighi mmiri nke ukwuu": "severe dehydration",
            "adighi mmiri ukwu": "severe dehydration",
            "onu na-akpo": "dry mouth",
            "onu na-akpo nkpo": "dry mouth",
            "onu na-adi akpo": "dry mouth",
            "adighi mmamiri": "reduced urination",
            "adighi mmamiri nke ukwuu": "severely reduced urination",
            "adighi mmamiri ukwu": "severely reduced urination",
            "mmamiri na-ebelata": "reduced urination",
            "mmamiri na-adi": "reduced urination",
            
            # Bleeding - Enhanced
            "obara na-agba": "bleeding",
            "obara na-agba nke ukwuu": "severe bleeding",
            "obara na-agba ukwu": "severe bleeding",
            "obara site na imi": "nosebleed",
            "imi na-agba obara": "nosebleed",
            "obara na-adi": "bleeding",
            "obara na-adi ukwu": "severe bleeding",
            
            # Skin conditions - Enhanced
            "akpukpo na-akpo": "itching",
            "akpukpo na-akpo nkpo": "itching",
            "akpukpo na-adi akpo": "itching",
            "akpukpo na-adi": "rash",
            "akpukpo na-adi nke ukwuu": "severe rash",
            "akpukpo na-adi ukwu": "severe rash",
            "akpukpo na-agba": "skin peeling",
            "akpukpo na-egbu mgbu": "skin abscess",
            "akpukpo na-egbu": "skin abscess",
            "akpukpo na-egbu ukwu": "severe skin abscess",
            
            # Pregnancy related - Enhanced
            "ime": "pregnant",
            "nwanyi na-eme ime": "pregnant",
            "ime di oke": "pregnancy complications",
            "ime di ukwu": "pregnancy complications",
            "ime na-adi": "pregnant",
            "ime na-adi ukwu": "pregnancy complications",
            
            # General descriptions - Enhanced
            "di oke": "severe",
            "di ukwu": "severe",
            "di mfe": "mild",
            "di otutu": "many",
            "di nkpa": "serious",
            "di ike": "severe",
            "na-abawanye": "worsening",
            "na-adi": "is",
            "na-adi ukwu": "is severe",
            "kemgbe": "for",
            "ihe dika": "about",
            
            # Time descriptions - Enhanced
            "unyahu": "1 day",
            "taa": "less than 1 day",
            "izu gara aga": "7 days",
            "ubochi ole na ole": "few days",
            "ubochi otutu": "many days",
            "ugbua": "recently",
            "mgbe": "when",
            "naani": "only",
            "ma": "but",
            "ka": "than",
            "ga": "will"
        }
    
    def _get_yoruba_mappings(self) -> Dict[str, str]:
        """Enhanced Yoruba medical translations with more comprehensive coverage"""
        return {
            # Fever & Temperature - Enhanced
            "ibà": "fever",
            "ibà giga": "high fever",
            "ibà to gaju": "high fever",
            "ibà to gaju pupo": "very high fever",
            "ara n gbona": "fever",
            "ara n gbona pupo": "fever",
            "ara n gbona to gaju": "high fever",
            "ara n gbona gidigidi": "severe fever",
            
            # Pain symptoms - Enhanced
            "ori": "headache",
            "ori n dun": "severe headache",
            "ori n dun gidigidi": "severe headache",
            "ori n dun to gaju": "severe headache",
            "ori n dun pupo": "severe headache",
            "ori to gaju": "severe headache",
            "ori n dun le": "severe headache",
            
            "ikun": "stomach pain",
            "ikun n dun": "severe abdominal pain",
            "ikun n dun gidigidi": "severe abdominal pain",
            "ikun n dun to gaju": "severe abdominal pain",
            "ikun n dun pupo": "severe abdominal pain",
            "ikun to gaju": "severe stomach pain",
            "ikun n dun le": "severe abdominal pain",
            
            "ara n dun": "body aches",
            "ara n dun gidigidi": "body pain",
            "ara n dun to gaju": "severe body pain",
            "ara n dun pupo": "severe body pain",
            "ara to gaju": "severe body pain",
            "ara n dun le": "severe body pain",
            
            "aya n dun": "chest pain",
            "aya n dun gidigidi": "chest pain",
            "aya n dun to gaju": "severe chest pain",
            "aya n dun pupo": "severe chest pain",
            "aya to gaju": "severe chest pain",
            "aya n dun le": "severe chest pain",
            
            "eyin n dun": "back pain",
            "eyin n dun gidigidi": "back pain",
            "eyin n dun to gaju": "severe back pain",
            "eyin n dun pupo": "severe back pain",
            "eyin to gaju": "severe back pain",
            "eyin n dun le": "severe back pain",
            
            "ofun n dun": "sore throat",
            "ofun n dun gidigidi": "sore throat",
            "ofun n dun to gaju": "severe sore throat",
            "ofun n dun pupo": "severe sore throat",
            "ofun to gaju": "severe sore throat",
            "ofun n dun le": "severe sore throat",
            
            "egbon n dun": "joint pain",
            "egbon n dun gidigidi": "joint pain",
            "egbon n dun to gaju": "severe joint pain",
            "egbon n dun pupo": "severe joint pain",
            "egbon to gaju": "severe joint pain",
            "egbon n dun le": "severe joint pain",
            
            # Diarrhea & Vomiting - Enhanced
            "ìtọ": "diarrhea",
            "ìtọ to gaju": "severe diarrhea",
            "ìtọ to gaju pupo": "very severe diarrhea",
            "ìtọ to ni eje": "bloody diarrhea",
            "ìtọ n wa": "diarrhea",
            "ìtọ n wa gidigidi": "severe diarrhea",
            "ìtọ pupo": "severe diarrhea",
            "ìtọ n wa le": "severe diarrhea",
            
            "ikọ": "vomiting",
            "ikọ to gaju": "persistent vomiting",
            "ikọ to gaju pupo": "very severe vomiting",
            "ikọ to ni eje": "bloody vomiting",
            "ikọ n wa": "nausea",
            "ikọ n wa gidigidi": "nausea",
            "ikọ pupo": "severe vomiting",
            "ikọ n wa le": "severe vomiting",
            
            # Weakness & Fatigue - Enhanced
            "alailera": "weakness",
            "alailera to gaju": "severe weakness",
            "alailera to gaju pupo": "very severe weakness",
            "alailera pupo": "severe weakness",
            "alailera n wa": "weakness",
            "alailera n wa gidigidi": "severe weakness",
            "alailera n wa le": "severe weakness",
            
            "agbara n dinku": "weakness",
            "agbara n dinku to gaju": "severe weakness",
            "agbara n dinku pupo": "severe weakness",
            "agbara n wa": "weakness",
            "agbara n wa gidigidi": "severe weakness",
            "agbara n wa le": "severe weakness",
            
            # Breathing problems - Enhanced
            "ipalara emi": "difficulty breathing",
            "ipalara emi to gaju": "severe breathing difficulty",
            "ipalara emi pupo": "severe breathing difficulty",
            "emi n le": "difficulty breathing",
            "emi n le to gaju": "severe breathing difficulty",
            "emi n le pupo": "severe breathing difficulty",
            "emi n le gidigidi": "severe breathing difficulty",
            "emi n yara": "fast breathing",
            "emi n yara to gaju": "very fast breathing",
            "emi n yara pupo": "very fast breathing",
            "emi n le to gaju": "severe breathing difficulty",
            
            # Cough - Enhanced
            "ikọ": "cough",
            "ikọ to gaju": "persistent cough",
            "ikọ to gaju pupo": "very severe cough",
            "ikọ to ni eje": "coughing blood",
            "ikọ n wa": "dry cough",
            "ikọ n wa gidigidi": "severe cough",
            "ikọ pupo": "severe cough",
            "ikọ n wa le": "severe cough",
            
            # Loss of consciousness & Seizures - Enhanced
            "ailera": "unconscious",
            "ailera to gaju": "severe unconsciousness",
            "ailera to gaju pupo": "very severe unconsciousness",
            "ailera pupo": "severe unconsciousness",
            "ailera n wa": "unconscious",
            "ailera n wa gidigidi": "severe unconsciousness",
            "ailera n wa le": "severe unconsciousness",
            
            "gbigbe": "convulsions",
            "gbigbe to gaju": "severe convulsions",
            "gbigbe to gaju pupo": "very severe convulsions",
            "gbigbe pupo": "severe convulsions",
            "gbigbe n wa": "convulsions",
            "gbigbe n wa gidigidi": "severe convulsions",
            "gbigbe n wa le": "severe convulsions",
            
            # Dehydration - Enhanced
            "ailera omi": "dehydration",
            "ailera omi to gaju": "severe dehydration",
            "ailera omi to gaju pupo": "very severe dehydration",
            "ailera omi pupo": "severe dehydration",
            "enu n gbe": "dry mouth",
            "enu n gbe gidigidi": "dry mouth",
            "enu n gbe to gaju": "very dry mouth",
            "enu n gbe pupo": "very dry mouth",
            "ailera isin": "reduced urination",
            "ailera isin to gaju": "severely reduced urination",
            "ailera isin pupo": "severely reduced urination",
            "isin n dinku": "reduced urination",
            "isin n dinku to gaju": "severely reduced urination",
            "isin n dinku pupo": "severely reduced urination",
            
            # Bleeding - Enhanced
            "eje n ja": "bleeding",
            "eje n ja to gaju": "severe bleeding",
            "eje n ja to gaju pupo": "very severe bleeding",
            "eje n ja pupo": "severe bleeding",
            "eje lati inu imu": "nosebleed",
            "imu n ja eje": "nosebleed",
            "eje n ja le": "severe bleeding",
            
            # Skin conditions - Enhanced
            "ara n ka": "itching",
            "ara n ka gidigidi": "itching",
            "ara n ka to gaju": "severe itching",
            "ara n ka pupo": "severe itching",
            "ara n yi": "rash",
            "ara n yi to gaju": "severe rash",
            "ara n yi pupo": "severe rash",
            "ara n bo": "skin peeling",
            "ara n bo to gaju": "severe skin peeling",
            "ara n bo pupo": "severe skin peeling",
            "ara n dun": "skin abscess",
            "ara n dun gidigidi": "skin abscess",
            "ara n dun to gaju": "severe skin abscess",
            "ara n dun pupo": "severe skin abscess",
            
            # Pregnancy related - Enhanced
            "oyun": "pregnant",
            "obinrin n oyun": "pregnant",
            "oyun to gaju": "pregnancy complications",
            "oyun to gaju pupo": "severe pregnancy complications",
            "oyun pupo": "pregnancy complications",
            "oyun n wa": "pregnant",
            "oyun n wa le": "pregnancy complications",
            
            # General descriptions - Enhanced
            "to gaju": "severe",
            "to gaju pupo": "very severe",
            "toto": "mild",
            "pupo": "many",
            "pupo pupo": "very many",
            "pataki": "serious",
            "le": "severe",
            "n pọ": "worsening",
            "n wa": "is",
            "n wa le": "is severe",
            "lati": "for",
            "nipa": "about",
            
            # Time descriptions - Enhanced
            "ana": "1 day",
            "oni": "less than 1 day",
            "ose ti koja": "7 days",
            "ojo die": "few days",
            "ojo pupo": "many days",
            "bayi": "recently",
            "koja": "past",
            "die": "few",
            "pupo": "many"
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Enhanced language detection with improved accuracy for Igbo and Yoruba
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Count matches for each language
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Add context pattern bonus for Igbo and Yoruba
            if lang in self.context_patterns:
                for pattern in self.context_patterns[lang]:
                    matches = len(re.findall(pattern, text_lower))
                    score += matches * 0.5  # Lower weight for context patterns
            
            language_scores[lang] = score
        
        # Return language with highest score
        if language_scores:
            best_lang = max(language_scores, key=language_scores.get)
            if language_scores[best_lang] > 0:
                return best_lang
        
        return None
    
    def translate_symptoms(self, symptoms: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Enhanced translation with improved accuracy
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
        Enhanced translation with better phrase matching
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
        """
        if not translation_map:
            return "No translations needed (standard English)"
        
        summary = "Translated from Nigerian languages:\n"
        for original, translated in translation_map.items():
            summary += f"  • '{original}' → '{translated}'\n"
        
        return summary.strip()


def test_enhanced_translator():
    """Test the enhanced translator with comprehensive examples"""
    print("\n" + "="*80)
    print("🗣️  TESTING ENHANCED MULTILINGUAL TRANSLATOR")
    print("="*80 + "\n")
    
    translator = EnhancedMultilingualTranslator()
    
    # Enhanced test cases with more comprehensive examples
    test_cases = [
        {
            "description": "Igbo Fever Case - Enhanced",
            "input": ["oku di elu", "isi na-egbu mgbu", "adighi ike nke ukwuu"],
            "expected_language": "igbo",
            "expected_keywords": ["fever", "headache", "weakness"]
        },
        {
            "description": "Igbo Diarrhea Emergency - Enhanced",
            "input": ["mgbawa di oke", "agba na-adi ukwu", "adighi ike ukwu"],
            "expected_language": "igbo",
            "expected_keywords": ["diarrhea", "vomiting", "weakness"]
        },
        {
            "description": "Yoruba Breathing Problem - Enhanced",
            "input": ["ipalara emi to gaju", "aya n dun le", "ikọ n wa le"],
            "expected_language": "yoruba",
            "expected_keywords": ["breathing", "chest", "cough"]
        },
        {
            "description": "Yoruba Severe Case - Enhanced",
            "input": ["ibà to gaju pupo", "ori n dun gidigidi", "alailera to gaju"],
            "expected_language": "yoruba",
            "expected_keywords": ["fever", "headache", "weakness"]
        },
        {
            "description": "Igbo Complex Symptoms - Enhanced",
            "input": ["oku na-ekpo ukwu", "nsogbu iku ume ukwu", "mgba na-adi ukwu"],
            "expected_language": "igbo",
            "expected_keywords": ["fever", "breathing", "convulsions"]
        },
        {
            "description": "Yoruba Complex Symptoms - Enhanced",
            "input": ["ara n gbona to gaju", "emi n le pupo", "gbigbe n wa le"],
            "expected_language": "yoruba",
            "expected_keywords": ["fever", "breathing", "convulsions"]
        },
        {
            "description": "Mixed Languages - Enhanced",
            "input": ["oku di elu", "body dey pain", "ibà to gaju"],
            "expected_language": "mixed",
            "expected_keywords": ["fever", "pain", "fever"]
        },
        {
            "description": "Pure English (no translation needed)",
            "input": ["headache", "fever", "cough"],
            "expected_language": "english",
            "expected_keywords": ["headache", "fever", "cough"]
        }
    ]
    
    total_tests = len(test_cases)
    successful_detections = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Input: {test['input']}")
        
        # Detect language for each symptom
        detected_languages = []
        for symptom in test['input']:
            lang = translator.detect_language(symptom)
            detected_languages.append(lang or "english")
        
        print(f"Detected languages: {detected_languages}")
        
        # Check if expected language was detected
        expected_lang = test['expected_language']
        if expected_lang == "mixed":
            # For mixed, check if multiple languages detected
            unique_langs = set([lang for lang in detected_languages if lang != "english"])
            if len(unique_langs) > 1:
                successful_detections += 1
                print(f"✅ Mixed languages detected correctly")
        elif expected_lang in detected_languages:
            successful_detections += 1
            print(f"✅ {expected_lang.capitalize()} detected correctly")
        else:
            print(f"❌ Expected {expected_lang}, got {detected_languages}")
        
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
    
    # Calculate accuracy
    detection_accuracy = (successful_detections / total_tests) * 100
    print("="*80)
    print(f"📊 ENHANCED TRANSLATOR RESULTS:")
    print(f"Detection Accuracy: {detection_accuracy:.1f}% ({successful_detections}/{total_tests})")
    print("="*80 + "\n")
    
    return translator


if __name__ == "__main__":
    translator = test_enhanced_translator()
