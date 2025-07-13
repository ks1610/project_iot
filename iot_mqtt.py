"""
import paho.mqtt.client as mqtt
import adafruit_dht
import board
import RPi.GPIO as GPIO
import time
import threading
import json

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
#client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.V5)

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

                data = {
                    "temp": f"{temperature:.1f}",
                    "hum": f"{humidity:.1f}"
                }
                with open("static/data.json", "w") as f:
                    json.dump(data, f)
            #if temperature is not None and humidity is not None:
            #    client.publish("home/temperature", f"{temperature:.1f}")
            #    client.publish("home/humidity", f"{humidity:.1f}")
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
"""

import paho.mqtt.client as mqtt
import time
import threading
import json
import os

# Simulated GPIO pins
led_state = False
relay_state = False

# MQTT Setup
BROKER = "localhost"
client = mqtt.Client()

def on_message(client, userdata, msg):
    global led_state, relay_state
    payload = msg.payload.decode()
    if msg.topic == "home/led":
        led_state = (payload == "ON")
        print(f"Simulated LED is {'ON' if led_state else 'OFF'}")
    elif msg.topic == "home/relay":
        relay_state = (payload == "ON")
        print(f"Simulated Relay is {'ON' if relay_state else 'OFF'}")

client.on_message = on_message
client.connect(BROKER)
client.subscribe("home/#")
client.loop_start()

# Simulate DHT sensor values
def read_and_publish():
    while True:
        temp = 23.0
        hum = 55.0

        client.publish("home/temperature", f"{temp:.1f}")
        client.publish("home/humidity", f"{hum:.1f}")

        data = {
            "temp": f"{temp:.1f}",
            "hum": f"{hum:.1f}"
        }

        os.makedirs("static", exist_ok=True)
        with open("static/data.json", "w") as f:
            json.dump(data, f)

        print("Simulated data published.")
        time.sleep(5)

# Start background thread
t = threading.Thread(target=read_and_publish)
t.daemon = True
t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Simulated system stopped.")

