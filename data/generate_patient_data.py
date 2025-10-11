"""
MediLink PHC - Patient Visit Data Generator
Creates realistic historical data for forecasting model
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import random

def generate_patient_visits_data(days=90, start_date=None):
    """
    Generate realistic patient visit data for Nigerian PHC
    
    Patterns:
    - Monday-Friday: 80-120 patients (peak on Mondays)
    - Saturday: 50-70 patients  
    - Sunday: 30-50 patients
    - Monthly spikes (end of month)
    - Seasonal variations (malaria season)
    """
    
    # Ensure the generated series ends yesterday so forecasts start from tomorrow
    # Example: if days=90 and today=2025-10-10, last generated date will be 2025-10-09
    if start_date is None:
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=days - 1)
        # Cast to datetime at midnight for consistency
        start_date = datetime.combine(start_date, datetime.min.time())
    
    dates = []
    patient_counts = []
    
    current_date = start_date
    
    for i in range(days):
        # Base pattern by day of week
        weekday = current_date.weekday()  # 0=Monday, 6=Sunday
        
        if weekday == 0:  # Monday - highest volume
            base_count = random.randint(100, 130)
        elif weekday in [1, 2, 3, 4]:  # Tuesday-Friday
            base_count = random.randint(80, 120)
        elif weekday == 5:  # Saturday
            base_count = random.randint(50, 70)
        else:  # Sunday
            base_count = random.randint(30, 50)
        
        # Add monthly spike (end of month)
        if current_date.day >= 25:
            base_count = int(base_count * random.uniform(1.1, 1.3))
        
        # Add seasonal variation (malaria season: June-October)
        month = current_date.month
        if month in [6, 7, 8, 9, 10]:  # Rainy season
            base_count = int(base_count * random.uniform(1.2, 1.5))
        
        # Add random variation
        final_count = base_count + random.randint(-10, 15)
        final_count = max(20, final_count)  # Minimum 20 patients
        
        dates.append(current_date)
        patient_counts.append(final_count)
        
        current_date += timedelta(days=1)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'patient_count': patient_counts
    })
    
    return df

def add_outbreak_spikes(df, spike_days=3):
    """
    Add realistic outbreak spikes to the data
    """
    df_copy = df.copy()
    
    # Add 2-3 outbreak spikes
    for _ in range(spike_days):
        # Random day in the middle of dataset
        spike_idx = random.randint(20, len(df_copy) - 20)
        
        # Increase patient count by 2-3x
        original_count = df_copy.loc[spike_idx, 'patient_count']
        spike_count = int(original_count * random.uniform(2.0, 3.5))
        
        df_copy.loc[spike_idx, 'patient_count'] = spike_count
        
        # Also increase nearby days slightly
        for offset in [-1, 1]:
            if 0 <= spike_idx + offset < len(df_copy):
                nearby_count = df_copy.loc[spike_idx + offset, 'patient_count']
                df_copy.loc[spike_idx + offset, 'patient_count'] = int(nearby_count * 1.2)
    
    return df_copy

if __name__ == "__main__":
    print("🏥 Generating Patient Visit Data for MediLink PHC")
    print("=" * 60)
    
    # Generate 90 days of data
    df = generate_patient_visits_data(days=90)
    
    # Add outbreak spikes
    df_with_spikes = add_outbreak_spikes(df, spike_days=3)
    
    # Save to CSV inside data/ to align with loaders
    df_with_spikes.to_csv('data/patient_visits.csv', index=False)
    
    print(f"✅ Generated {len(df_with_spikes)} days of patient visit data")
    print(f"📊 Statistics:")
    print(f"   Average daily patients: {df_with_spikes['patient_count'].mean():.1f}")
    print(f"   Min patients: {df_with_spikes['patient_count'].min()}")
    print(f"   Max patients: {df_with_spikes['patient_count'].max()}")
    print(f"   Total patients: {df_with_spikes['patient_count'].sum():,}")
    
    print(f"\n📅 Date range: {df_with_spikes['date'].min().strftime('%Y-%m-%d')} to {df_with_spikes['date'].max().strftime('%Y-%m-%d')}")
    print(f"💾 Saved to: data/patient_visits.csv")
    
    # Show sample data
    print(f"\n📋 Sample data (first 10 days):")
    print(df_with_spikes.head(10).to_string(index=False))
