# 🏥 MediLink PHC - API Integration Guide

**For Backend Developers**  
**Date:** October 9, 2025  
**Version:** Day 4 - Backend Ready

---

## 📋 **OVERVIEW**

This guide provides complete integration instructions for the MediLink PHC AI models. All functions return clean JSON responses suitable for REST API endpoints.

---

## 🔧 **SETUP**

### **Installation**
```bash
pip install pandas numpy prophet matplotlib seaborn groq google-generativeai python-dotenv
```

### **Environment Variables**
```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
PRIMARY_AI_PROVIDER=groq
```

### **Import Service**
```python
from src.backend_prediction_service import create_prediction_service

# Initialize service
service = create_prediction_service()
```

---

## 🚀 **API ENDPOINTS**

### **1. POST /api/triage/analyze**
**Purpose:** Analyze patient symptoms and return triage assessment

**Request Body:**
```json
{
  "age": 30,
  "gender": "Male",
  "symptoms": ["fever", "headache", "body aches"],
  "duration": "3 days",
  "vital_signs": {
    "temperature": 38.5,
    "heart_rate": 95
  },
  "medical_history": "diabetes" // optional
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "triage_level": 2,
    "triage_label": "Urgent",
    "confidence": 85,
    "conditions": [
      {
        "name": "Malaria",
        "confidence": 70,
        "reasoning": "Fever, headache, and body aches are common symptoms"
      }
    ],
    "immediate_actions": [
      "Perform malaria RDT",
      "Start antipyretics for fever"
    ],
    "referral_needed": false,
    "referral_reason": "",
    "recommended_tests": ["Malaria RDT", "Blood work"],
    "warning_signs": ["Difficulty breathing", "Severe headache"],
    "patient_advice": "Rest, drink fluids, return if symptoms worsen",
    "response_time": 1.2
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": {
    "code": "TRIAGE_ERROR",
    "message": "AI service unavailable",
    "user_message": "Unable to analyze patient symptoms. Please try again."
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Backend Implementation:**
```python
@app.post("/api/triage/analyze")
async def analyze_triage(patient_data: dict):
    result = service.analyze_triage(patient_data)
    return result
```

---

### **2. GET /api/predictions/forecast**
**Purpose:** Get patient volume forecast for next N days

**Query Parameters:**
- `facility_id` (optional): Facility identifier
- `days_ahead` (optional): Days to forecast (1-30, default: 7)

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "facility_id": "PHC_001",
    "forecast_period": "2025-10-10 to 2025-10-16",
    "days_ahead": 7,
    "forecast": [
      {
        "date": "2025-10-10",
        "day_of_week": "Thursday",
        "predicted_patients": 145,
        "lower_bound": 120,
        "upper_bound": 170
      }
    ],
    "summary": {
      "total_predicted_patients": 1015,
      "average_daily_patients": 145,
      "min_daily_patients": 75,
      "max_daily_patients": 203,
      "peak_day": "2025-10-12",
      "lowest_day": "2025-10-10"
    }
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Backend Implementation:**
```python
@app.get("/api/predictions/forecast")
async def get_forecast(facility_id: str = None, days_ahead: int = 7):
    result = service.get_patient_forecast(facility_id, days_ahead)
    return result
