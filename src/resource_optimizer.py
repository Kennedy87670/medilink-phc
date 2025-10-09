"""
MediLink PHC - Resource Optimization System
Provides staffing and inventory recommendations based on patient forecasts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class ResourceOptimizer:
    """
    Optimizes PHC resources based on patient volume forecasts
    """
    
    def __init__(self):
        # PHC capacity parameters
        self.nurse_capacity = 30  # Patients per nurse per day
        self.doctor_capacity = 50  # Patients per doctor per day
        self.pharmacist_capacity = 100  # Prescriptions per pharmacist per day
        
        # Inventory parameters
        self.drug_alert_days = 7  # Alert when < 7 days remaining
        self.critical_drug_alert_days = 14  # Alert critical drugs earlier
        
        # Critical drugs that need longer lead time
        self.critical_drugs = [
            "ACT", "Artemether", "Quinine", "Chloroquine",  # Malaria
            "Ceftriaxone", "Penicillin", "Amoxicillin",    # Antibiotics
            "ORS", "Zinc", "Vitamin A",                    # Nutrition
            "Insulin", "Metformin",                         # Diabetes
            "Salbutamol", "Prednisolone"                    # Respiratory
        ]
    
    def recommend_staffing(self, predicted_patients: int, 
                          current_staff: Dict[str, int] = None,
                          facility_type: str = "standard") -> Dict:
        """
        Recommend optimal staffing based on predicted patient volume
        
        Args:
            predicted_patients: Expected number of patients
            current_staff: Current staff levels {"nurses": 3, "doctors": 1, "pharmacists": 1}
            facility_type: "standard", "busy", or "rural"
        
        Returns:
            Staffing recommendations
        """
        
        # Default current staff if not provided
        if current_staff is None:
            current_staff = {"nurses": 3, "doctors": 1, "pharmacists": 1}
        
        # Adjust capacity based on facility type
        capacity_multiplier = self._get_capacity_multiplier(facility_type)
        nurse_capacity = self.nurse_capacity * capacity_multiplier
        doctor_capacity = self.doctor_capacity * capacity_multiplier
        pharmacist_capacity = self.pharmacist_capacity * capacity_multiplier
        
        # Calculate required staff
        required_nurses = max(1, int(np.ceil(predicted_patients / nurse_capacity)))
        required_doctors = max(1, int(np.ceil(predicted_patients / doctor_capacity)))
        required_pharmacists = max(1, int(np.ceil(predicted_patients / pharmacist_capacity)))
        
        # Current vs required comparison
        current_nurses = current_staff.get("nurses", 0)
        current_doctors = current_staff.get("doctors", 0)
        current_pharmacists = current_staff.get("pharmacists", 0)
        
        # Calculate gaps
        nurse_gap = required_nurses - current_nurses
        doctor_gap = required_doctors - current_doctors
        pharmacist_gap = required_pharmacists - current_pharmacists
        
        # Determine urgency
        urgency = self._determine_staffing_urgency(predicted_patients, current_staff, 
                                                 required_nurses, required_doctors, required_pharmacists)
        
        # Generate recommendations
        recommendations = self._generate_staffing_recommendations(
            nurse_gap, doctor_gap, pharmacist_gap, urgency
        )
        
        # Calculate workload per staff member
        workload_nurses = predicted_patients / max(1, current_nurses)
        workload_doctors = predicted_patients / max(1, current_doctors)
        workload_pharmacists = predicted_patients / max(1, current_pharmacists)
        
        return {
            "predicted_patients": predicted_patients,
            "facility_type": facility_type,
            "current_staff": current_staff,
            "required_staff": {
                "nurses": required_nurses,
                "doctors": required_doctors,
                "pharmacists": required_pharmacists
            },
            "staff_gaps": {
                "nurses": nurse_gap,
                "doctors": doctor_gap,
                "pharmacists": pharmacist_gap
            },
            "urgency": urgency,
            "workload_per_staff": {
                "nurses": round(workload_nurses, 1),
                "doctors": round(workload_doctors, 1),
                "pharmacists": round(workload_pharmacists, 1)
            },
            "recommendations": recommendations,
            "capacity_utilization": {
                "nurse_capacity": nurse_capacity,
                "doctor_capacity": doctor_capacity,
                "pharmacist_capacity": pharmacist_capacity
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_capacity_multiplier(self, facility_type: str) -> float:
        """Get capacity multiplier based on facility type"""
        multipliers = {
            "rural": 0.8,    # Lower capacity in rural areas
            "standard": 1.0,  # Standard capacity
            "busy": 1.2      # Higher capacity in busy areas
        }
        return multipliers.get(facility_type, 1.0)
    
    def _determine_staffing_urgency(self, predicted_patients: int, current_staff: Dict,
                                   required_nurses: int, required_doctors: int, 
                                   required_pharmacists: int) -> str:
        """Determine urgency level for staffing"""
        current_total = sum(current_staff.values())
        required_total = required_nurses + required_doctors + required_pharmacists
        
        if required_total > current_total * 1.5:
            return "critical"
        elif required_total > current_total * 1.2:
            return "high"
        elif required_total > current_total:
            return "moderate"
        else:
            return "low"
    
    def _generate_staffing_recommendations(self, nurse_gap: int, doctor_gap: int, 
                                         pharmacist_gap: int, urgency: str) -> List[str]:
        """Generate specific staffing recommendations"""
        recommendations = []
        
        if urgency == "critical":
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED")
            recommendations.append("Contact district health office for emergency staffing")
            recommendations.append("Consider temporary staff from nearby facilities")
        
        if nurse_gap > 0:
            recommendations.append(f"Add {nurse_gap} nurse(s) - Current workload too high")
        elif nurse_gap < 0:
            recommendations.append(f"Consider reducing nurses by {abs(nurse_gap)} - Overstaffed")
        
        if doctor_gap > 0:
            recommendations.append(f"Add {doctor_gap} doctor(s) - Patient load exceeds capacity")
        elif doctor_gap < 0:
            recommendations.append(f"Consider reducing doctors by {abs(doctor_gap)} - Overstaffed")
        
        if pharmacist_gap > 0:
            recommendations.append(f"Add {pharmacist_gap} pharmacist(s) - Prescription load too high")
        elif pharmacist_gap < 0:
            recommendations.append(f"Consider reducing pharmacists by {abs(pharmacist_gap)} - Overstaffed")
        
        if urgency in ["critical", "high"]:
            recommendations.append("Implement extended hours if possible")
            recommendations.append("Prepare for patient overflow")
        
        return recommendations
    
    def predict_drug_stockout(self, drug_name: str, current_stock: int, 
                            daily_usage: float, lead_time_days: int = 7) -> Dict:
        """
        Predict when a drug will run out and generate alerts
        
        Args:
            drug_name: Name of the drug
            current_stock: Current stock level
            daily_usage: Average daily usage
            lead_time_days: Days needed to restock
        
        Returns:
            Stockout prediction and recommendations
        """
        
        if daily_usage <= 0:
            return {
                "drug_name": drug_name,
                "current_stock": current_stock,
                "daily_usage": daily_usage,
                "days_remaining": float('inf'),
                "stockout_date": None,
                "alert_level": "none",
                "recommendations": ["No usage data - monitor closely"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate days until stockout
        days_remaining = current_stock / daily_usage
        
        # Calculate stockout date
        stockout_date = datetime.now() + timedelta(days=int(days_remaining))
        
        # Determine alert level
        alert_level = self._determine_stockout_alert_level(
            drug_name, days_remaining, lead_time_days
        )
        
        # Generate recommendations
        recommendations = self._generate_stockout_recommendations(
            drug_name, days_remaining, lead_time_days, alert_level
        )
        
        return {
            "drug_name": drug_name,
            "current_stock": current_stock,
            "daily_usage": daily_usage,
            "days_remaining": round(days_remaining, 1),
            "stockout_date": stockout_date.strftime('%Y-%m-%d'),
            "alert_level": alert_level,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_stockout_alert_level(self, drug_name: str, days_remaining: float, 
                                       lead_time_days: int) -> str:
        """Determine alert level for stockout"""
        is_critical = drug_name in self.critical_drugs
        
        if is_critical:
            critical_threshold = self.critical_drug_alert_days
        else:
            critical_threshold = self.drug_alert_days
        
        if days_remaining <= lead_time_days:
            return "critical"
        elif days_remaining <= critical_threshold:
            return "warning"
        elif days_remaining <= critical_threshold * 2:
            return "caution"
        else:
            return "normal"
    
    def _generate_stockout_recommendations(self, drug_name: str, days_remaining: float,
                                         lead_time_days: int, alert_level: str) -> List[str]:
        """Generate stockout recommendations"""
        recommendations = []
        
        if alert_level == "critical":
            recommendations.append("🚨 IMMEDIATE ACTION: Order now!")
            recommendations.append("Contact emergency supply chain")
            recommendations.append("Consider borrowing from nearby facilities")
        elif alert_level == "warning":
            recommendations.append("⚠️ Order within 24 hours")
            recommendations.append("Contact district pharmacy")
        elif alert_level == "caution":
            recommendations.append("📋 Plan to order soon")
            recommendations.append("Monitor usage patterns")
        else:
            recommendations.append("✅ Stock levels adequate")
        
        # Add drug-specific recommendations
        if drug_name in self.critical_drugs:
            recommendations.append("Critical drug - prioritize restocking")
        
        return recommendations
    
    def analyze_inventory(self, inventory_data: Dict[str, Dict]) -> Dict:
        """
        Analyze entire inventory for stockout risks
        
        Args:
            inventory_data: Dictionary with drug names as keys and inventory info as values
                Example: {
                    "ACT": {"current_stock": 50, "daily_usage": 8},
                    "ORS": {"current_stock": 200, "daily_usage": 15}
                }
        
        Returns:
            Complete inventory analysis
        """
        analyses = {}
        critical_alerts = 0
        warning_alerts = 0
        
        for drug_name, data in inventory_data.items():
            analysis = self.predict_drug_stockout(
                drug_name, 
                data.get("current_stock", 0),
                data.get("daily_usage", 0)
            )
            analyses[drug_name] = analysis
            
            if analysis["alert_level"] == "critical":
                critical_alerts += 1
            elif analysis["alert_level"] == "warning":
                warning_alerts += 1
        
        # Overall inventory status
        total_drugs = len(inventory_data)
        if critical_alerts > 0:
            overall_status = "CRITICAL"
        elif warning_alerts > 0:
            overall_status = "WARNING"
        else:
            overall_status = "NORMAL"
        
        return {
            "overall_status": overall_status,
            "total_drugs": total_drugs,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "drug_analyses": analyses,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_resource_report(self, staffing_analysis: Dict, 
                               inventory_analysis: Dict) -> str:
        """Generate comprehensive resource report"""
        
        report = f"""
