# scripts/inspect_headers.py
import csv, os

INPUT_CSV = os.path.join("data","weather_data_with_population.csv")

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)        # default comma separator
    print("HEADERS:", reader.fieldnames)
    exit()
