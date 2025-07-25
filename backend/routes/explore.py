import json, statistics, requests
from flask import Blueprint, jsonify

explore_bp = Blueprint("explore", __name__)

# Load ward polygons once
with open("data/bangalore_wards.geojson") as f:
    wards = json.load(f)["features"]

def polygon_centroid(coords):
    """Approximate centroid for a Polygon (first ring only)."""
    lats, lons = [], []
    for lon, lat in coords[0]:
        lons.append(lon)
        lats.append(lat)
    return sum(lats) / len(lats), sum(lons) / len(lons)

def fetch_temp(lat, lon):
    """Call Open‑Meteo for current temperature."""
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }, timeout=5)
    data = r.json().get("current_weather", {})
    return data.get("temperature")

@explore_bp.route("/api/heat_anomaly")
def heat_anomaly():
    # 1) Gather temperatures for each ward centroid
    ward_temps = []
    for feat in wards:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            lat, lon = polygon_centroid(geom["coordinates"])
        else:
            # simple fallback for MultiPolygon: first polygon
            lat, lon = polygon_centroid(geom["coordinates"][0])
        temp = fetch_temp(lat, lon) or 0
        ward_temps.append((feat["properties"]["WARD_NO"], temp))

    # 2) Compute citywide median
    temps_only = [t for _, t in ward_temps]
    median = statistics.median(temps_only) if temps_only else 0

    # 3) Build anomalies dict
    anomalies = {
        str(ward_id): round(temp - median, 2)
        for ward_id, temp in ward_temps
    }
    return jsonify(anomalies)

@explore_bp.route("/api/explore")
def realtime_data():
    """Existing route for temperature, wind, AQI popups."""
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "Missing coords"}), 400

    # Open-Meteo weather
    w = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }).json().get("current_weather", {})

    # OpenWeatherMap AQI (free tier)
    aqi = None
    try:
        aqi_resp = requests.get("https://api.openweathermap.org/data/2.5/air_pollution", params={
            "lat": lat, "lon": lon, "appid": "123f39e4276ae8f8750e0dc1bf345d83"
        }).json()
        aqi = aqi_resp["list"][0]["main"]["aqi"]
    except:
        pass

    return jsonify({
        "temperature": w.get("temperature"),
        "wind":        w.get("windspeed"),
        "aqi":         aqi
    })