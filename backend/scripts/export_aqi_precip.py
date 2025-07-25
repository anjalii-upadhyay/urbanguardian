# save as scripts/export_aqi_precip.py

import pandas as pd

# 1. Load your two‑month weather+population data
df = pd.read_csv("data/weather_data_with_population.csv")

# 2. Water‑stress proxy: average precipitation per ward
precip = (
    df
    .groupby("ward_no", as_index=False)["precipitation_sum"]
    .mean()
    .rename(columns={"precipitation_sum":"value"})
)
precip.to_csv("data/water_precip_2month.csv", index=False)
print("✅ Created data/water_precip_2month.csv")

# 3. AQI: load your raw AQI logs (ensure you have data/aqi_raw.csv with ward_no,aqi columns)
aqi_df = pd.read_csv("data/aqi_raw.csv")
aqi = (
    aqi_df
    .groupby("ward_no", as_index=False)["aqi"]
    .mean()
    .rename(columns={"aqi":"value"})
)
aqi.to_csv("data/aqi_2month.csv", index=False)
print("✅ Created data/aqi_2month.csv")
