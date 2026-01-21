import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.components import render_kpi_card
from src.data_quality import check_sensor_health
from src.utils import load_config

# Load Config
config = load_config()

def get_system_health_metrics(df):
    """
    Calculates high-level health metrics.
    """
    total_points = len(df)
    broken_points = len(df[df['machine_status'] == 'BROKEN'])
    recovering_points = len(df[df['machine_status'] == 'RECOVERING'])
    
    # Calculate uptime (Normal / Total)
    uptime_pct = ((total_points - broken_points - recovering_points) / total_points) * 100
    
    return {
        'uptime_pct': uptime_pct,
        'total_failures': broken_points, 
        'recovery_events': recovering_points
    }

def calculate_reliability_metrics(events_df, total_duration_hours):
    """
    Calculates MTBF (Mean Time Between Failures) and MTTR (Mean Time To Repair).
    """
    if events_df.empty:
        return {'MTBF': float('inf'), 'MTTR': 0}
        
    # Filter for Failure events
    failures = events_df[events_df['status'].isin(['BROKEN', 'RECOVERING'])]
    num_failures = len(failures)
    
    if num_failures == 0:
         return {'MTBF': float('inf'), 'MTTR': 0}
         
    total_downtime_hours = failures['duration_mins'].sum() / 60
    total_uptime_hours = total_duration_hours - total_downtime_hours
    
    # Avoid division by zero
    mtbf = total_uptime_hours / num_failures if num_failures > 0 else 0
    mttr = (total_downtime_hours / num_failures) * 60 # In minutes usually
    
    return {
        'MTBF': mtbf, # Hours
        'MTTR': mttr  # Minutes
    }

