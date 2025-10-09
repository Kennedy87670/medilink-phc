"""
MediLink PHC - Backend-Optimized Prediction Service
Clean JSON responses for API integration
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from volume_forecast_model import PatientVolumeForecaster
from outbreak_detector import OutbreakDetector
from resource_optimizer import ResourceOptimizer

class BackendPredictionService:
    """
    Backend-optimized prediction service with clean JSON responses
    """
    
    def __init__(self, data_path: str = "data/patient_visits.csv"):
        """Initialize the prediction service"""
        self.data_path = data_path
        self.forecaster = None
        self.outbreak_detector = OutbreakDetector()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize forecasting model if data exists
        if os.path.exists(data_path):
            self._initialize_forecaster()
    
    def _initialize_forecaster(self):
        """Initialize the forecasting model"""
        try:
            self.forecaster = PatientVolumeForecaster()
            df = self.forecaster.load_data(self.data_path)
            self.forecaster.train_model(df, test_split=0.2)
        except Exception as e:
            print(f"Warning: Could not initialize forecaster: {e}")
            self.forecaster = None
    
    def analyze_triage(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patient for triage (integrates with existing AI triage service)
        
        Args:
            patient_data: {
                "age": int,
                "gender": str,
                "symptoms": List[str],
                "duration": str,
                "vital_signs": Dict,
                "medical_history": str (optional)
            }
        
        Returns:
            Clean JSON response for API
        """
        try:
            # Import AI triage service
            from ai_triage_service_v2 import AITriageService
            
            # Initialize triage service
            triage_service = AITriageService()
            
            # Analyze patient
            result = triage_service.analyze_patient(patient_data)
            
            # Clean response for API
            return {
                "success": True,
                "data": {
                    "triage_level": result.get("triage_level"),
                    "triage_label": result.get("triage_label"),
                    "confidence": result.get("confidence", 0),
                    "conditions": result.get("conditions", []),
                    "immediate_actions": result.get("immediate_actions", []),
                    "referral_needed": result.get("referral_needed", False),
                    "referral_reason": result.get("referral_reason", ""),
                    "recommended_tests": result.get("recommended_tests", []),
                    "warning_signs": result.get("warning_signs", []),
                    "patient_advice": result.get("patient_advice", ""),
                    "response_time": result.get("response_time", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "TRIAGE_ERROR",
                    "message": str(e),
                    "user_message": "Unable to analyze patient symptoms. Please try again."
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def get_patient_forecast(self, facility_id: Optional[str] = None, 
                            days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get patient volume forecast
        
        Args:
            facility_id: Optional facility identifier
            days_ahead: Number of days to forecast (1-30)
        
        Returns:
            Clean JSON response
        """
        if not self.forecaster:
            return {
                "success": False,
                "error": {
                    "code": "FORECAST_UNAVAILABLE",
                    "message": "Forecasting model not available",
                    "user_message": "Patient volume forecasting is temporarily unavailable."
                },
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Validate input
            if not (1 <= days_ahead <= 30):
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_DAYS",
                        "message": f"days_ahead must be between 1 and 30, got {days_ahead}",
                        "user_message": "Forecast period must be between 1 and 30 days."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate forecast
            forecast_df = self.forecaster.generate_forecast(days_ahead)
            
            # Convert to clean JSON
            forecast_data = []
            for _, row in forecast_df.iterrows():
                forecast_data.append({
                    "date": row['ds'].strftime('%Y-%m-%d'),
                    "day_of_week": row['ds'].strftime('%A'),
                    "predicted_patients": int(row['yhat']),
                    "lower_bound": int(row['yhat_lower']),
                    "upper_bound": int(row['yhat_upper'])
                })
            
            # Generate summary
            summary = self.forecaster.get_forecast_summary(forecast_df)
            
            return {
                "success": True,
                "data": {
                    "facility_id": facility_id,
                    "forecast_period": f"{forecast_df['ds'].min().strftime('%Y-%m-%d')} to {forecast_df['ds'].max().strftime('%Y-%m-%d')}",
                    "days_ahead": days_ahead,
                    "forecast": forecast_data,
                    "summary": {
                        "total_predicted_patients": summary['total_predicted_patients'],
                        "average_daily_patients": summary['average_daily_patients'],
                        "min_daily_patients": summary['min_daily_patients'],
                        "max_daily_patients": summary['max_daily_patients'],
                        "peak_day": summary['peak_day'],
                        "lowest_day": summary['lowest_day']
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "FORECAST_ERROR",
                    "message": str(e),
                    "user_message": "Unable to generate patient forecast. Please try again later."
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def check_outbreak(self, disease: str, region: str, 
                      current_cases: int, historical_cases: List[int],
                      time_period: str = "weekly") -> Dict[str, Any]:
        """
        Check for disease outbreak
        
        Args:
            disease: Disease name
            region: Geographic region
            current_cases: Current period case count
            historical_cases: List of historical case counts
            time_period: "daily", "weekly", or "monthly"
        
        Returns:
            Clean JSON response
        """
        try:
            # Validate inputs
            if not disease or not region:
                return {
                    "success": False,
                    "error": {
                        "code": "MISSING_PARAMETERS",
                        "message": "disease and region are required",
                        "user_message": "Disease name and region are required for outbreak analysis."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            if current_cases < 0:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_CASES",
                        "message": "current_cases cannot be negative",
                        "user_message": "Current case count cannot be negative."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Analyze outbreak
            analysis = self.outbreak_detector.detect_outbreak(
                disease, current_cases, historical_cases, time_period
            )
            
            return {
                "success": True,
                "data": {
                    "disease": analysis["disease"],
                    "region": region,
                    "time_period": time_period,
                    "is_outbreak": analysis["is_outbreak"],
                    "severity": analysis["severity"],
                    "z_score": analysis["z_score"],
                    "current_cases": analysis["current_cases"],
                    "historical_average": analysis["historical_average"],
                    "multiplier": analysis["multiplier"],
                    "alert_message": analysis["alert_message"],
                    "recommendations": analysis["recommendations"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "OUTBREAK_ERROR",
                    "message": str(e),
                    "user_message": "Unable to analyze outbreak risk. Please check your data."
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def recommend_resources(self, predicted_patients: int, 
                          current_staff: Dict[str, int] = None,
                          facility_type: str = "standard") -> Dict[str, Any]:
        """
        Get resource optimization recommendations
        
        Args:
            predicted_patients: Expected number of patients
            current_staff: Current staff levels
            facility_type: "standard", "busy", or "rural"
        
        Returns:
            Clean JSON response
        """
        try:
            # Validate inputs
            if predicted_patients < 0:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_PATIENTS",
                        "message": "predicted_patients cannot be negative",
                        "user_message": "Predicted patient count cannot be negative."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            if facility_type not in ["standard", "busy", "rural"]:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_FACILITY_TYPE",
                        "message": f"facility_type must be 'standard', 'busy', or 'rural', got '{facility_type}'",
                        "user_message": "Facility type must be standard, busy, or rural."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get recommendations
            analysis = self.resource_optimizer.recommend_staffing(
                predicted_patients, current_staff, facility_type
            )
            
            return {
                "success": True,
                "data": {
                    "predicted_patients": analysis["predicted_patients"],
                    "facility_type": analysis["facility_type"],
                    "current_staff": analysis["current_staff"],
                    "required_staff": analysis["required_staff"],
                    "staff_gaps": analysis["staff_gaps"],
                    "urgency": analysis["urgency"],
                    "workload_per_staff": analysis["workload_per_staff"],
                    "recommendations": analysis["recommendations"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "RESOURCE_ERROR",
                    "message": str(e),
                    "user_message": "Unable to generate resource recommendations. Please try again."
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_inventory(self, inventory_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze inventory for stockout risks
        
        Args:
            inventory_data: Dictionary with drug inventory information
        
        Returns:
            Clean JSON response
        """
        try:
            # Validate input
            if not inventory_data:
                return {
                    "success": False,
                    "error": {
                        "code": "EMPTY_INVENTORY",
                        "message": "inventory_data cannot be empty",
                        "user_message": "Inventory data is required for analysis."
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Analyze inventory
            analysis = self.resource_optimizer.analyze_inventory(inventory_data)
            
            return {
                "success": True,
                "data": {
                    "overall_status": analysis["overall_status"],
                    "total_drugs": analysis["total_drugs"],
                    "critical_alerts": analysis["critical_alerts"],
                    "warning_alerts": analysis["warning_alerts"],
                    "drug_analyses": analysis["drug_analyses"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INVENTORY_ERROR",
                    "message": str(e),
                    "user_message": "Unable to analyze inventory. Please check your data."
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "success": True,
            "data": {
                "forecasting_model": self.forecaster is not None,
                "outbreak_detector": True,
                "resource_optimizer": True,
                "data_path": self.data_path,
                "data_available": os.path.exists(self.data_path),
                "timestamp": datetime.now().isoformat()
            }
        }


# Convenience function for backend integration
def create_prediction_service() -> BackendPredictionService:
    """Create and return a prediction service instance"""
    return BackendPredictionService()


if __name__ == "__main__":
    # Test the backend service
    service = create_prediction_service()
    
    # Test triage
    patient_data = {
        "age": 30,
        "gender": "Male",
        "symptoms": ["fever", "headache"],
        "duration": "3 days",
        "vital_signs": {"temperature": 38.5}
    }
    
    result = service.analyze_triage(patient_data)
    print("Triage Test:", json.dumps(result, indent=2))