🏥 MEDILINK PHC - RESOURCE OPTIMIZATION REPORT
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STAFFING ANALYSIS:
{'-'*30}
Predicted Patients: {staffing_analysis['predicted_patients']}
Urgency Level: {staffing_analysis['urgency'].upper()}

Current Staff:
  Nurses: {staffing_analysis['current_staff']['nurses']}
  Doctors: {staffing_analysis['current_staff']['doctors']}
  Pharmacists: {staffing_analysis['current_staff']['pharmacists']}

Required Staff:
  Nurses: {staffing_analysis['required_staff']['nurses']}
  Doctors: {staffing_analysis['required_staff']['doctors']}
  Pharmacists: {staffing_analysis['required_staff']['pharmacists']}

Recommendations:
"""
        for rec in staffing_analysis['recommendations']:
            report += f"  • {rec}\n"
        
        report += f"""
INVENTORY ANALYSIS:
{'-'*30}
Overall Status: {inventory_analysis['overall_status']}
Critical Alerts: {inventory_analysis['critical_alerts']}
Warning Alerts: {inventory_analysis['warning_alerts']}

Drug Stockout Risks:
"""
        
        for drug, analysis in inventory_analysis['drug_analyses'].items():
            if analysis['alert_level'] in ['critical', 'warning']:
                status_icon = "🚨" if analysis['alert_level'] == "critical" else "⚠️"
                report += f"  {status_icon} {drug}: {analysis['days_remaining']} days remaining\n"
        
        return report


def test_resource_optimizer():
    """Test the resource optimization system"""
    print("🧪 Testing Resource Optimization System")
    print("=" * 50)
    
    optimizer = ResourceOptimizer()
    
    # Test staffing recommendations
    print("\n👥 STAFFING RECOMMENDATIONS")
    print("-" * 30)
    
    staffing_scenarios = [
        {"patients": 120, "staff": {"nurses": 3, "doctors": 1, "pharmacists": 1}},
        {"patients": 200, "staff": {"nurses": 2, "doctors": 1, "pharmacists": 1}},
        {"patients": 80, "staff": {"nurses": 4, "doctors": 2, "pharmacists": 2}}
    ]
    
    for i, scenario in enumerate(staffing_scenarios, 1):
        print(f"\nScenario {i}: {scenario['patients']} patients")
        analysis = optimizer.recommend_staffing(
            scenario['patients'], 
            scenario['staff']
        )
        
        print(f"Urgency: {analysis['urgency'].upper()}")
        print(f"Required: {analysis['required_staff']['nurses']} nurses, "
              f"{analysis['required_staff']['doctors']} doctors, "
              f"{analysis['required_staff']['pharmacists']} pharmacists")
        
        for rec in analysis['recommendations'][:2]:  # Show top 2 recommendations
            print(f"  • {rec}")
    
    # Test inventory analysis
    print(f"\n💊 INVENTORY ANALYSIS")
    print("-" * 30)
    
    inventory_data = {
        "ACT": {"current_stock": 50, "daily_usage": 8},
        "ORS": {"current_stock": 200, "daily_usage": 15},
        "Penicillin": {"current_stock": 20, "daily_usage": 5},
        "Zinc": {"current_stock": 100, "daily_usage": 3},
        "Insulin": {"current_stock": 5, "daily_usage": 2}
    }
    
    inventory_analysis = optimizer.analyze_inventory(inventory_data)
    
    print(f"Overall Status: {inventory_analysis['overall_status']}")
    print(f"Critical Alerts: {inventory_analysis['critical_alerts']}")
    print(f"Warning Alerts: {inventory_analysis['warning_alerts']}")
    
    print(f"\nStockout Risks:")
    for drug, analysis in inventory_analysis['drug_analyses'].items():
        if analysis['alert_level'] in ['critical', 'warning']:
            status_icon = "🚨" if analysis['alert_level'] == "critical" else "⚠️"
            print(f"  {status_icon} {drug}: {analysis['days_remaining']} days remaining")
    
    # Generate comprehensive report
    staffing_analysis = optimizer.recommend_staffing(150, {"nurses": 2, "doctors": 1, "pharmacists": 1})
    report = optimizer.generate_resource_report(staffing_analysis, inventory_analysis)
    
    print(f"\n📄 COMPREHENSIVE REPORT:")
    print(report)
    
    return optimizer


if __name__ == "__main__":
    optimizer = test_resource_optimizer()
