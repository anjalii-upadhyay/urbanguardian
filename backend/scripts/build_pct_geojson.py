import csv, json

# 1. load ward shapefile GeoJSON
wards = json.load(open("data/BBMP.geojson", encoding="utf-8"))

# 2. load anomalies CSV
rows = list(csv.DictReader(open("data/heat_anomaly.csv", encoding="utf-8")))
# parse raw anomalies
raws = []
for r in rows:
    raw = float(r["current_avg"]) - float(r["baseline_temp"])
    raws.append(raw)
minR, maxR = min(raws), max(raws)

# 3. build ward→pct lookup
lookup = {}
for r in rows:
    w = r["ward_no"]
    raw = float(r["current_avg"]) - float(r["baseline_temp"])
    pct = int(round((raw - minR) / (maxR - minR) * 100))
    lookup[w] = max(0, min(100, pct))

# 4. assign to GeoJSON features
for feat in wards["features"]:
    no = str(feat["properties"].get("KGISWardNo") or feat["properties"].get("ward_no"))
    feat["properties"]["anomaly_pct"] = lookup.get(no, 0)

# 5. save out
json.dump(wards, open("static/data/wards_with_pct.geojson", "w"), indent=2)
print("✅ wards_with_pct.geojson built with anomaly_pct property")
