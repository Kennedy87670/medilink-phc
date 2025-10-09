"""
MediLink PHC - Prediction Service Wrapper
Unified interface for all AI models - ready for backend integration
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from volume_forecast_model import PatientVolumeForecaster
from outbreak_detector import OutbreakDetector
from resource_optimizer import ResourceOptimizer

class PredictionService:
    """
    Unified prediction service that wraps all AI models
    Ready for backend API integration
    """
    
    def __init__(self, data_path: str = "data/patient_visits.csv"):
        """
        Initialize the prediction service with all models
        
        Args:
            data_path: Path to patient visit data for forecasting
        """
        self.data_path = data_path
        self.forecaster = None
        self.outbreak_detector = OutbreakDetector()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize forecasting model if data exists
        if os.path.exists(data_path):
            self._initialize_forecaster()
        
        print("✅ PredictionService initialized successfully")
    
    def _initialize_forecaster(self):
        """Initialize the forecasting model"""
        try:
            self.forecaster = PatientVolumeForecaster()
            df = self.forecaster.load_data(self.data_path)
            self.forecaster.train_model(df, test_split=0.2)
            print("✅ Forecasting model loaded and trained")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize forecaster: {e}")
            self.forecaster = None
    
    def get_patient_forecast(self, facility_id: Optional[str] = None, 
                            days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get patient volume forecast for the next N days
        
        Args:
            facility_id: Optional facility identifier (for future multi-facility support)
            days_ahead: Number of days to forecast (default: 7)
        
        Returns:
            JSON response with forecast data
        """
        if not self.forecaster:
            return {
                "error": "Forecasting model not available",
                "message": "Patient visit data not found or model failed to initialize",
                "facility_id": facility_id,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Generate forecast
            forecast_df = self.forecaster.generate_forecast(days_ahead)
            
            # Convert to JSON-serializable format
            forecast_data = []
            for _, row in forecast_df.iterrows():
                forecast_data.append({
                    "date": row['ds'].strftime('%Y-%m-%d'),
                    "day_of_week": row['ds'].strftime('%A'),
                    "predicted_patients": int(row['yhat']),
                    "lower_bound": int(row['yhat_lower']),
                    "upper_bound": int(row['yhat_upper']),
                    "confidence_interval": f"{int(row['yhat_lower'])}-{int(row['yhat_upper'])}"
                })
            
            # Generate summary
            summary = self.forecaster.get_forecast_summary(forecast_df)
            
            return {
                "success": True,
                "facility_id": facility_id,
                "forecast_period": f"{forecast_df['ds'].min().strftime('%Y-%m-%d')} to {forecast_df['ds'].max().strftime('%Y-%m-%d')}",
                "days_ahead": days_ahead,
                "forecast_data": forecast_data,
                "summary": {
                    "total_predicted_patients": summary['total_predicted_patients'],
                    "average_daily_patients": summary['average_daily_patients'],
                    "min_daily_patients": summary['min_daily_patients'],
                    "max_daily_patients": summary['max_daily_patients'],
                    "peak_day": summary['peak_day'],
                    "lowest_day": summary['lowest_day']
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "facility_id": facility_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_outbreak_risk(self, disease: str, region: str, 
                           current_cases: int, historical_cases: List[int],
                           time_period: str = "weekly") -> Dict[str, Any]:
        """
        Check for disease outbreak using statistical analysis
        
        Args:
            disease: Disease name (e.g., "Malaria")
            region: Geographic region
            current_cases: Current period case count
            historical_cases: List of historical case counts
            time_period: "daily", "weekly", or "monthly"
        
        Returns:
            JSON response with outbreak analysis
        """
        try:
            analysis = self.outbreak_detector.detect_outbreak(
                disease, current_cases, historical_cases, time_period
            )
            
            # Add region information
            analysis["region"] = region
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "disease": disease,
                "region": region,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_multiple_outbreaks(self, outbreak_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze multiple diseases for outbreaks
        
        Args:
            outbreak_data: Dictionary with disease data
                Example: {
                    "Malaria": {"current": 45, "historical": [20, 22, 18, 25, 21]},
                    "Typhoid": {"current": 12, "historical": [8, 10, 9, 11, 7]}
                }
        
        Returns:
            JSON response with multi-disease analysis
        """
        try:
            analysis = self.outbreak_detector.analyze_multiple_diseases(outbreak_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
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
            JSON response with staffing recommendations
        """
        try:
            analysis = self.resource_optimizer.recommend_staffing(
                predicted_patients, current_staff, facility_type
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "predicted_patients": predicted_patients,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_inventory(self, inventory_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze inventory for stockout risks
        
        Args:
            inventory_data: Dictionary with drug inventory information
        
        Returns:
            JSON response with inventory analysis
        """
        try:
            analysis = self.resource_optimizer.analyze_inventory(inventory_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_comprehensive_analysis(self, facility_id: str, 
                                 outbreak_data: Dict[str, Dict] = None,
                                 inventory_data: Dict[str, Dict] = None,
                                 current_staff: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Get comprehensive analysis combining all models
        
        Args:
            facility_id: Facility identifier
            outbreak_data: Disease outbreak data
            inventory_data: Drug inventory data
            current_staff: Current staffing levels
        
        Returns:
            Comprehensive analysis combining all models
        """
        try:
            # Get patient forecast
            forecast = self.get_patient_forecast(facility_id, days_ahead=7)
            
            # Get outbreak analysis if data provided
            outbreak_analysis = None
            if outbreak_data:
                outbreak_analysis = self.analyze_multiple_outbreaks(outbreak_data)
            
            # Get resource recommendations
            resource_analysis = None
            if forecast.get("success") and current_staff:
                predicted_patients = forecast["summary"]["average_daily_patients"]
                resource_analysis = self.recommend_resources(
                    predicted_patients, current_staff
                )
            
            # Get inventory analysis if data provided
            inventory_analysis = None
            if inventory_data:
                inventory_analysis = self.analyze_inventory(inventory_data)
            
            return {
                "success": True,
                "facility_id": facility_id,
                "forecast": forecast,
                "outbreak_analysis": outbreak_analysis,
                "resource_analysis": resource_analysis,
                "inventory_analysis": inventory_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "facility_id": facility_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of all prediction services
        
        Returns:
            Service status information
        """
        status = {
            "forecasting_model": self.forecaster is not None,
            "outbreak_detector": True,  # Always available
            "resource_optimizer": True,  # Always available
            "data_path": self.data_path,
            "data_available": os.path.exists(self.data_path),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.forecaster:
            status["forecasting_model_trained"] = self.forecaster.trained
        
        return status


def test_prediction_service():
    """Test the complete prediction service"""
    print("🧪 Testing Prediction Service")
    print("=" * 50)
    
    # Initialize service
    service = PredictionService()
    
    # Test service status
    print("\n📊 SERVICE STATUS")
    print("-" * 20)
    status = service.get_service_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    # Test patient forecast
    print(f"\n🔮 PATIENT FORECAST")
    print("-" * 20)
    forecast = service.get_patient_forecast("PHC_001", days_ahead=7)
    
    if forecast.get("success"):
        print(f"Forecast Period: {forecast['forecast_period']}")
        print(f"Average Daily Patients: {forecast['summary']['average_daily_patients']}")
        print(f"Peak Day: {forecast['summary']['peak_day']}")
        
        print(f"\nDaily Forecast:")
        for day in forecast['forecast_data'][:3]:  # Show first 3 days
            print(f"  {day['date']} ({day['day_of_week']}): {day['predicted_patients']} patients")
    else:
        print(f"Forecast Error: {forecast.get('error')}")
    
    # Test outbreak detection
    print(f"\n🚨 OUTBREAK DETECTION")
    print("-" * 20)
    outbreak_data = {
        "Malaria": {"current": 65, "historical": [20, 22, 18, 25, 21, 23, 19, 24, 20, 22]},
        "Typhoid": {"current": 12, "historical": [10, 11, 9, 12, 10, 11, 9, 12, 10, 11]}
    }
    
    outbreak_analysis = service.analyze_multiple_outbreaks(outbreak_data)
    
    if outbreak_analysis.get("success"):
        summary = outbreak_analysis["analysis"]["summary"]
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Outbreaks Detected: {summary['outbreaks_detected']}")
        print(f"Severe Outbreaks: {summary['severe_outbreaks']}")
    else:
        print(f"Outbreak Analysis Error: {outbreak_analysis.get('error')}")
    
    # Test resource recommendations
    print(f"\n👥 RESOURCE RECOMMENDATIONS")
    print("-" * 20)
    current_staff = {"nurses": 3, "doctors": 1, "pharmacists": 1}
    
    if forecast.get("success"):
        predicted_patients = forecast["summary"]["average_daily_patients"]
        resource_analysis = service.recommend_resources(
            predicted_patients, current_staff
        )
        
        if resource_analysis.get("success"):
            analysis = resource_analysis["analysis"]
            print(f"Urgency: {analysis['urgency'].upper()}")
            print(f"Required Staff: {analysis['required_staff']['nurses']} nurses, "
                  f"{analysis['required_staff']['doctors']} doctors")
            
            print(f"Top Recommendations:")
            for rec in analysis['recommendations'][:2]:
                print(f"  • {rec}")
        else:
            print(f"Resource Analysis Error: {resource_analysis.get('error')}")
    
    # Test inventory analysis
    print(f"\n💊 INVENTORY ANALYSIS")
    print("-" * 20)
    inventory_data = {
        "ACT": {"current_stock": 50, "daily_usage": 8},
        "ORS": {"current_stock": 200, "daily_usage": 15},
        "Penicillin": {"current_stock": 20, "daily_usage": 5}
    }
    
    inventory_analysis = service.analyze_inventory(inventory_data)
    
    if inventory_analysis.get("success"):
        analysis = inventory_analysis["analysis"]
        print(f"Overall Status: {analysis['overall_status']}")
        print(f"Critical Alerts: {analysis['critical_alerts']}")
        print(f"Warning Alerts: {analysis['warning_alerts']}")
    else:
        print(f"Inventory Analysis Error: {inventory_analysis.get('error')}")
    
    # Test comprehensive analysis
    print(f"\n📋 COMPREHENSIVE ANALYSIS")
    print("-" * 20)
    comprehensive = service.get_comprehensive_analysis(
        "PHC_001",
        outbreak_data=outbreak_data,
        inventory_data=inventory_data,
        current_staff=current_staff
    )
    
    if comprehensive.get("success"):
        print("✅ All analyses completed successfully")
        print(f"Facility: {comprehensive['facility_id']}")
        
        # Count successful analyses
        analyses = ["forecast", "outbreak_analysis", "resource_analysis", "inventory_analysis"]
        successful = sum(1 for analysis in analyses if comprehensive.get(analysis, {}).get("success"))
        print(f"Successful Analyses: {successful}/{len(analyses)}")
    else:
        print(f"Comprehensive Analysis Error: {comprehensive.get('error')}")
    
    print(f"\n✅ Prediction Service testing complete!")
    return service


if __name__ == "__main__":
    service = test_prediction_service()
