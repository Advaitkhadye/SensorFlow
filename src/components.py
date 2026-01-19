import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_kpi_card(title, value, delta=None):
    """
    Renders a styled KPI Metric card using HTML.
    """
    delta_html = ""
    if delta:
        color = "green" if "+" in str(delta) or float(str(delta).strip('%')) > 0 else "red"
        delta_html = f'<div class="delta" style="color: {color}">{delta}</div>'
        
    html_code = f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <h2>{value}</h2>
        {delta_html}
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

def plot_sensor_correlation(corr_matrix, height=600):
    """
    Plots the correlation heatmap using Plotly.
    """
    if corr_matrix.empty:
        st.warning("No correlation data available.")
        return None
        
    fig = px.imshow(
        corr_matrix, 
        text_auto=False,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Sensor Correlation Matrix"
    )
    fig.update_layout(height=height)
    return fig

def plot_timeline(df, sensor_col, status_col=None):
    """
    Plots a sensor's value over time, optionally colored by machine status.
    """
    if df.empty or sensor_col not in df.columns:
        return None
        
    fig = px.line(
        df, 
        x='timestamp', 
        y=sensor_col, 
        title=f"{sensor_col} Timeline",
        color=status_col if status_col in df.columns else None
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Sensor Value")
    return fig
