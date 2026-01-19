import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads sensor data from a CSV file.
    Uses caching to improve performance on subsequent reloads.
    """
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()

    try:
        # Load the dataset
        # Optimizing types helps memory usage, but for now we load simply
        # parsing dates is crucial for time-series
        df = pd.read_csv(file_path)
        
        # Basic trimming if there are empty columns like 'Unnamed: 0'
        cols_to_drop = [c for c in df.columns if 'Unnamed' in c]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
            
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, errors='coerce')
        elif 'date' in df.columns:
             df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
             
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def get_basic_stats(df: pd.DataFrame):
    """
    Returns a dictionary of basic statistics for the dashboard header.
    """
    stats = {}
    if df.empty:
        return stats
        
    stats['total_rows'] = len(df)
    stats['cols'] = len(df.columns)
    return stats
