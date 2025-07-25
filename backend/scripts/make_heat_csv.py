# backend/scripts/make_heat_csv.py

import csv, os, statistics
from datetime import datetime

# ─── Paths ──────────────────────────────────────────────
INPUT_CSV  = os.path.join("data", "weather_data_with_population.csv")
OUTPUT_CSV = os.path.join("data", "heat_anomaly.csv")

# ─── 1) Read & group data ─────────────────────────────────
ward_data = {}  
# ward_no → {
#   "ward_name": str,
#   "lat": float, "lon": float,            # sample coords (from latest row)
#   "records": [ (date_obj, avg_temp) ... ]
# }

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        wid   = r["ward_no"]
        wname = r["ward_name"]
        # parse date (adjust format if needed)
        date_obj = datetime.fromisoformat(r["date"])
        tmax = float(r["temperature_max"])
        tmin = float(r["temperature_min"])
        avg  = (tmax + tmin) / 2

        if wid not in ward_data:
            ward_data[wid] = {
                "ward_name": wname,
                "records": [],
                "sample_lat": float(r["latitude"]),
                "sample_lon": float(r["longitude"])
            }
        ward_data[wid]["records"].append((date_obj, avg))

# ─── 2) Compute baseline & anomaly ────────────────────────
results = []
for wid, info in ward_data.items():
    recs = info["records"]
    # 2a) sort by date
    recs.sort(key=lambda x: x[0])
    # 2b) current_avg = avg_temp on the latest date
    latest_date, current_avg = recs[-1]
    # 2c) baseline = mean of all avg_temps
    baseline = statistics.mean([v for _, v in recs])
    anomaly  = current_avg - baseline

    results.append({
        "ward_no":       wid,
        "ward_name":     info["ward_name"],
        "date":          latest_date.date().isoformat(),
        "latitude":      round(info["sample_lat"], 6),
        "longitude":     round(info["sample_lon"], 6),
        "current_avg":   round(current_avg, 2),
        "baseline_temp": round(baseline,    2),
        "anomaly":       round(anomaly,     2),
    })

# ─── 3) Write out the updated CSV ─────────────────────────
fieldnames = [
    "ward_no", "ward_name", "date", "latitude", "longitude",
    "current_avg", "baseline_temp", "anomaly"
]
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Generated {OUTPUT_CSV} with {len(results)} wards")
