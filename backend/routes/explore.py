# backend/routes/explore.py

from flask import Blueprint, request, jsonify
import requests

explore_bp = Blueprint("explore", __name__)

# Free weather & air-quality endpoints (no API key required)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL        = "https://air-quality-api.open-meteo.com/v1/air-quality"

@explore_bp.route("/api/explore")
def get_environment_data():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    # 1) Current weather from Open-Meteo
    meteo = requests.get(OPEN_METEO_URL, params={
        "latitude":        float(lat),
        "longitude":       float(lon),
        "current_weather": True
    }).json()

    # 2) Hourly PM2.5 (µg/m³) from Open-Meteo Air-Quality API
    aqi_resp = requests.get(AQI_URL, params={
        "latitude":  lat,
        "longitude": lon,
        "hourly":    "pm2_5"
    }).json()
    pm25 = None
    try:
        pm25_list = aqi_resp["hourly"]["pm2_5"]
        pm25      = pm25_list[-1] if pm25_list else None
    except KeyError:
        pm25 = None

    # 3) Return consolidated JSON
    return jsonify({
        "temperature": meteo.get("current_weather", {}).get("temperature"),
        #"humidity":    meteo.get("current_weather", {}).get("humidity"),
        "wind":        meteo.get("current_weather", {}).get("windspeed"),
        "aqi":         pm25
    })
