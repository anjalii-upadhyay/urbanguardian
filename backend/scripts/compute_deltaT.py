import csv
from collections import defaultdict

# 1. Input & output paths
IN_CSV  = "data/bengaluru_full_year.csv"
OUT_CSV = "../static/data/ward_avgTemp.csv"

# 2. Accumulators
sum_temp = defaultdict(float)
count    = defaultdict(int)
names    = {}

# 3. Read full-year CSV
with open(IN_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        w = r["ward_no"]
        names[w] = r["ward_name"]
        # daily mean temp
        tmax = float(r["temp_max"])
        tmin = float(r["temp_min"])
        avg  = (tmax + tmin) / 2
        sum_temp[w] += avg
        count[w]    += 1

# 4. Write ward-level average temperature
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ward_no", "ward_name", "avg_temp"])
    for w, total in sum_temp.items():
        avg_year = total / count[w]
        writer.writerow([w, names[w], f"{avg_year:.3f}"])

print(f"✅ Generated {OUT_CSV} with {len(sum_temp)} wards.")
