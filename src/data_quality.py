import pandas as pd
import numpy as np

def check_sensor_health(df, lookback_window=500):
    """
    Analyzes sensor columns for data quality issues.
    
    Checks for:
    1. Zero Variance (Dead/Stuck Sensor)
    2. High Null Rate (though ETL handles this, good to monitor raw if we had it, strictly on current DF here)
    3. Flatline Detection (Recent check)
    
    Args:
        df: The dataframe containing sensor data.
        lookback_window: Number of recent rows to check for flatlining.
        
    Returns:
        pd.DataFrame: A report of sensor health status.
    """
    if df.empty:
        return pd.DataFrame()
        
    sensor_cols = [c for c in df.columns if 'sensor' in c]
    health_report = []
    
    # Check only the recent window for "current" status
    recent_df = df.tail(lookback_window) if len(df) > lookback_window else df
    
    for sensor in sensor_cols:
        status = "HEALTHY"
        details = "Normal operation"
        
        # 1. Check Variance (Stuck Sensor)
        if recent_df[sensor].std() == 0:
            status = "CRITICAL"
            details = "Flatline (Zero Variance)"
            
        # 2. Check for NaN saturation (if any slipped through or if we view raw)
        elif recent_df[sensor].isna().mean() > 0.1:
            status = "WARNING"
            details = "High Missing Data Rate"
            
        health_report.append({
            'sensor': sensor,
            'status': status,
            'details': details,
            'current_value': recent_df[sensor].iloc[-1]
        })
        
    return pd.DataFrame(health_report)

def get_data_quality_metrics(df):
    """
    Returns high-level data quality summary.
    """
    sensor_cols = [c for c in df.columns if 'sensor' in c]
    total_cells = len(df) * len(sensor_cols)
    missing_cells = df[sensor_cols].isna().sum().sum()
    
    quality_score = 100 * (1 - (missing_cells / total_cells)) if total_cells > 0 else 0
    
    return {
        'quality_score': quality_score,
        'total_sensors': len(sensor_cols),
        'rows': len(df)
    }
