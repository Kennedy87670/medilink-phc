"""
MediLink PHC - Outbreak Detection System
Uses statistical Z-score method to detect disease outbreaks
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class OutbreakDetector:
    """
    Detects disease outbreaks using statistical analysis
    """
    
    def __init__(self):
        self.outbreak_threshold = 2.0  # Z-score threshold for outbreak
        self.severe_threshold = 3.0    # Z-score threshold for severe outbreak
        
    def detect_outbreak(self, disease_name: str, current_cases: int, 
                       historical_cases: List[int], 
                       time_period: str = "weekly") -> Dict:
        """
        Detect outbreak using Z-score method
        
        Args:
            disease_name: Name of the disease (e.g., "Malaria")
            current_cases: Current period case count
            historical_cases: List of historical case counts
            time_period: "daily", "weekly", or "monthly"
        
        Returns:
            Dictionary with outbreak analysis
        """
        
        # Validate inputs
        if not historical_cases or len(historical_cases) < 3:
            return self._create_no_data_response(disease_name, current_cases)
        
        # Remove zeros and outliers for better statistics
        clean_historical = self._clean_historical_data(historical_cases)
        
        if len(clean_historical) < 3:
            return self._create_no_data_response(disease_name, current_cases)
        
        # Calculate statistics
        mean_cases = np.mean(clean_historical)
        std_cases = np.std(clean_historical, ddof=1)  # Sample standard deviation
        
        # Handle edge case where std is 0
        if std_cases == 0:
            std_cases = 1.0
        
        # Calculate Z-score
        z_score = (current_cases - mean_cases) / std_cases
        
        # Determine outbreak status
        is_outbreak = z_score >= self.outbreak_threshold
        is_severe = z_score >= self.severe_threshold
        
        # Calculate multiplier
        multiplier = current_cases / mean_cases if mean_cases > 0 else 0
        
        # Generate alert message
        alert_message = self._generate_alert_message(
            disease_name, current_cases, mean_cases, multiplier, z_score, is_severe
        )
        
        # Determine severity level
        if is_severe:
            severity = "severe"
        elif is_outbreak:
            severity = "moderate"
        else:
            severity = "normal"
        
        # Create response
        response = {
            "disease": disease_name,
            "time_period": time_period,
            "is_outbreak": is_outbreak,
            "severity": severity,
            "z_score": round(z_score, 2),
            "current_cases": current_cases,
            "historical_average": round(mean_cases, 1),
            "historical_std": round(std_cases, 1),
            "multiplier": round(multiplier, 1),
            "alert_message": alert_message,
            "recommendations": self._get_recommendations(severity, disease_name),
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _clean_historical_data(self, historical_cases: List[int]) -> List[int]:
        """
        Clean historical data by removing outliers and zeros
        """
        # Convert to numpy array for easier manipulation
        data = np.array(historical_cases)
        
        # Remove zeros (might indicate missing data)
        data = data[data > 0]
        
        if len(data) == 0:
            return []
        
        # Remove extreme outliers using IQR method
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Filter outliers
        clean_data = data[(data >= lower_bound) & (data <= upper_bound)]
        
        return clean_data.tolist()
    
    def _create_no_data_response(self, disease_name: str, current_cases: int) -> Dict:
        """
        Create response when insufficient historical data
        """
        return {
            "disease": disease_name,
            "is_outbreak": False,
            "severity": "unknown",
            "z_score": 0.0,
            "current_cases": current_cases,
            "historical_average": 0,
            "historical_std": 0,
            "multiplier": 0,
            "alert_message": f"Insufficient historical data for {disease_name} outbreak detection",
            "recommendations": ["Collect more historical data", "Monitor closely"],
            "timestamp": datetime.now().isoformat(),
            "error": "insufficient_data"
        }
    
    def _generate_alert_message(self, disease_name: str, current_cases: int, 
                               mean_cases: float, multiplier: float, 
                               z_score: float, is_severe: bool) -> str:
        """
        Generate human-readable alert message
        """
        if is_severe:
            return f"🚨 SEVERE OUTBREAK ALERT: {disease_name} cases are {multiplier:.1f}x above normal ({current_cases} vs {mean_cases:.0f} average)"
        elif z_score >= self.outbreak_threshold:
            return f"⚠️ OUTBREAK ALERT: {disease_name} cases are {multiplier:.1f}x above normal ({current_cases} vs {mean_cases:.0f} average)"
        else:
            return f"✅ Normal levels: {disease_name} cases are within normal range ({current_cases} vs {mean_cases:.0f} average)"
    
    def _get_recommendations(self, severity: str, disease_name: str) -> List[str]:
        """
        Get recommendations based on outbreak severity
        """
        recommendations = []
        
        if severity == "severe":
            recommendations.extend([
                "Immediate notification to health authorities",
                "Activate emergency response protocols",
                "Increase surveillance and testing",
                "Consider isolation/quarantine measures",
                "Prepare for increased patient load",
                "Alert nearby healthcare facilities"
            ])
        elif severity == "moderate":
            recommendations.extend([
                "Increase monitoring frequency",
                "Prepare additional resources",
                "Notify health authorities",
                "Review infection control measures",
                "Consider targeted interventions"
            ])
        else:
            recommendations.extend([
                "Continue routine monitoring",
                "Maintain standard protocols",
                "Document case patterns"
            ])
        
        # Add disease-specific recommendations
        if disease_name.lower() == "malaria":
            recommendations.append("Distribute mosquito nets and repellents")
            recommendations.append("Increase vector control measures")
        elif disease_name.lower() == "cholera":
            recommendations.append("Ensure clean water supply")
            recommendations.append("Promote hand hygiene")
        elif disease_name.lower() == "meningitis":
            recommendations.append("Consider mass vaccination if available")
            recommendations.append("Implement respiratory precautions")
        
        return recommendations
    
    def analyze_multiple_diseases(self, disease_data: Dict[str, Dict]) -> Dict:
        """
        Analyze multiple diseases for outbreaks
        
        Args:
            disease_data: Dictionary with disease names as keys and case data as values
                Example: {
                    "Malaria": {"current": 45, "historical": [20, 22, 18, 25, 21]},
                    "Typhoid": {"current": 12, "historical": [8, 10, 9, 11, 7]}
                }
        
        Returns:
            Dictionary with analysis for all diseases
        """
        results = {}
        outbreak_count = 0
        severe_outbreak_count = 0
        
        for disease, data in disease_data.items():
            current_cases = data.get("current", 0)
            historical_cases = data.get("historical", [])
            
            analysis = self.detect_outbreak(disease, current_cases, historical_cases)
            results[disease] = analysis
            
            if analysis["is_outbreak"]:
                outbreak_count += 1
            if analysis["severity"] == "severe":
                severe_outbreak_count += 1
        
        # Overall summary
        summary = {
            "total_diseases_monitored": len(disease_data),
            "outbreaks_detected": outbreak_count,
            "severe_outbreaks": severe_outbreak_count,
            "overall_status": "CRITICAL" if severe_outbreak_count > 0 else 
                            "ALERT" if outbreak_count > 0 else "NORMAL",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "summary": summary,
            "disease_analyses": results
        }
    
    def generate_outbreak_report(self, analysis_results: Dict) -> str:
        """
        Generate a formatted outbreak report
        """
        summary = analysis_results["summary"]
        diseases = analysis_results["disease_analyses"]
        
        report = f"""
