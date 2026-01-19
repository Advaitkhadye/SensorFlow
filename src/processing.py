import pandas as pd

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names to lowercase with underscores."""
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    return df

def get_sensor_columns(df: pd.DataFrame) -> list:
    """Identifies columns that look like sensors (e.g., 'sensor_00')."""
    return [c for c in df.columns if 'sensor' in c]

def calculate_correlations(df: pd.DataFrame, sensor_cols: list) -> pd.DataFrame:
    """Calculates the correlation matrix for sensor columns."""
    if not sensor_cols:
        return pd.DataFrame()
    return df[sensor_cols].corr()
