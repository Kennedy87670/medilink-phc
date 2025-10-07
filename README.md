# 🏥 MediLink PHC - AI-Powered Healthcare Platform

**An intelligent Primary Health Care platform for Nigeria**

[![Hackathon](https://img.shields.io/badge/Hackathon-6%20Days-blue)]()
[![Python](https://img.shields.io/badge/Python-3.11+-green)]()
[![AI](https://img.shields.io/badge/AI-Groq%20%7C%20Gemini-orange)]()
[![Status](https://img.shields.io/badge/Status-Day%201-yellow)]()

## 🎯 Problem Statement

Nigeria faces a healthcare crisis:

- **80%** of Primary Health Care centers are non-functional
- Patients frequently lose medical records
- Health workers lack diagnostic support tools
- Managers cannot predict patient surges
- Limited access to specialist consultations

## 💡 Our Solution

**MediLink PHC** is an AI-powered web platform with three core systems:

### 1. 🤖 AI Triage Assistant

- Analyzes patient symptoms in real-time
- Provides triage level (1-4) based on WHO IMCI protocols
- Suggests likely diseases and immediate actions
- Determines if hospital referral is needed
- **Response time: <3 seconds**
- **Target accuracy: 80%+**

### 2. 📊 Patient Volume Forecasting

- Predicts patient visits for the next 7 days
- Uses Facebook Prophet time-series forecasting
- Helps managers optimize staff allocation
- **Target error (MAPE): <20%**

### 3. 🚨 Outbreak Detection System

- Detects abnormal disease patterns
- Alerts when cases spike (e.g., "Malaria cases 2.5x above normal")
- Uses statistical Z-score analysis
- Enables early intervention

## 🛠️ Tech Stack

### AI & Machine Learning

- **Groq API** (Primary) - Ultra-fast LLM inference (<1s)
- **Gemini API** (Backup) - Reliable Google AI
- **Facebook Prophet** - Time-series forecasting
- **NumPy/Pandas** - Data processing

### Backend

- **Python 3.11+**
- **FastAPI** - Modern, fast API framework
- **Pydantic** - Data validation

### Development

- **Jupyter Notebooks** - Experimentation
- **pytest** - Testing
- **python-dotenv** - Environment management

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11 or higher
python --version

# pip package manager
pip --version
```

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/medilink-phc.git
cd medilink-phc
```

2. **Create virtual environment**

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys
# Get Groq API key: https://console.groq.com
# Get Gemini API key: https://makersuite.google.com/app/apikey
```

5. **Test API connections**

```bash
python src/ai_triage_service.py
```

### Running Tests

```bash
# Test with Groq
python tests/test_scenarios.py groq

# Test with Gemini
python tests/test_scenarios.py gemini
```

## 📁 Project Structure

```
medilink-phc/
├── src/                          # Source code
│   ├── ai_triage_service.py     # AI triage system
│   ├── volume_forecast_model.py # Patient forecasting
│   ├── outbreak_detector.py     # Outbreak detection
│   └── prediction_service.py    # API wrapper
│
├── data/                         # Data files
│   ├── symptom_disease_mapping.csv
│   └── processed/
│
├── tests/                        # Test files
│   ├── test_scenarios.py
│   └── test_results_day1.json
│
├── notebooks/                    # Jupyter notebooks
│   └── day1_triage_testing.ipynb
│
├── docs/                         # Documentation
│   ├── MODEL_DOCUMENTATION.md
│   ├── triage_prompt_v1.txt
│   └── daily_progress/
│
└── requirements.txt              # Dependencies
```

## 📖 How It Works

### AI Triage System

1. **Input**: Patient age, gender, symptoms, vital signs
2. **Processing**:
   - Builds structured prompt with WHO IMCI context
   - Sends to Groq/Gemini API
   - Receives JSON response
3. **Output**:
   - Triage level (1-4)
   - Likely conditions with confidence scores
   - Immediate actions
   - Referral recommendation

### Example Usage

```python
from src.ai_triage_service import AITriageService

# Initialize service
service = AITriageService(provider='groq')

# Patient data
patient = {
    'age': 30,
    'gender': 'Male',
    'symptoms': ['fever', 'headache', 'body_aches'],
    'duration': '3 days',
    'vital_signs': {
        'temperature': 38.5
    }
}

# Analyze
result = service.analyze_patient(patient)

print(f"Triage Level: {result['triage_level']}")
print(f"Conditions: {result['conditions']}")
print(f"Response Time: {result['response_time']}s")
```

## 📊 Day 1 Progress

### ✅ Completed Tasks

- [x] WHO IMCI protocol research
- [x] Symptom-disease mapping database (47 symptoms)
- [x] Groq & Gemini API setup
- [x] AI triage service implementation
- [x] Triage prompt template (v1)
- [x] 5 test scenarios with results

### 📈 Performance Metrics (Day 1)

- **Response Time**: 0.6-1.2 seconds ✅ (Target: <3s)
- **Test Pass Rate**: 100% (5/5 scenarios)
- **API Reliability**: Groq working, Gemini backup ready

### 🎯 Next Steps (Day 2)

- [ ] Refine prompt for edge cases
- [ ] Add multilingual support (Pidgin, Hausa)
- [ ] Improve condition confidence scoring
- [ ] Create Jupyter notebook for interactive testing
- [ ] Optimize response parsing

## 🤝 Team

- **Data Scientist** (You) - AI systems, ML models
- **Frontend Developer** - Web UI
- **Backend Developer** - API, integration
- **Data Analyst** - Insights, visualizations
- **Data Engineer** - Database, data pipeline

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- WHO IMCI Guidelines
- Nigerian Federal Ministry of Health
- Groq & Google Gemini APIs
- Facebook Prophet Library

---

**Built with ❤️ for Nigerian Healthcare**

For questions or issues, please create a GitHub issue or contact the team.
