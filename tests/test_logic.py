import pytest
import pandas as pd
import numpy as np
from src.anomaly_insights import calculate_reliability_metrics, analyze_root_cause
from src.data_quality import check_sensor_health

def test_reliability_metrics():
    # Mock dataframe with 1 "broken" event of 60 mins
    data = {
        'status': ['BROKEN'],
        'duration_mins': [60]
    }
    events_df = pd.DataFrame(data)
    
    total_hours = 10 # 10 hours total
    
    metrics = calculate_reliability_metrics(events_df, total_hours)
    
    # Downtime = 1 hr
    # Uptime = 9 hrs
    # Failures = 1
    # MTBF = 9 / 1 = 9.0
    # MTTR = 60 / 1 = 60.0
    
    assert metrics['MTBF'] == 9.0
    assert metrics['MTTR'] == 60.0

def test_analyze_root_cause_empty():
    # Should handle empty input gracefully
    df = pd.DataFrame()
    row = {}
    result = analyze_root_cause(df, row)
    assert result == []

def test_sensor_health_flatline():
    # Create a flatline sensor
    df = pd.DataFrame({
        'sensor_00': [10, 10, 10, 10, 10], # Flatline
        'sensor_01': [1, 2, 3, 4, 5]       # Normal
    })
    
    health_df = check_sensor_health(df, lookback_window=5)
    
    assert not health_df.empty
    
    # Check sensor_00
    s00 = health_df[health_df['sensor'] == 'sensor_00'].iloc[0]
    assert s00['status'] == 'CRITICAL'
    assert 'Zero Variance' in s00['details']
    
    # Check sensor_01
    s01 = health_df[health_df['sensor'] == 'sensor_01'].iloc[0]
    assert s01['status'] == 'HEALTHY'
