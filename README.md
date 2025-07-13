# project_iot

Tạo folder project 
mkdir project

1. Install môi trường ảo
$sudo apt update 
$sudo apt install python3-venv

2. Tạo môi trường ảo
$cd project 
$python3 -m venv venv

3. Active môi trường ảo
$source venv/bin/activate

4. Tải thư viện 
sudo apt install mosquitto mosquitto-clients python3-pip
$pip install --upgrade pip
$pip3 install flask paho-mqtt Adafruit_DHT RPi.GPI
$pip install adafruit-circuitpython-dht
$pip install adafruit-blinka

5. Tạo Sensor data file 
$mkdir static
$echo '{"temp": "--", "hum": "--"}' > static/data.json

6. Tạo Python MQTT client

tạo file iot_mqtt.py

import paho.mqtt.client as mqtt
import adafruit_dht
import board
import RPi.GPIO as GPIO
import time
import threading

# GPIO Pins
LED_PIN = 17
RELAY_PIN = 27

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# DHT11 setup
dht_device = adafruit_dht.DHT11(board.D4)  # GPIO4

# MQTT Setup
BROKER = "localhost"
client = mqtt.Client()

# Control handler
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if msg.topic == "home/led":
        GPIO.output(LED_PIN, payload == "ON")
    elif msg.topic == "home/relay":
        GPIO.output(RELAY_PIN, payload == "ON")

client.on_message = on_message
client.connect(BROKER)
client.subscribe("home/#")
client.loop_start()

# DHT read and publish
def read_and_publish():
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            if temperature is not None and humidity is not None:
                client.publish("home/temperature", f"{temperature:.1f}")
                client.publish("home/humidity", f"{humidity:.1f}")
            else:
                print("Sensor read returned None")
        except RuntimeError as e:
            print(f"DHT error: {e}")
        time.sleep(5)

# Run reading thread
t = threading.Thread(target=read_and_publish)
t.daemon = True
t.start()

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    client.disconnect()

7. Flask web app

tạo file web_app.py 

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


8. Tạo giao diện web
$mkdir templates
$cd templates
tạo file index.html

<!DOCTYPE html>
<html>
<head>
    <title>IoT Control Panel</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 20px; }
        h2 { color: #007BFF; }
        .status { font-size: 1.5em; }
        button { margin: 5px; padding: 10px 20px; font-size: 1em; }
    </style>
</head>
<body>
    <h2>DHT11 Sensor Readings</h2>
    <p>Temp: <span id = "temp">--</span>C</p>
    <p>Humi: <span id = "hum">--</spam>%</p>
      
    <h2>Controls</h2>

    <button onclick="setState('led', 'ON')">LED ON</button>
    <button onclick="setState('led', 'OFF')">LED OFF</button>
    <br><br>
    <button onclick="setState('relay', 'ON')">Relay ON</button>
    <button onclick="setState('relay', 'OFF')">Relay OFF</button>

    <script>
        function updateData() {
            fetch("/data")
                .then(res => res.json())
                .then(data => {
                    document.getElementById("temp").innerText = data.temp;
                    document.getElementById("hum").innerText = data.hum;
                });
        }
        setInterval(updateData, 3000);
        function setState(device, state) {
            fetch("/control", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `device=${device}&state=${state}`
            });
        }
    </script>
</body>
</html>

9. Run

#terminal 1:
$cd project
$source venv/bin/activate
$python3 iot_mqtt.py

#terminal 2:
$cd project
$source venv/bin/activate
$python3 web_app.py
nhập địa chỉ URL của web trên browser: http://<raspberrypi_ip>:5000


