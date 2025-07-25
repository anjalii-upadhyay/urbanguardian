# backend/scripts/make_yearly_csv.py

import json
import requests
import csv
from shapely.geometry import shape
from datetime import datetime

# ───────── CONFIG ─────────

# 1. GeoJSON local path (download once, place in backend/data/)
GEOJSON = "data/bangalore_wards.geojson"   

# 2. Output CSV path
OUTPUT = "data/bengaluru_full_year.csv"

# 3. Date range for full year
START_DATE = "2024-01-01"
END_DATE   = "2024-12-31"

# 4. Archive API template
API_URL = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude={lat}&longitude={lon}"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_max"
    "&timezone=Asia%2FKolkata"
    f"&start_date={START_DATE}&end_date={END_DATE}"
)

# ───────── SCRIPT ─────────

def load_wards(path):
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    return gj["features"]

def ward_centroid(feat):
    poly = shape(feat["geometry"])
    c = poly.centroid
    return c.y, c.x

def fetch_daily(lat, lon):
    url = API_URL.format(lat=lat, lon=lon)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("daily", {})
    return (
        data.get("time", []),
        data.get("temperature_2m_max", []),
        data.get("temperature_2m_min", []),
        data.get("precipitation_sum", []),
        data.get("relative_humidity_2m_max", [])
    )

def main():
    wards = load_wards(GEOJSON)
    fieldnames = [
        "ward_no", "ward_name", "date",
        "latitude","longitude",
        "temp_max","temp_min",
        "precip_sum","humidity_max"
    ]

    with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for feat in wards:
            props = feat["properties"]
            ward_no   = props.get("KGISWardNo") or props.get("ward_no") or ""
            ward_name = props.get("KGISWardName") or props.get("ward_name") or ""
            lat, lon  = ward_centroid(feat)

            try:
                dates, tmax, tmin, prec, hum = fetch_daily(lat, lon)
            except Exception as e:
                print(f"❌ Ward {ward_no}: fetch failed → {e}")
                continue

            if not dates:
                print(f"⚠️ Ward {ward_no}: no data returned")
                continue

            for i, d in enumerate(dates):
                row = {
                    "ward_no": ward_no,
                    "ward_name": ward_name,
                    "date": d,
                    "latitude": lat,
                    "longitude": lon,
                    "temp_max": tmax[i],
                    "temp_min": tmin[i],
                    "precip_sum": prec[i],
                    "humidity_max": hum[i],
                }
                writer.writerow(row)

            print(f"✅ Wrote {len(dates)} days for Ward {ward_no}")

    print(f"\n✅ Full‑year CSV saved to {OUTPUT}")

if __name__ == "__main__":
    main()
