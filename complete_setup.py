"""
MediLink PHC - Complete Project Setup Script
This script creates all necessary files with content
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Create a file with given content"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

def setup_project():
    """Set up complete project structure with files"""
    
    print("\n🏥 MediLink PHC - Project Setup")
    print("=" * 50)
    print("Creating all project files...\n")
    
    # Get current directory
    base_dir = os.getcwd()
    print(f"📁 Working directory: {base_dir}\n")
    
    # Create .env.example
    env_example = """# AI Provider API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Choose primary provider: groq or gemini
PRIMARY_AI_PROVIDER=groq

# Model configurations
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_MODEL=gemini-1.5-flash

# API settings
MAX_TOKENS=1024
TEMPERATURE=0.2
TIMEOUT_SECONDS=5

# Application settings
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
    create_file('.env.example', env_example)
    
    # Create symptom_disease_mapping.csv
    symptom_csv = """symptom,possible_diseases,severity,triage_hint
fever,"malaria, typhoid, dengue, flu, meningitis",high,2-3
high_fever_above_39,"malaria, meningitis, severe infection, typhoid",critical,1-2
headache,"malaria, meningitis, migraine, typhoid, hypertension",medium,2-3
severe_headache,"meningitis, severe malaria, cerebral malaria, hypertension crisis",critical,1-2
cough,"flu, pneumonia, tuberculosis, bronchitis, COVID-19",medium,3-4
persistent_cough,"tuberculosis, pneumonia, chronic bronchitis, asthma",high,2-3
difficulty_breathing,"pneumonia, asthma, severe malaria, heart failure, anemia",critical,1-2
chest_pain,"pneumonia, heart problems, pleurisy, muscle strain",high,1-2
vomiting,"malaria, typhoid, gastroenteritis, food poisoning, cholera",medium,2-3
persistent_vomiting,"severe dehydration, cholera, meningitis, severe malaria",critical,1-2
diarrhea,"cholera, gastroenteritis, food poisoning, typhoid, dysentery",medium,2-3
bloody_diarrhea,"dysentery, severe gastroenteritis, typhoid complications",high,1-2
stomach_pain,"typhoid, gastroenteritis, appendicitis, intestinal worms, ulcer",medium,2-3
severe_abdominal_pain,"appendicitis, ectopic pregnancy, peritonitis, severe gastroenteritis",critical,1-2
body_aches,"malaria, flu, dengue, typhoid, viral infection",medium,2-3
weakness,"malaria, typhoid, anemia, dehydration, chronic illness",medium,2-3
extreme_weakness,"severe anemia, severe malaria, sepsis, severe dehydration",high,1-2
dizziness,"malaria, anemia, hypertension, dehydration, low blood sugar",medium,2-3
convulsions,"meningitis, cerebral malaria, epilepsy, fever-related seizures",critical,1
unconscious,"meningitis, severe malaria, sepsis, stroke, severe hypoglycemia",critical,1
neck_stiffness,"meningitis, severe infection, cervical spine issues",critical,1-2
rash,"measles, chickenpox, dengue, drug reaction, skin infection",medium,2-4
joint_pain,"dengue, malaria, rheumatoid arthritis, gout, viral infection",medium,3-4
swollen_joints,"septic arthritis, rheumatoid arthritis, gout, injury",high,2-3
runny_nose,"common cold, flu, allergies, sinusitis",low,4
sore_throat,"pharyngitis, tonsillitis, flu, strep throat",low,3-4
difficulty_swallowing,"severe tonsillitis, epiglottitis, abscess",high,1-2
loss_of_appetite,"malaria, typhoid, depression, chronic illness, HIV/AIDS",medium,3
nausea,"malaria, typhoid, gastritis, pregnancy, food poisoning",medium,3-4
pale_skin,"anemia, malaria, blood loss, malnutrition",high,2-3
yellow_eyes,"jaundice, hepatitis, severe malaria, liver disease",high,1-2
dark_urine,"hepatitis, severe dehydration, malaria, liver disease",medium,2-3
painful_urination,"urinary tract infection, sexually transmitted infection, kidney stones",medium,3
frequent_urination,"diabetes, urinary tract infection, pregnancy",medium,3
blood_in_urine,"kidney stones, urinary tract infection, schistosomiasis, trauma",high,2
swelling_feet,"heart failure, kidney disease, malnutrition, liver disease",medium,2-3
rapid_breathing,"pneumonia, asthma, heart failure, severe anemia, sepsis",critical,1-2
wheezing,"asthma, bronchitis, pneumonia, allergic reaction",high,2-3
back_pain,"kidney infection, muscle strain, typhoid, malaria",medium,3
severe_back_pain,"kidney stones, spinal infection, ruptured disc",high,2
bleeding,"trauma, dengue, low platelets, clotting disorder",high,1-2
wounds,"trauma, infection, burns, animal bites",medium,2-4
high_blood_pressure,"hypertension, kidney disease, stress",medium,2-3
low_blood_pressure,"shock, dehydration, blood loss, severe infection",critical,1
confusion,"meningitis, severe malaria, sepsis, stroke, hypoglycemia",critical,1
irritability,"meningitis, severe infection, pain, fever in children",high,2
refusing_to_eat,"severe illness, meningitis, pneumonia, malaria in children",high,1-2
sunken_eyes,"severe dehydration, malnutrition, cholera",high,1-2
dry_mouth,"dehydration, fever, diabetes",medium,2-3
skin_turgor_poor,"severe dehydration, malnutrition",high,1-2
"""
    create_file('data/symptom_disease_mapping.csv', symptom_csv)
    
    # Note about other files
    print("\n" + "=" * 50)
    print("✅ Basic structure created!")
    print("=" * 50)
    print("\n📝 Next steps:")
    print("1. Copy the Python code files I provided:")
    print("   - src/ai_triage_service.py")
    print("   - tests/test_scenarios.py")
    print("2. Copy documentation files:")
    print("   - README.md")
    print("   - docs/day1_report.md")
    print("   - GETTING_STARTED.md")
    print("\n💡 I'll provide instructions for this next!")

if __name__ == "__main__":
    setup_project()