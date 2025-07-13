from flask import Flask, render_template, request, jsonify
import paho.mqtt.publish as publish
import json
import os

app = Flask(__name__)

MQTT_BROKER = "localhost"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/control", methods=["POST"])
def control():
    device = request.form.get("device")
    state = request.form.get("state")
    if device and state:
        publish.single(f"home/{device}", state, hostname=MQTT_BROKER)
        return "OK", 200
    return "Missing data", 400

@app.route("/data")
def data():
    try:
        with open("static/data.json") as f:
            sensor_data = json.load(f)
        return jsonify(sensor_data)
    except Exception as e:
        return jsonify({"temp": "--", "hum": "--"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
