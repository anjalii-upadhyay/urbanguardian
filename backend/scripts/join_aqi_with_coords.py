# scripts/join_aqi_with_coords.py

import pandas as pd
import requests
import os

def fetch_station_metadata():
    """
    Fetch station metadata with SSL verification disabled.
    """
    url = "https://app.cpcbccr.com/arcgis/rest/services/AQI_Stations/FeatureServer/0/query"
    params = {
        "where":     "STATE_NAME='KARNATAKA' AND CITY_NAME='BENGALURU'",
        "outFields": "STATION_NAME,Latitude,Longitude",
        "f":         "json"
    }
    # disable SSL verify to bypass expired cert
    resp = requests.get(url, params=params, timeout=10, verify=False)
    resp.raise_for_status()
    return pd.DataFrame([{
        "Station": feat["attributes"]["STATION_NAME"].strip(),
        "lat":      feat["attributes"]["Latitude"],
        "lon":      feat["attributes"]["Longitude"]
    } for feat in resp.json()["features"]])

def merge_aqi_with_coords():
    # compute static/data path from project root
    script_dir   = os.path.dirname(__file__)
    backend_dir  = os.path.dirname(script_dir)
    project_root = os.path.dirname(backend_dir)
    static_data  = os.path.join(project_root, "static", "data")

    avg_csv    = os.path.join(static_data, "station_annual_avg_all_stations.csv")
    output_csv = os.path.join(static_data, "station_aqi_for_map.csv")

    # 1) load AQI averages
    avg_df = pd.read_csv(avg_csv)
    avg_df["Station"] = avg_df["Station"].str.strip()

    # 2) fetch coords (with SSL verify disabled)
    meta_df = fetch_station_metadata()

    # 3) merge and write
    merged = pd.merge(meta_df, avg_df, on="Station", how="inner")
    merged.to_csv(output_csv, index=False)
    print(f"✅ Wrote {len(merged)} stations to {output_csv}")

if __name__ == "__main__":
    # suppress the InsecureRequestWarning
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    merge_aqi_with_coords()
