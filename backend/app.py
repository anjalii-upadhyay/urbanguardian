# from flask import Flask, send_from_directory, jsonify, render_template
# from routes.explore import explore_bp
# from routes.simulate import simulate_bp

# app = Flask(__name__, template_folder='../templates', static_folder='../static')

# # Register blueprint if using modular routes
# app.register_blueprint(explore_bp)
# app.register_blueprint(simulate_bp)

# @app.route("/")
# def home():
#     return render_template("explore.html")
# @app.route("/wards")
# def serve_wards():
#     return send_from_directory("data", "bangalore_wards.geojson")

# @app.route("/impact")
# def impact():
#     # serve the Impact Simulator page
#     return render_template("impact.html")

# if __name__ == "__main__":
#     app.run(debug=True)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__, 
            template_folder="../templates", 
            static_folder="../static")

# AQI endpoint (OpenAQ)
@app.route("/api/aqi")
def aqi():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400

    # Call OpenAQ latest measurements near given coords
    resp = requests.get(
        "https://api.openaq.org/v2/latest",
        params={
            "coordinates": f"{lat},{lon}",
            "radius": 10000,  # 10km
            "limit": 1
        },
        timeout=5
    )
    if resp.status_code != 200:
        return jsonify({"error": "OpenAQ error"}), resp.status_code

    data = resp.json()
    if data.get("results"):
        meas = data["results"][0]["measurements"][0]
        return jsonify({
            "parameter": meas["parameter"],
            "value": meas["value"],
            "unit": meas["unit"]
        })

    return jsonify({"error": "No data"}), 404


# Serve the map page
@app.route("/")
def home():
    return render_template("explore.html")


# Run
if __name__ == "__main__":
    # Use 0.0.0.0 if you want to expose externally
    app.run(host="127.0.0.1", port=5000, debug=True)
