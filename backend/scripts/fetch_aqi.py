# backend/scripts/make_ward_aqi.py

import json, csv, time, requests
from shapely.geometry import shape

# ─── Config ───
GEOJSON_IN = "data/BBMP.geojson"        # your wards file
CSV_OUT    = "../static/data/ward_aqi.csv"  # where to save
OWM_URL    = "https://api.openweathermap.org/data/2.5/air_pollution"
OWM_KEY    = "123f39e4276ae8f8750e0dc1bf345d83"

# ─── Helpers ───
def load_wards(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["features"]

def centroid(feat):
    poly = shape(feat["geometry"])
    c    = poly.centroid
    return c.y, c.x

# ─── Main ───
def main():
    wards = load_wards(GEOJSON_IN)
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=["ward_no","aqi"])
        writer.writeheader()

        for feat in wards:
            wn = feat["properties"].get("KGISWardNo") or feat["properties"].get("ward_no")
            lat, lon = centroid(feat)

            # Call OWM Air Pollution
            resp = requests.get(OWM_URL, params={
                "lat": lat, "lon": lon,
                "appid": OWM_KEY
            })
            if resp.status_code != 200:
                print(f"❌ Ward {wn}: API error {resp.status_code}")
                continue

            data = resp.json().get("list", [])
            if not data:
                print(f"⚠️ Ward {wn}: no data")
                continue

            aqi_val = data[0]["main"]["aqi"]  # 1–5 scale
            writer.writerow({"ward_no": str(wn), "aqi": aqi_val})
            print(f"✅ Ward {wn}: AQI {aqi_val}")

            time.sleep(1)  # courteous pause

    print(f"✅ CSV saved: {CSV_OUT}")

if __name__ == "__main__":
    main()
