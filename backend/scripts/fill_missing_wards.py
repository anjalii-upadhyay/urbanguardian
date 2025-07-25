#!/usr/bin/env python3
# backend/scripts/build_full_yearly.py

import csv
import json
import requests
import time
from shapely.geometry import shape

# ───────── CONFIG ─────────

GEOJSON      = "data/BBMP (1).geojson"
OUTPUT_CSV   = "data/bengaluru_full_year.csv"
START_DATE   = "2024-01-01"
END_DATE     = "2024-12-31"
TIMEZONE     = "Asia%2FKolkata"
DELAY_SEC    = 1.0

API_URL_TPL  = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude={lat}&longitude={lon}"
    "&daily=temperature_2m_max,temperature_2m_min,"
    "precipitation_sum,relative_humidity_2m_max"
    f"&timezone={TIMEZONE}"
    f"&start_date={START_DATE}&end_date={END_DATE}"
)

FIELDNAMES = [
    "ward_no","ward_name","date",
    "latitude","longitude",
    "temp_max","temp_min",
    "precip_sum","humidity_max"
]


# ───────── HELPERS ─────────

def load_wards(path):
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    feats = gj.get("features", [])
    out = []
    for feat in feats:
        props = feat.get("properties", {})
        ward_no   = str(props.get("KGISWardNo") or props.get("ward_no") or "").strip()
        ward_name = props.get("KGISWardName") or props.get("ward_name") or ""
        geom      = feat.get("geometry")
        if ward_no and geom:
            out.append((ward_no, ward_name, geom))
    return out

def ward_centroid(geom):
    poly = shape(geom)
    c = poly.centroid
    return c.y, c.x

def fetch_daily(lat, lon):
    url  = API_URL_TPL.format(lat=lat, lon=lon)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    d = resp.json().get("daily", {})
    return (
        d.get("time", []),
        d.get("temperature_2m_max", []),
        d.get("temperature_2m_min", []),
        d.get("precipitation_sum", []),
        d.get("relative_humidity_2m_max", [])
    )


# ───────── MAIN ─────────

def main():
    wards = load_wards(GEOJSON)
    print(f"🗺️  Loaded {len(wards)} wards from GeoJSON.")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=FIELDNAMES)
        writer.writeheader()

        for ward_no, ward_name, geom in wards:
            lat, lon = ward_centroid(geom)
            time.sleep(DELAY_SEC)

            try:
                dates, tmax, tmin, prec, hum = fetch_daily(lat, lon)
            except Exception as e:
                print(f"❌ Ward {ward_no} fetch failed: {e}")
                continue

            if not dates:
                print(f"⚠️  Ward {ward_no} returned no data, skipping.")
                continue

            for i, dt in enumerate(dates):
                writer.writerow({
                    "ward_no":     ward_no,
                    "ward_name":   ward_name,
                    "date":        dt,
                    "latitude":    lat,
                    "longitude":   lon,
                    "temp_max":    tmax[i],
                    "temp_min":    tmin[i],
                    "precip_sum":  prec[i],
                    "humidity_max":hum[i],
                })
            print(f"✅ Wrote {len(dates)} days for Ward {ward_no}")

    print(f"\n🎉 Full‑year CSV built at: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