def get_anomaly_events(df, threshold=2.0):
    """
    Identifies specific windows of time where the system was in a 'critical' state.
    """
    events = []
    
    if df.empty:
        return pd.DataFrame()
        
    temp_df = df.copy()
    temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'])
    
    # detecting state changes
    temp_df['status_change'] = temp_df['machine_status'].shift() != temp_df['machine_status']
    state_groups = temp_df.groupby(temp_df['status_change'].cumsum())
    
    for _, group in state_groups:
        status = group['machine_status'].iloc[0]
        if status in ['BROKEN', 'RECOVERING']:
            events.append({
                'start_time': group['timestamp'].min(),
                'end_time': group['timestamp'].max(),
                'duration_mins': (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 60,
                'status': status,
                'max_anomaly_score': group['anomaly_score'].max() if 'anomaly_score' in group.columns else 0
            })
            
    return pd.DataFrame(events).sort_values('start_time', ascending=False)

def analyze_root_cause(df, event_row, top_n=3):
    """
    Identifies which sensors contributed most to the anomaly during the event window.
    """
    if df.empty:
        return []
        
    # 1. Define Baseline (Normal Operation)
    baseline_df = df[df['machine_status'] == 'NORMAL']
    if baseline_df.empty:
        return []
        
    # 2. Define Event Window
    event_start = event_row['start_time']
    event_end = event_row['end_time']
    
    event_window_df = df[(df['timestamp'] >= event_start) & (df['timestamp'] <= event_end)]
    if event_window_df.empty:
        return []
        
    sensor_cols = [c for c in df.columns if 'sensor' in c]
    contributions = []
    
    for sensor in sensor_cols:
        try:
            # We compare the Mean shift using Z-Score logic
            mu_baseline = baseline_df[sensor].mean()
            sigma_baseline = baseline_df[sensor].std()
            
            if sigma_baseline == 0:
                continue
                
            mu_event = event_window_df[sensor].mean()
            
            # How many standard deviations did it shift?
            deviation_score = abs(mu_event - mu_baseline) / sigma_baseline
            
            contributions.append({
                'sensor': sensor,
                'deviation_score': deviation_score,
                'event_mean': mu_event,
                'baseline_mean': mu_baseline
            })
        except:
            continue
            
    # Sort by highest deviation
    results_df = pd.DataFrame(contributions).sort_values('deviation_score', ascending=False)
    return results_df.head(top_n)

def calculate_financial_risk(events_df, cost_per_minute):
    """
    Estimates financial impact based on downtime duration.
    """
    if events_df.empty:
        return 0
    
    # We only care about BROKEN/RECOVERING time
    total_downtime_minutes = events_df['duration_mins'].sum()
    return total_downtime_minutes * cost_per_minute

def plot_health_timeline(df):
    """
    Plots the anomaly score over time with background colors for machine status.
    """
    if 'anomaly_score' not in df.columns:
        return None
        
    fig = go.Figure()
    
    # Plot Anomaly Score
    fig.add_trace(go.Scatter(
        x=df['timestamp'], 
        y=df['anomaly_score'],
        mode='lines',
        name='System Anomaly Score',
        line=dict(color=config['ui']['theme_color'], width=1.5),
        opacity=0.8
    ))
    
    # Highlight Broken areas
    broken_df = df[df['machine_status'] == 'BROKEN']
    if not broken_df.empty:
        fig.add_trace(go.Scatter(
            x=broken_df['timestamp'],
            y=broken_df['anomaly_score'],
            mode='markers',
            name='Failure Event',
            marker=dict(color='#E74C3C', size=10, symbol='x')
        ))
        
    fig.update_layout(
        title="System Health & Anomaly Timeline",
        xaxis_title="Timeline",
        yaxis_title="Anomaly Score (Deviation)",
        height=config['ui']['chart_height'],
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def render_anomaly_insights(df):
    st.markdown("## 🧠 Anomaly Insights & Root Cause Analysis")
    
    if df.empty:
        st.warning("No data available for analysis.")
        return

    # --- Section 1: Financial Impact & Config ---
    default_cost = config['business']['cost_per_minute']
    
    with st.expander("⚙️  Configuration & Business Logic", expanded=False):
        cost_per_min = st.slider("Estimated Cost of Downtime ($ per minute)", 100, 5000, default_cost, step=100)
    
    events_df = get_anomaly_events(df, threshold=config['etl']['anomaly_threshold_std'])
    
    # Reliability Metrics Calculation
    total_duration_hours = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
    reliability = calculate_reliability_metrics(events_df, total_duration_hours)
    
    total_risk = calculate_financial_risk(events_df, cost_per_min)
    metrics = get_system_health_metrics(df)
    
    # Metrics Row 1: Status & Risk
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("System Integrity", f"{metrics['uptime_pct']:.2f}%")
        st.caption("Operational Uptime")
    with col2:
        render_kpi_card("MTBF", f"{reliability['MTBF']:.1f} hrs")
        st.caption("Mean Time Between Failures")
    with col3:
        render_kpi_card("MTTR", f"{reliability['MTTR']:.1f} mins")
        st.caption("Mean Time To Repair")
    with col4:
        render_kpi_card("Est. Financial Impact", f"${total_risk:,.0f}")
        st.caption(f"@ ${cost_per_min}/min penalty")

    st.markdown("---")

    # --- Section 2: Sensor Health Monitor ---
    st.markdown("### 🏥 Sensor Health Cluster")
    with st.expander("View Sensor Health Status", expanded=True):
        health_df = check_sensor_health(df)
        if not health_df.empty:
            critical_sensors = health_df[health_df['status'] == 'CRITICAL']
            if not critical_sensors.empty:
                st.error(f"⚠️ {len(critical_sensors)} Sensors in CRITICAL state (Flatline/Dead)")
                st.dataframe(critical_sensors, use_container_width=True)
            else:
                st.success("✅ All sensors operating within normal parameters.")
                
            warning_sensors = health_df[health_df['status'] == 'WARNING']
            if not warning_sensors.empty:
                st.warning(f"⚠️ {len(warning_sensors)} Sensors with Data Quality Warnings")
                st.dataframe(warning_sensors, use_container_width=True)

    st.markdown("---")

    # --- Section 3: Visual Timeline ---
    st.markdown("### 📉 System Health Timeline")
    fig = plot_health_timeline(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # --- Section 4: Smart Diagnostics (Drill Down) ---
    st.markdown("### 🕵️ Smart Diagnostics & Event Logs")
    
    col_list, col_details = st.columns([1, 1])
    
    with col_list:
        st.subheader("Detected Events")
        if not events_df.empty:
            # Create a selection list
            event_options = events_df.apply(
                lambda x: f"{x['start_time']} | {x['status']} ({x['duration_mins']:.0f} min)", axis=1
            )
            selected_event_idx = st.selectbox(
                "Select an Event to Analyze:", 
                options=event_options.index, 
                format_func=lambda i: event_options[i]
            )
            
            # Show list below
            display_df = events_df.copy()
            display_df['start_time'] = display_df['start_time'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(
                display_df[['start_time', 'status', 'duration_mins']],
                use_container_width=True,
                hide_index=True,
                height=200
            )
        else:
            st.success("No anomalies detected.")
            selected_event_idx = None

    with col_details:
        st.subheader("Root Cause Analysis")
        if selected_event_idx is not None:
            selected_row = events_df.loc[selected_event_idx]
            
            # Calculate financials for this specific event
            event_cost = selected_row['duration_mins'] * cost_per_min
            
            st.info(f"**Event Context**: {selected_row['status']} event lasting {selected_row['duration_mins']:.1f} minutes.")
            st.metric("Event Cost Impact", f"${event_cost:,.0f}")
            
            st.markdown("#### 🔍 Top Contributing Sensors")
            st.markdown("Analysis attempts to identify sensors that deviated most from their 'Normal' baseline during this event.")
            
            rca_results = analyze_root_cause(df, selected_row)
            
            if not rca_results.empty:
                for i, row in rca_results.iterrows():
                    st.markdown(f"**{i+1}. {row['sensor']}**")
                    st.progress(min(row['deviation_score'] / 10, 1.0), text=f"Deviation Score: {row['deviation_score']:.1f}σ")
            else:
                st.warning("Not enough data to isolate specific root causes.")
        else:
            st.markdown("*Select an event from the list to see automated diagnosis.*")
