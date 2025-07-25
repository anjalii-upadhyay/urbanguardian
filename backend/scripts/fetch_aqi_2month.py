# scripts/fetch_aqi_2month.py

import csv
import time
import requests
from shapely.geometry import shape
import json
import os

# ───────── CONFIG ─────────

GEOJSON = "data\BBMP (1).geojson"   # ← your local file
START_DATE  = "2025-04-01"
END_DATE    = "2025-05-31"

ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude={lat}&longitude={lon}"
    "&hourly=pm2_5"
    f"&start_date={START_DATE}&end_date={END_DATE}"
    "&timezone=Asia%2FKolkata"
)

OUTPUT_CSV = "data/aqi_raw.csv"

# ───────── HELPERS ─────────

def load_wards(path):
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    return gj["features"]

def ward_centroid(feat):
    geom = feat["geometry"]
    c = shape(geom).centroid
    return c.y, c.x

# ───────── MAIN ─────────

def main():
    if not os.path.exists(GEOJSON):
        print(f"❌ GeoJSON not found at {GEOJSON}")
        return

    print("🔍 Loading wards…")
    wards = load_wards(GEOJSON)

    print(f"🗺️  Found {len(wards)} wards.\n")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["ward_no", "avg_pm2_5"])

        for feat in wards:
            props   = feat["properties"]
            ward_no = props.get("KGISWardNo") or props.get("ward_no") or ""
            lat, lon = ward_centroid(feat)
            url = ARCHIVE_URL.format(lat=lat, lon=lon)

            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                hourly = resp.json().get("hourly", {})
                pm_vals = hourly.get("pm2_5", [])

                if pm_vals:
                    avg_pm = sum(pm_vals) / len(pm_vals)
                    writer.writerow([ward_no, f"{avg_pm:.2f}"])
                    print(f"✅ Ward {ward_no} → avg_pm2_5 = {avg_pm:.2f}")
                else:
                    writer.writerow([ward_no, ""])
                    print(f"⚠️ Ward {ward_no}: no data")

            except Exception as e:
                writer.writerow([ward_no, ""])
                print(f"❌ Ward {ward_no} error:", e)

            time.sleep(1)  # rate-limit

    print(f"\n✅ AQI CSV written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
