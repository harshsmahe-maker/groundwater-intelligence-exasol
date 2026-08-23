# Groundwater Intelligence Platform (Exasol-Powered)

An AI-powered early-warning system that turns India's real-time groundwater sensor data into actionable intelligence — detecting faulty sensors, flagging genuine depletion trends, and forecasting which blocks are heading toward crisis, before wells run dry.

---

## Problem

India's groundwater is depleting at an alarming rate, and several blocks are already classified as "over-exploited" by the Central Ground Water Board (CGWB). Thousands of Digital Water Level Recorders (DWLRs) continuously capture real-time groundwater data through the India-WRIS platform — but this data remains purely reactive:

- There is no system that detects anomalies at scale or forecasts depletion before it becomes a crisis.
- Faulty sensor readings are not distinguished from genuine, crisis-level depletion trends, undermining trust in the data.
- District officials and farmers have no way to know, in advance, which regions are approaching critical groundwater depletion — decisions are only made after a crisis (dry borewells, water scarcity) has already occurred.

## Solution

This project is an AI-powered groundwater intelligence platform, built on **Exasol's high-performance analytics engine**, that:

1. **Ingests** historical and real-time DWLR sensor data across monitoring stations nationwide.
2. **Detects anomalies** — distinguishing faulty sensor readings (spikes, flatlines) from genuine, crisis-level depletion trends, using Exasol's massively parallel SQL window functions to analyze patterns across every station simultaneously.
3. **Forecasts depletion risk** — predicting which blocks/districts are likely to cross critical groundwater thresholds in the coming months, using historical trend and seasonal patterns.
4. **Delivers early warnings** through an accessible Streamlit dashboard, enabling district authorities and farmers to act before wells run dry, not after.

## Architecture

```
DWLR Sensor Data (CSV)
        │
        ▼
   Exasol Database  ◄── IMPORT (bulk-optimized ingestion)
        │
        ├── SQL window functions ──► Anomaly Detection (sensor_fault vs genuine_depletion)
        │
        ├── pyexasol ──► Python (trend/seasonal model) ──► Forecast Risk ──► written back to Exasol
        │
        ▼
  Streamlit Dashboard  ◄── live queries via pyexasol
```

## How Exasol Is Used

Exasol Personal (deployed locally via `exasol/docker-db` on Docker) is the **primary data platform** for this project, not a peripheral component:

- **Ingestion**: Station metadata and sensor readings are loaded using Exasol's native `IMPORT INTO ... FROM LOCAL CSV FILE` statement, Exasol's bulk-optimized loading path.
- **Anomaly detection**: Runs entirely as set-based SQL inside Exasol using window functions (`AVG() OVER`, `STDDEV() OVER`, `LAG() OVER` partitioned by station) — computing rolling averages, rolling standard deviation, and step-change detection across every station in parallel, in a single query. This is the "massively parallel processing" piece: no station-by-station looping in application code.
- **Forecasting**: Python (via `pyexasol`) pulls historical readings out of Exasol, fits a per-block trend model, and writes the resulting risk forecasts back into Exasol — so Exasol remains both the source of truth and the destination.
- **Serving**: The Streamlit dashboard queries Exasol directly and live on every page load — Exasol is the single backing store for the whole application, not a one-time export.

## Results (on the included sample dataset)

- **100 monitoring stations** across 10 Indian states, **18,200 readings** over an 18-month period
- **2,675 anomalies** flagged automatically:
  - **2,590** classified as sensor faults (spikes/flatlines)
  - **85** classified as genuine depletion trends
- **60 forecast records** (20 blocks × 3 time horizons: 30/60/90 days), each with a predicted water level and risk classification (critical / high / moderate / low)

## Repository Structure

```
/data        - sample CSV datasets (stations.csv, readings.csv) + generator script
/sql         - database schema and anomaly-detection SQL
/pipeline    - Python scripts: forecasting model (pulls/writes to Exasol)
/dashboard   - Streamlit dashboard app
README.md    - this file
```

## Setup & Run Guide

### 1. Prerequisites
- Docker Desktop
- Python 3.10+
- DBeaver (or any SQL client with an Exasol driver)

### 2. Start Exasol
```bash
docker run --name exasoldb -p 127.0.0.1:8563:8563 --detach --privileged --stop-timeout 120 exasol/docker-db:latest
docker logs -f exasoldb   # wait for "All stages finished"
```

### 3. Create the schema
Connect with DBeaver (host `localhost`, port `8563`, user `sys`, password `exasol`; disable certificate validation for the self-signed dev cert), then run the schema script in `/sql`.

### 4. Load sample data
```sql
IMPORT INTO groundwater.stations
FROM LOCAL CSV FILE '<path-to>/data/stations.csv'
ROW SEPARATOR = 'CRLF' COLUMN SEPARATOR = ',' SKIP = 1;

IMPORT INTO groundwater.readings
FROM LOCAL CSV FILE '<path-to>/data/readings.csv'
ROW SEPARATOR = 'CRLF' COLUMN SEPARATOR = ',' SKIP = 1;
```

### 5. Run anomaly detection
Execute the view creation and `INSERT INTO groundwater.anomalies ...` statements in `/sql`.

### 6. Run the forecast
```bash
pip install pyexasol pandas numpy statsmodels streamlit
python pipeline/forecast.py
```

### 7. Launch the dashboard
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your browser.

## Demo Video

[Link to demo video — add here]

## Team / Submission

Submitted for [hackathon name] — [team name / members].
