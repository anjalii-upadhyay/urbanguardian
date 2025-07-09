from flask import Flask, send_from_directory, jsonify, render_template
from routes.explore import explore_bp

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Register blueprint if using modular routes
app.register_blueprint(explore_bp)

@app.route("/")
def home():
    return render_template("explore.html")
@app.route("/wards")
def serve_wards():
    return send_from_directory("data", "bangalore_wards.geojson")

if __name__ == "__main__":
    app.run(debug=True)
