import streamlit as st
import pyexasol
import pandas as pd

st.set_page_config(page_title="Groundwater Intelligence Dashboard", layout="wide")

@st.cache_resource
def get_connection():
    return pyexasol.connect(
        dsn='localhost:8563', user='sys', password='exasol',
        schema='groundwater', websocket_sslopt={'cert_reqs': 0}
    )

conn = get_connection()

st.title("🌊 India Groundwater Intelligence Dashboard")
st.caption("Real-time anomaly detection and depletion forecasting powered by Exasol")

# --- Summary metrics ---
anomaly_summary = conn.export_to_pandas(
    "SELECT anomaly_type, COUNT(*) as cnt FROM groundwater.anomalies GROUP BY anomaly_type"
)
anomaly_summary.columns = [c.lower() for c in anomaly_summary.columns]

forecast_summary = conn.export_to_pandas(
    "SELECT risk_level, COUNT(*) as cnt FROM groundwater.forecasts GROUP BY risk_level"
)
forecast_summary.columns = [c.lower() for c in forecast_summary.columns]

col1, col2, col3, col4 = st.columns(4)
total_stations = conn.export_to_pandas("SELECT COUNT(*) as c FROM groundwater.stations").iloc[0, 0]
total_readings = conn.export_to_pandas("SELECT COUNT(*) as c FROM groundwater.readings").iloc[0, 0]
genuine = anomaly_summary[anomaly_summary['anomaly_type'] == 'genuine_depletion']['cnt'].sum()
faults = anomaly_summary[anomaly_summary['anomaly_type'] == 'sensor_fault']['cnt'].sum()

col1.metric("Monitored Stations", int(total_stations))
col2.metric("Total Readings", int(total_readings))
col3.metric("Genuine Depletion Alerts", int(genuine))
col4.metric("Sensor Faults Detected", int(faults))

st.divider()

# --- Risk forecast table ---
st.subheader("⚠️ Depletion Risk Forecast by Block")
forecast_df = conn.export_to_pandas("SELECT * FROM groundwater.forecasts ORDER BY forecast_date, block")
forecast_df.columns = [c.lower() for c in forecast_df.columns]

risk_color = {'critical': '🔴', 'high': '🟠', 'moderate': '🟡', 'low': '🟢'}
forecast_df['risk_level'] = forecast_df['risk_level'].apply(lambda x: f"{risk_color.get(x, '')} {x}")

st.dataframe(forecast_df, use_container_width=True)

st.divider()

# --- Anomaly breakdown chart ---
st.subheader("🔍 Anomaly Detection Breakdown")
c1, c2 = st.columns(2)
with c1:
    st.bar_chart(anomaly_summary.set_index('anomaly_type'))
with c2:
    st.bar_chart(forecast_summary.set_index('risk_level'))

st.divider()

# --- Station-level drill-down ---
st.subheader("📊 Station Water Level Trend")
stations_list = conn.export_to_pandas(
    "SELECT station_id, block, district, state_name FROM groundwater.stations ORDER BY station_id"
)
stations_list.columns = [c.lower() for c in stations_list.columns]

# Build a readable label like "DWLR0004 — Bilara, Jodhpur, Rajasthan"
stations_list['label'] = stations_list.apply(
    lambda r: f"{r['station_id']} — {r['block']}, {r['district']}, {r['state_name']}", axis=1
)

selected_label = st.selectbox(label="Select a station", options=stations_list['label'].tolist())
selected_station = selected_label.split(" — ")[0]  # extract just the station_id for the query below

if selected_station:
    trend = conn.export_to_pandas(
        f"SELECT reading_ts, water_level_m FROM groundwater.readings WHERE station_id = '{selected_station}' ORDER BY reading_ts"
    )
    trend.columns = [c.lower() for c in trend.columns]
    trend['reading_ts'] = pd.to_datetime(trend['reading_ts'])

    # Filter out impossible sensor-fault values for cleaner visualization
    trend_clean = trend[(trend['water_level_m'] >= 0) & (trend['water_level_m'] <= 100)]
    excluded = len(trend) - len(trend_clean)

    st.line_chart(trend_clean.set_index('reading_ts'))
    if excluded > 0:
        st.caption(f"⚠️ {excluded} readings excluded from chart as likely sensor faults (see Anomaly Detection above)")