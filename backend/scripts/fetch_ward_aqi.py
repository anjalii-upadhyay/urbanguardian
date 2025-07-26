# scripts/fetch_cpcb_stations.py
import requests, pandas as pd

url = "https://airquality.cpcbccr.com/arcgis/rest/services/AQI_Stations/FeatureServer/0/query"
params = {
    "where":     "STATE_NAME='KARNATAKA' AND CITY_NAME='BENGALURU'",
    "outFields": "STATION_NAME,Latitude,Longitude",
    "f":         "json"
}
resp = requests.get(url, params=params)
resp.raise_for_status()
feats = resp.json()["features"]

# build metadata DataFrame
meta = pd.DataFrame([{
    "Station": a["attributes"]["STATION_NAME"],
    "lat":      a["attributes"]["Latitude"],
    "lon":      a["attributes"]["Longitude"]
} for a in feats])

meta.to_csv("backend/static/data/station_metadata.csv", index=False)
print("Wrote station_metadata.csv")
