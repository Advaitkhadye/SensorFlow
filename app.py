import streamlit as st
import pandas as pd
import os
import plotly.express as px
from src.data_loader import load_data, get_basic_stats
from src.processing import clean_column_names, get_sensor_columns, calculate_correlations
from src.components import render_kpi_card, plot_sensor_correlation, plot_timeline
from src.styles import get_custom_css

# Page Configuration
st.set_page_config(
    page_title="SensorFlow: Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Styles
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("SensorFlow: Anomaly Detection")
    st.markdown("---")
    
    st.subheader("Dataset Info")
    st.info(
        "This project analyzes the `sensor.csv` dataset to predict machine failures."
    )
    # Download option for the dataset
    st.link_button("View dataset on Kaggle", "https://www.kaggle.com/datasets/nphantawee/pump-sensor-data")
    if os.path.exists("sensor.csv"):
        with open("sensor.csv", "rb") as file:
            st.download_button(
                label="Dataset Used (sensor.csv)",
                data=file,
                file_name="sensor.csv",
                mime="text/csv"
            )
    
    DATA_PATH = 'sensor.csv'
    DATA_FILE = DATA_PATH if os.path.exists(DATA_PATH) else None

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "**SensorFlow** is an advanced EDA & Anomaly Detection dashboard. "
        "It uses Principal Component Analysis (PCA) to analyze historical sensor data "
        "and identifies potential failure modes."
    )


# Main Data Loading
@st.cache_data
def load_processed_data(path):
    if os.path.exists(path):
        return pd.read_parquet(path)
    return pd.DataFrame()

# Try loading processed data first
PROCESSED_DATA_PATH = 'processed_data.parquet'
df_processed = load_processed_data(PROCESSED_DATA_PATH)

if not df_processed.empty:
    df = df_processed # Use the processed data with PCA columns
elif DATA_FILE:
    df = load_data(DATA_FILE)
    if not df.empty:
        # Preprocessing on the fly (legacy mode)
        df = clean_column_names(df)
else:
    df = pd.DataFrame()

if not df.empty:
    sensor_cols = get_sensor_columns(df)
    
    # Header Section
    st.markdown("## System Status")
    
    stats = get_basic_stats(df)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
            render_kpi_card("Total Datapoints", f"{stats.get('total_rows', 0):,}")
    with col2:
            render_kpi_card("Active Sensors", len(sensor_cols))
    with col3:
            latest_time = df['timestamp'].max() if 'timestamp' in df.columns else "N/A"
            render_kpi_card("Last Update", str(latest_time))
    with col4:
            if 'machine_status' in df.columns:
                status_counts = df['machine_status'].value_counts()
                top_status = status_counts.idxmax()
                render_kpi_card("Dominant Status", top_status)

    st.markdown("---")

    # Tabs Navigation
    tab_overview, tab_deepdive, tab_anomalies, tab_ai = st.tabs(["Overview", "Deep Dive", "Anomaly Detection", "AI Health Space"])

    # Tab 1: Overview
    with tab_overview:
        st.subheader("Sensor Time Series")
        selected_sensor = st.selectbox("Select Sensor to View", sensor_cols)
        fig_timeline = plot_timeline(df, selected_sensor, status_col='machine_status')
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)

    # Tab 2: Deep Dive (Correlation)
    with tab_deepdive:
        st.subheader("Sensor Correlations")
        if len(sensor_cols) > 10:
            selected_sensors_corr = st.multiselect("Select Sensors for Matrix", sensor_cols, default=sensor_cols[:10])
        else:
            selected_sensors_corr = sensor_cols
            
        if selected_sensors_corr:
            corr_matrix = calculate_correlations(df, selected_sensors_corr)
            fig_corr = plot_sensor_correlation(corr_matrix)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)

    # Tab 3: Anomalies
    with tab_anomalies:
        st.subheader("Significant Events Detection")
        target_sensor = st.selectbox("Select Sensor for Analysis", sensor_cols, key='anomaly_sensor')
        threshold = st.slider("Std Dev Threshold", 1.0, 5.0, 2.5)
        
        if target_sensor:
            series = df[target_sensor]
            mean = series.mean()
            std = series.std()
            anomalies = df[abs(series - mean) > (threshold * std)]
            
            st.info(f"Detected {len(anomalies)} anomalies based on {threshold}σ threshold.")
            if not anomalies.empty:
                st.dataframe(anomalies[['timestamp', target_sensor, 'machine_status']].sort_values('timestamp', ascending=False), use_container_width=True)

    # Tab 4: AI Health Space
    with tab_ai:
        st.subheader("Principal Component Analysis (PCA) Projection")
        st.markdown(
            "This view reduces the 50+ dimensions of sensor data into 2 distinct 'Health Components'. "
            "It allows you to visualize the **Machine State** in a simplified 2D space."
        )
        
        if 'PCA_1' in df.columns and 'PCA_2' in df.columns:
            # We sub-sample for performance updates
            chart_df = df.sample(n=min(5000, len(df)), random_state=42)
            
            fig_pca = px.scatter(
                chart_df, 
                x='PCA_1', 
                y='PCA_2', 
                color='machine_status',
                title="Machine Health Cluster Map (PCA)",
                hover_data=['timestamp'],
                color_discrete_map={'NORMAL': 'green', 'BROKEN': 'red', 'RECOVERING': 'orange'}
            )
            st.plotly_chart(fig_pca, use_container_width=True)
            
            st.markdown("### Anomaly Score Trend")
            st.line_chart(chart_df.set_index('timestamp')['anomaly_score'])
        else:
            st.warning("PCA data not found. Please run `etl_pipeline.py` to generate AI features.")

else:
    st.warning("Data could not be loaded. Please ensure `sensor.csv` exists or upload a file.")