🏥 MEDILINK PHC - OUTBREAK DETECTION REPORT
{'='*60}
Generated: {summary['timestamp']}

OVERALL STATUS: {summary['overall_status']}
Diseases Monitored: {summary['total_diseases_monitored']}
Outbreaks Detected: {summary['outbreaks_detected']}
Severe Outbreaks: {summary['severe_outbreaks']}

DETAILED ANALYSIS:
{'-'*40}
"""
        
        for disease, analysis in diseases.items():
            status_icon = "🚨" if analysis["severity"] == "severe" else "⚠️" if analysis["is_outbreak"] else "✅"
            
            report += f"""
{status_icon} {disease.upper()}
   Current Cases: {analysis['current_cases']}
   Historical Average: {analysis['historical_average']}
   Z-Score: {analysis['z_score']}
   Status: {analysis['severity'].upper()}
   Alert: {analysis['alert_message']}
   
   Recommendations:
"""
            for rec in analysis['recommendations'][:3]:  # Show top 3 recommendations
                report += f"   • {rec}\n"
        
        return report


def test_outbreak_detector():
    """
    Test the outbreak detection system with sample data
    """
    print("🧪 Testing Outbreak Detection System")
    print("=" * 50)
    
    detector = OutbreakDetector()
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Malaria Cases",
            "disease": "Malaria",
            "current": 25,
            "historical": [20, 22, 18, 25, 21, 23, 19, 24, 20, 22]
        },
        {
            "name": "Malaria Outbreak",
            "disease": "Malaria", 
            "current": 65,
            "historical": [20, 22, 18, 25, 21, 23, 19, 24, 20, 22]
        },
        {
            "name": "Severe Cholera Outbreak",
            "disease": "Cholera",
            "current": 45,
            "historical": [8, 10, 9, 11, 7, 9, 8, 10, 9, 7]
        },
        {
            "name": "Normal Typhoid",
            "disease": "Typhoid",
            "current": 12,
            "historical": [10, 11, 9, 12, 10, 11, 9, 12, 10, 11]
        }
    ]
    
    for test in test_cases:
        print(f"\n🔬 {test['name']}")
        print("-" * 30)
        
        result = detector.detect_outbreak(
            test["disease"], 
            test["current"], 
            test["historical"]
        )
        
        print(f"Disease: {result['disease']}")
        print(f"Current Cases: {result['current_cases']}")
        print(f"Historical Average: {result['historical_average']}")
        print(f"Z-Score: {result['z_score']}")
        print(f"Outbreak: {'YES' if result['is_outbreak'] else 'NO'}")
        print(f"Severity: {result['severity'].upper()}")
        print(f"Alert: {result['alert_message']}")
    
    # Test multiple diseases
    print(f"\n🔬 MULTIPLE DISEASES ANALYSIS")
    print("-" * 40)
    
    multi_disease_data = {
        "Malaria": {"current": 65, "historical": [20, 22, 18, 25, 21, 23, 19, 24, 20, 22]},
        "Typhoid": {"current": 12, "historical": [10, 11, 9, 12, 10, 11, 9, 12, 10, 11]},
        "Cholera": {"current": 45, "historical": [8, 10, 9, 11, 7, 9, 8, 10, 9, 7]},
        "Meningitis": {"current": 3, "historical": [2, 1, 2, 3, 1, 2, 1, 3, 2, 1]}
    }
    
    multi_analysis = detector.analyze_multiple_diseases(multi_disease_data)
    
    print(f"Overall Status: {multi_analysis['summary']['overall_status']}")
    print(f"Outbreaks Detected: {multi_analysis['summary']['outbreaks_detected']}")
    print(f"Severe Outbreaks: {multi_analysis['summary']['severe_outbreaks']}")
    
    # Generate report
    report = detector.generate_outbreak_report(multi_analysis)
    print(f"\n📄 OUTBREAK REPORT:")
    print(report)
    
    return detector


if __name__ == "__main__":
    detector = test_outbreak_detector()
