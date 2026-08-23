IMPORT INTO groundwater.stations
FROM LOCAL CSV FILE 'C:\Users\LENOVO\PycharmProjects\VIT hackathon project\data\stations.csv'
ROW SEPARATOR = 'CRLF'
COLUMN SEPARATOR = ','
SKIP = 1;

IMPORT INTO groundwater.readings
FROM LOCAL CSV FILE 'C:\Users\LENOVO\PycharmProjects\VIT hackathon project\data\readings.csv'
ROW SEPARATOR = 'CRLF'
COLUMN SEPARATOR = ','
SKIP = 1;

SELECT COUNT(*) FROM groundwater.stations;
SELECT COUNT(*) FROM groundwater.readings;

SELECT COUNT(*) FROM groundwater.stations;

DELETE FROM groundwater.readings;
DELETE FROM groundwater.stations;

SELECT COUNT(*) FROM groundwater.readings;
SELECT COUNT(*) FROM groundwater.stations;

SELECT COUNT(*) FROM groundwater.stations;
SELECT COUNT(*) FROM groundwater.readings;

DELETE FROM groundwater.readings;

DELETE FROM groundwater.stations;

SELECT COUNT(*) FROM groundwater.stations;
SELECT COUNT(*) FROM groundwater.readings;

SELECT COUNT(*) FROM groundwater.stations;

SELECT COUNT(*) FROM groundwater.stations;

SELECT COUNT(*) FROM groundwater.readings;

CREATE OR REPLACE VIEW groundwater.readings_flagged AS
SELECT
    station_id,
    reading_ts,
    water_level_m,
    AVG(water_level_m) OVER (
        PARTITION BY station_id ORDER BY reading_ts
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg,
    STDDEV(water_level_m) OVER (
        PARTITION BY station_id ORDER BY reading_ts
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_std,
    water_level_m - LAG(water_level_m) OVER (
        PARTITION BY station_id ORDER BY reading_ts
    ) AS delta_from_prev
FROM groundwater.readings;

INSERT INTO groundwater.anomalies SELECT station_id, reading_ts, CASE WHEN ABS(delta_from_prev) > 5 THEN 'sensor_fault' WHEN rolling_std < 0.01 THEN 'sensor_fault' WHEN rolling_avg - water_level_m > 0.3 THEN 'genuine_depletion' ELSE 'normal' END AS anomaly_type, ABS(delta_from_prev) AS score FROM groundwater.readings_flagged WHERE ABS(delta_from_prev) > 5 OR rolling_std < 0.01 OR rolling_avg - water_level_m > 0.3;

SELECT COUNT(*) FROM groundwater.anomalies;
SELECT anomaly_type, COUNT(*) FROM groundwater.anomalies GROUP BY anomaly_type;

DELETE FROM groundwater.anomalies;

SELECT COUNT(*) FROM groundwater.anomalies;

SELECT COUNT(*) FROM groundwater.anomalies;

SELECT COUNT(*) FROM groundwater.forecasts;

SELECT 1;

SELECT COUNT(*) FROM groundwater.anomalies;

SELECT anomaly_type, COUNT(*) FROM groundwater.anomalies GROUP BY anomaly_type;

SELECT * FROM groundwater.anomalies WHERE anomaly_type = 'sensor_fault' LIMIT 20;

SELECT COUNT(*) FROM groundwater.readings;

SELECT risk_level, COUNT(*) FROM groundwater.forecasts GROUP BY risk_level;

SELECT * FROM groundwater.anomalies WHERE station_id = 'DWLR0001' ORDER BY reading_ts;

SELECT DISTINCT block, district, state_name FROM groundwater.stations LIMIT 20;

SELECT station_id, COUNT(*) as cnt 
FROM groundwater.stations 
GROUP BY station_id 
HAVING COUNT(*) > 1 
ORDER BY cnt DESC 
LIMIT 20;

SELECT COUNT(*) FROM groundwater.stations;

CREATE TABLE groundwater.stations_clean AS
SELECT DISTINCT * FROM groundwater.stations;

DROP TABLE groundwater.stations;

ALTER TABLE groundwater.stations_clean RENAME TO groundwater.stations;

RENAME TABLE groundwater.stations_clean TO groundwater.stations;

SELECT COUNT(*) FROM groundwater.stations;

SELECT station_id, COUNT(*) FROM groundwater.stations GROUP BY station_id HAVING COUNT(*) > 1;

SELECT DISTINCT block, district, state_name FROM groundwater.stations LIMIT 20;

SELECT DISTINCT block, district, state_name FROM groundwater.stations ORDER BY block;
