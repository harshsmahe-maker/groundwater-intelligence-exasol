import csv
import random
from datetime import datetime, timedelta

random.seed(42)

states_districts_blocks = [
    ("Maharashtra", "Pune", "Haveli"),
    ("Maharashtra", "Nashik", "Niphad"),
    ("Karnataka", "Bengaluru Rural", "Devanahalli"),
    ("Karnataka", "Kolar", "Malur"),
    ("Tamil Nadu", "Coimbatore", "Mettupalayam"),
    ("Tamil Nadu", "Madurai", "Melur"),
    ("Rajasthan", "Jaipur", "Sanganer"),
    ("Rajasthan", "Jodhpur", "Bilara"),
    ("Punjab", "Ludhiana", "Samrala"),
    ("Punjab", "Patiala", "Rajpura"),
    ("Gujarat", "Ahmedabad", "Daskroi"),
    ("Gujarat", "Mehsana", "Kadi"),
    ("Uttar Pradesh", "Meerut", "Sardhana"),
    ("Uttar Pradesh", "Agra", "Fatehabad"),
    ("Andhra Pradesh", "Anantapur", "Kalyandurg"),
    ("Andhra Pradesh", "Kurnool", "Adoni"),
    ("Madhya Pradesh", "Indore", "Depalpur"),
    ("Madhya Pradesh", "Ujjain", "Ghatiya"),
    ("Haryana", "Hisar", "Hansi"),
    ("Haryana", "Karnal", "Nilokheri"),
]

stations = []
sid = 1
for state, district, block in states_districts_blocks:
    for i in range(5):
        station_id = f"DWLR{sid:04d}"
        lat = round(random.uniform(8.0, 32.0), 6)
        lon = round(random.uniform(70.0, 88.0), 6)
        stations.append([station_id, block, district, state, lat, lon])
        sid += 1

with open('stations.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'block', 'district', 'state_name', 'latitude', 'longitude'])
    w.writerows(stations)

readings = []
start_date = datetime(2024, 6, 1)
num_days = 545

for idx, s in enumerate(stations):
    station_id = s[0]
    base_level = round(random.uniform(5.0, 25.0), 2)
    trend_type = random.choices(['stable', 'genuine_depletion', 'sensor_fault'], weights=[0.55, 0.30, 0.15])[0]
    depletion_rate = random.uniform(0.015, 0.05) if trend_type == 'genuine_depletion' else random.uniform(-0.005, 0.005)
    fault_day = random.randint(100, num_days - 50) if trend_type == 'sensor_fault' else None

    level = base_level
    for d in range(num_days):
        date = start_date + timedelta(days=d)
        month = date.month
        seasonal = -0.02 if month in [6,7,8,9] else 0.01
        noise = random.uniform(-0.05, 0.05)
        level = max(0.5, level + depletion_rate + seasonal + noise)
        rainfall = round(random.uniform(0, 40), 1) if month in [6,7,8,9] else round(random.uniform(0, 5), 1)
        recorded_level = level

        if trend_type == 'sensor_fault' and fault_day and d >= fault_day:
            if d < fault_day + 20:
                recorded_level = level + 999
            else:
                recorded_level = round(base_level, 2)

        if d % 3 == 0:
            readings.append([station_id, date.strftime('%Y-%m-%d %H:%M:%S'), round(recorded_level, 2), rainfall])

with open('readings.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'reading_ts', 'water_level_m', 'rainfall_mm'])
    w.writerows(readings)

print(f"stations: {len(stations)} rows")
print(f"readings: {len(readings)} rows")