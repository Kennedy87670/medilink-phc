"""
MediLink PHC - Patient Volume Forecasting Model
Uses Facebook Prophet for time-series forecasting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PatientVolumeForecaster:
    """
    Patient volume forecasting using Facebook Prophet
    """
    
    def __init__(self):
        self.model = None
        self.trained = False
        
    def load_data(self, csv_path='data/patient_visits.csv'):
        """
        Load patient visit data and prepare for Prophet
        """
        print("📊 Loading patient visit data...")
        
        # Load data
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        
        # Prophet requires 'ds' and 'y' columns
        prophet_df = df.rename(columns={'date': 'ds', 'patient_count': 'y'})
        
        print(f"✅ Loaded {len(prophet_df)} days of data")
        print(f"   Date range: {prophet_df['ds'].min().strftime('%Y-%m-%d')} to {prophet_df['ds'].max().strftime('%Y-%m-%d')}")
        print(f"   Average daily patients: {prophet_df['y'].mean():.1f}")
        
        return prophet_df
    
    def train_model(self, df, test_split=0.2):
        """
        Train Prophet model and evaluate performance
        """
        print("\n🤖 Training Prophet forecasting model...")
        
        # Split data for evaluation
        split_idx = int(len(df) * (1 - test_split))
        train_df = df[:split_idx].copy()
        test_df = df[split_idx:].copy()
        
        print(f"   Training on {len(train_df)} days")
        print(f"   Testing on {len(test_df)} days")
        
        # Initialize Prophet with optimized parameters for healthcare data
        self.model = Prophet(
            yearly_seasonality=False,     # Disable yearly (not enough data)
            weekly_seasonality=True,      # Capture weekly patterns
            daily_seasonality=False,      # Not needed for daily data
            seasonality_mode='additive',  # Better for healthcare data
            changepoint_prior_scale=0.1,  # Less sensitive to trend changes
            seasonality_prior_scale=1.0,  # Reduce seasonality strength
            holidays_prior_scale=1.0,     # Reduce holiday effects
            interval_width=0.8,           # 80% confidence intervals
            changepoint_range=0.8         # Limit changepoint detection
        )
        
        # Add Nigerian holidays (affect patient volume)
        holidays_df = self._create_nigerian_holidays()
        self.model.add_country_holidays(country_name='Nigeria')
        
        # Train the model
        self.model.fit(train_df)
        self.trained = True
        
        print("✅ Model trained successfully!")
        
        # Evaluate on test set
        evaluation_results = self._evaluate_model(train_df, test_df)
        
        return evaluation_results
    
    def _create_nigerian_holidays(self):
        """
        Create Nigerian holidays that affect patient volume
        """
        holidays = []
        
        # Major Nigerian holidays (approximate dates)
        holiday_dates = [
            ('2025-01-01', 'New Year'),
            ('2025-04-18', 'Good Friday'),
            ('2025-04-21', 'Easter Monday'),
            ('2025-05-01', 'Workers Day'),
            ('2025-05-29', 'Democracy Day'),
            ('2025-06-12', 'Democracy Day'),
            ('2025-10-01', 'Independence Day'),
            ('2025-12-25', 'Christmas Day'),
            ('2025-12-26', 'Boxing Day')
        ]
        
        for date_str, name in holiday_dates:
            holidays.append({
                'holiday': name,
                'ds': pd.to_datetime(date_str),
                'lower_window': -1,  # Day before
                'upper_window': 1,   # Day after
            })
        
        return pd.DataFrame(holidays)
    
    def _evaluate_model(self, train_df, test_df):
        """
        Evaluate model performance using MAPE
        """
        print("\n📈 Evaluating model performance...")
        
        # Make predictions on test set
        future = self.model.make_future_dataframe(periods=len(test_df))
        forecast = self.model.predict(future)
        
        # Get predictions for test period
        test_predictions = forecast['yhat'][-len(test_df):].values
        test_actual = test_df['y'].values
        
        # Calculate MAPE
        mape = np.mean(np.abs((test_actual - test_predictions) / test_actual)) * 100
        
        print(f"   MAPE (Mean Absolute Percentage Error): {mape:.1f}%")
        
        if mape < 20:
            print("   ✅ Excellent forecast accuracy!")
        elif mape < 30:
            print("   ✅ Good forecast accuracy")
        else:
            print("   ⚠️  Forecast accuracy needs improvement")
        
        return {
            'mape': mape,
            'test_predictions': test_predictions,
            'test_actual': test_actual,
            'forecast': forecast
        }
    
    def generate_forecast(self, days_ahead=7):
        """
        Generate forecast for next N days
        """
        if not self.trained:
            raise ValueError("Model must be trained first!")
        
        print(f"\n🔮 Generating {days_ahead}-day forecast...")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=days_ahead)
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Get only future predictions
        future_forecast = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        
        # Round predictions
        future_forecast['yhat'] = future_forecast['yhat'].round().astype(int)
        future_forecast['yhat_lower'] = future_forecast['yhat_lower'].round().astype(int)
        future_forecast['yhat_upper'] = future_forecast['yhat_upper'].round().astype(int)
        
        print("✅ Forecast generated!")
        
        return future_forecast
    
    def visualize_forecast(self, historical_df, forecast_df, save_path='reports/patient_forecast.png'):
        """
        Create visualization of historical data and forecast
        """
        print(f"\n📊 Creating forecast visualization...")
        
        # Set up the plot
        plt.figure(figsize=(15, 8))
        
        # Plot historical data
        plt.plot(historical_df['ds'], historical_df['y'], 
                label='Historical Data', color='blue', linewidth=2)
        
        # Plot forecast
        plt.plot(forecast_df['ds'], forecast_df['yhat'], 
                label='Forecast', color='red', linewidth=2, linestyle='--')
        
        # Plot confidence intervals
        plt.fill_between(forecast_df['ds'], 
                        forecast_df['yhat_lower'], 
                        forecast_df['yhat_upper'],
                        alpha=0.3, color='red', label='Confidence Interval')
        
        # Formatting
        plt.title('MediLink PHC - Patient Volume Forecast', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Daily Patient Count', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        # Tight layout
        plt.tight_layout()
        
        # Save plot
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved to: {save_path}")
        
        # Don't show plot in headless environment
        # plt.show()
    
    def get_forecast_summary(self, forecast_df):
        """
        Generate summary statistics for forecast
        """
        summary = {
            'forecast_period': f"{forecast_df['ds'].min().strftime('%Y-%m-%d')} to {forecast_df['ds'].max().strftime('%Y-%m-%d')}",
            'total_predicted_patients': int(forecast_df['yhat'].sum()),
            'average_daily_patients': int(forecast_df['yhat'].mean()),
            'min_daily_patients': int(forecast_df['yhat'].min()),
            'max_daily_patients': int(forecast_df['yhat'].max()),
            'peak_day': forecast_df.loc[forecast_df['yhat'].idxmax(), 'ds'].strftime('%Y-%m-%d'),
            'lowest_day': forecast_df.loc[forecast_df['yhat'].idxmin(), 'ds'].strftime('%Y-%m-%d')
        }
        
        return summary


def main():
    """
    Main function to run the forecasting pipeline
    """
    print("🏥 MediLink PHC - Patient Volume Forecasting")
    print("=" * 60)
    
    # Initialize forecaster
    forecaster = PatientVolumeForecaster()
    
    # Load data
    df = forecaster.load_data()
    
    # Train model
    evaluation = forecaster.train_model(df, test_split=0.2)
    
    # Generate 7-day forecast
    forecast = forecaster.generate_forecast(days_ahead=7)
    
    # Create visualization
    forecaster.visualize_forecast(df, forecast)
    
    # Print forecast summary
    print("\n📋 FORECAST SUMMARY")
    print("=" * 40)
    summary = forecaster.get_forecast_summary(forecast)
    
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Show detailed forecast
    print(f"\n📅 DETAILED 7-DAY FORECAST")
    print("=" * 40)
    forecast_display = forecast.copy()
    forecast_display['ds'] = forecast_display['ds'].dt.strftime('%Y-%m-%d (%A)')
    forecast_display.columns = ['Date', 'Predicted Patients', 'Lower Bound', 'Upper Bound']
    print(forecast_display.to_string(index=False))
    
    # Save forecast to CSV
    forecast.to_csv('reports/patient_forecast.csv', index=False)
    print(f"\n💾 Forecast saved to: reports/patient_forecast.csv")
    
    return forecaster, forecast, evaluation


if __name__ == "__main__":
    forecaster, forecast, evaluation = main()
