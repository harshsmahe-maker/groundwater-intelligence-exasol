import pyexasol
import pandas as pd
import numpy as np
from datetime import timedelta

# Connect to Exasol
conn = pyexasol.connect(dsn='localhost:8563', user='sys', password='exasol', schema='groundwater', websocket_sslopt={'cert_reqs': 0})

# Pull readings joined with station block info
query = """
SELECT r.station_id, s.block, s.district, s.state_name, r.reading_ts, r.water_level_m
FROM groundwater.readings r
JOIN groundwater.stations s ON r.station_id = s.station_id
ORDER BY s.block, r.reading_ts
"""
df = conn.export_to_pandas(query)
df.columns = [c.lower() for c in df.columns]
df['reading_ts'] = pd.to_datetime(df['reading_ts'])

# Critical threshold: depth to water level considered "over-exploited" risk
CRITICAL_THRESHOLD_M = 25.0

results = []

# Group by block, average across all stations in that block per date
for block, block_df in df.groupby('block'):
    daily = block_df.groupby('reading_ts')['water_level_m'].mean().reset_index()
    daily = daily.sort_values('reading_ts')

    if len(daily) < 10:
        continue

    # Simple linear trend (slope) over the available history
    daily['days'] = (daily['reading_ts'] - daily['reading_ts'].min()).dt.days
    x = daily['days'].values
    y = daily['water_level_m'].values
    slope, intercept = np.polyfit(x, y, 1)

    last_day = x.max()
    last_level = y[-1]
    district = block_df['district'].iloc[0]
    state = block_df['state_name'].iloc[0]

    # Forecast next 90 days in 30-day steps
    for horizon_days in [30, 60, 90]:
        future_day = last_day + horizon_days
        predicted_level = slope * future_day + intercept
        forecast_date = daily['reading_ts'].max() + timedelta(days=horizon_days)

        if predicted_level >= CRITICAL_THRESHOLD_M:
            risk = 'critical'
        elif predicted_level >= CRITICAL_THRESHOLD_M * 0.85:
            risk = 'high'
        elif predicted_level >= CRITICAL_THRESHOLD_M * 0.7:
            risk = 'moderate'
        else:
            risk = 'low'

        results.append({
            'block': block,
            'forecast_date': forecast_date.date(),
            'risk_level': risk,
            'predicted_level_m': round(float(predicted_level), 2)
        })

forecast_df = pd.DataFrame(results)
print(forecast_df.head(20))
print(f"\nTotal forecast rows: {len(forecast_df)}")

# Clear old forecasts and write new ones
conn.execute("DELETE FROM groundwater.forecasts")
conn.import_from_pandas(forecast_df, 'forecasts')

print("Forecasts written to Exasol successfully.")
conn.close()