```

---

### **3. POST /api/predictions/outbreak**
**Purpose:** Check for disease outbreak using statistical analysis

**Request Body:**
```json
{
  "disease": "Malaria",
  "region": "Lagos",
  "current_cases": 65,
  "historical_cases": [20, 22, 18, 25, 21, 23, 19, 24, 20, 22],
  "time_period": "weekly"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "disease": "Malaria",
    "region": "Lagos",
    "time_period": "weekly",
    "is_outbreak": true,
    "severity": "severe",
    "z_score": 19.63,
    "current_cases": 65,
    "historical_average": 21.4,
    "multiplier": 3.0,
    "alert_message": "🚨 SEVERE OUTBREAK ALERT: Malaria cases are 3.0x above normal",
    "recommendations": [
      "Immediate notification to health authorities",
      "Activate emergency response protocols",
      "Increase surveillance and testing"
    ]
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Backend Implementation:**
```python
@app.post("/api/predictions/outbreak")
async def check_outbreak(outbreak_data: dict):
    result = service.check_outbreak(
        outbreak_data["disease"],
        outbreak_data["region"],
        outbreak_data["current_cases"],
        outbreak_data["historical_cases"],
        outbreak_data.get("time_period", "weekly")
    )
    return result
```

---

### **4. POST /api/resources/staffing**
**Purpose:** Get staffing recommendations based on predicted patient volume

**Request Body:**
```json
{
  "predicted_patients": 150,
  "current_staff": {
    "nurses": 3,
    "doctors": 1,
    "pharmacists": 1
  },
  "facility_type": "standard"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "predicted_patients": 150,
    "facility_type": "standard",
    "current_staff": {
      "nurses": 3,
      "doctors": 1,
      "pharmacists": 1
    },
    "required_staff": {
      "nurses": 5,
      "doctors": 3,
      "pharmacists": 2
    },
    "staff_gaps": {
      "nurses": 2,
      "doctors": 2,
      "pharmacists": 1
    },
    "urgency": "critical",
    "workload_per_staff": {
      "nurses": 50.0,
      "doctors": 150.0,
      "pharmacists": 150.0
    },
    "recommendations": [
      "🚨 IMMEDIATE ACTION REQUIRED",
      "Add 2 nurse(s) - Current workload too high",
      "Add 2 doctor(s) - Patient load exceeds capacity"
    ]
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Backend Implementation:**
```python
@app.post("/api/resources/staffing")
async def recommend_staffing(staffing_data: dict):
    result = service.recommend_resources(
        staffing_data["predicted_patients"],
        staffing_data.get("current_staff"),
        staffing_data.get("facility_type", "standard")
    )
    return result
```

---

### **5. POST /api/resources/inventory**
**Purpose:** Analyze inventory for drug stockout risks

**Request Body:**
```json
{
  "inventory_data": {
    "ACT": {
      "current_stock": 50,
      "daily_usage": 8
    },
    "ORS": {
      "current_stock": 200,
      "daily_usage": 15
    },
    "Penicillin": {
      "current_stock": 20,
      "daily_usage": 5
    }
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "overall_status": "CRITICAL",
    "total_drugs": 3,
    "critical_alerts": 2,
    "warning_alerts": 1,
    "drug_analyses": {
      "ACT": {
        "drug_name": "ACT",
        "current_stock": 50,
        "daily_usage": 8,
        "days_remaining": 6.2,
        "stockout_date": "2025-10-15",
        "alert_level": "critical",
        "recommendations": ["🚨 IMMEDIATE ACTION: Order now!"]
      }
    }
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

**Backend Implementation:**
```python
@app.post("/api/resources/inventory")
async def analyze_inventory(inventory_data: dict):
    result = service.analyze_inventory(inventory_data["inventory_data"])
    return result
```

---

### **6. GET /api/status**
**Purpose:** Check service status and availability

**Response:**
```json
{
  "success": true,
  "data": {
    "forecasting_model": true,
    "outbreak_detector": true,
    "resource_optimizer": true,
    "data_path": "data/patient_visits.csv",
    "data_available": true,
    "timestamp": "2025-10-09T07:00:00"
  }
}
```

**Backend Implementation:**
```python
@app.get("/api/status")
async def get_status():
    result = service.get_service_status()
    return result
```

---

## ⚠️ **ERROR HANDLING**

### **Common Error Codes:**
- `TRIAGE_ERROR`: AI triage service failed
- `FORECAST_UNAVAILABLE`: Forecasting model not loaded
- `FORECAST_ERROR`: Forecasting calculation failed
- `OUTBREAK_ERROR`: Outbreak analysis failed
- `RESOURCE_ERROR`: Resource optimization failed
- `INVENTORY_ERROR`: Inventory analysis failed
- `MISSING_PARAMETERS`: Required parameters missing
- `INVALID_PARAMETERS`: Invalid parameter values

### **Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Technical error message",
    "user_message": "User-friendly error message"
  },
  "timestamp": "2025-10-09T07:00:00"
}
```

---

## 🔄 **INTEGRATION EXAMPLES**

### **Complete FastAPI Implementation:**
```python
from fastapi import FastAPI, HTTPException
from src.backend_prediction_service import create_prediction_service

app = FastAPI(title="MediLink PHC API", version="1.0.0")

# Initialize service
service = create_prediction_service()

@app.post("/api/triage/analyze")
async def analyze_triage(patient_data: dict):
    result = service.analyze_triage(patient_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/api/predictions/forecast")
async def get_forecast(facility_id: str = None, days_ahead: int = 7):
    result = service.get_patient_forecast(facility_id, days_ahead)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# ... other endpoints
```

### **Testing with curl:**
```bash
# Test triage
curl -X POST "http://localhost:8000/api/triage/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "gender": "Male",
    "symptoms": ["fever", "headache"],
    "duration": "3 days"
  }'

# Test forecast
curl "http://localhost:8000/api/predictions/forecast?days_ahead=7"

# Test outbreak
curl -X POST "http://localhost:8000/api/predictions/outbreak" \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "Malaria",
    "region": "Lagos",
    "current_cases": 65,
    "historical_cases": [20, 22, 18, 25, 21]
  }'
```

---

## 📊 **PERFORMANCE EXPECTATIONS**

- **Triage Analysis:** <3 seconds response time
- **Forecast Generation:** <2 seconds
- **Outbreak Detection:** <1 second
- **Resource Optimization:** <1 second
- **Inventory Analysis:** <1 second

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **Forecasting model not available**
   - Ensure `data/patient_visits.csv` exists
   - Check Prophet installation: `pip install prophet`

2. **AI triage service fails**
   - Verify API keys in `.env` file
   - Check internet connectivity for Groq/Gemini APIs

3. **Import errors**
   - Ensure all dependencies installed
   - Check Python path includes `src/` directory

### **Logging:**
```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## 📞 **SUPPORT**

For technical support or questions:
- Check error messages in API responses
- Verify all required parameters are provided
- Ensure data formats match examples above
- Test with provided curl examples

---

**Ready for Production Integration!** 🚀
