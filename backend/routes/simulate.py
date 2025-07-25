from flask import Blueprint, request, jsonify

simulate_bp = Blueprint("simulate", __name__)

@simulate_bp.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json() or {}
    recommendation = data.get("recommendation","")
    # Hard-coded “impact zones” for demo:
    # pick 5 random lat/lon pairs + a “score” 0–1
    demo_points = [
        (12.95, 77.56, 0.2),
        (12.98, 77.58, 0.7),
        (12.92, 77.57, 0.4),
        (13.00, 77.55, 0.9),
        (12.94, 77.60, 0.1),
    ]
    # Build response: each point -> color
    out = []
    for lat, lon, score in demo_points:
        if score >= 0.8:
            color="green"
        elif score >= 0.4:
            color="orange"
        else:
            color="red"
        out.append({
            "lat": lat,
            "lon": lon,
            "score": score,
            "color": color
        })
    return jsonify({ "zones": out })
