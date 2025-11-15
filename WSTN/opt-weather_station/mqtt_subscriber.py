import pickle

import paho.mqtt.client as mqtt
import requests

#Can leave this as 127.0.0.1 for now
#but you will need to change it come comp day
#(address TBD)
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
#Change this to match your team number
MQTT_TOPIC = "TEAM_XXX/weather_data"
#Change this to the address of your WWW box
POST_URL = "http://www.teamXXX.isucdc.com:8080/weather"
#Change this to the address of your NEWS box
API_URL = "http://news.teamXXX.isucdc.com:8080/weather"

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}")
    try:
        raw_bytes = pickle.loads(msg.payload)
        print(f"Raw bytes: {raw_bytes}")

        hex_str = raw_bytes.hex()
        print(f"Hex string: {hex_str}")

        payload = {"hex": hex_str}

        response = requests.post(POST_URL, data=payload)
        print(f"POST response: {response.status_code}")

        api_data = {
            "temp": raw_bytes[3],
            "humidity": raw_bytes[4],
            "windSpeed": raw_bytes[5]
        }
        response = requests.post(API_URL, json=api_data)
        print(f"API response: {response.status_code}")
    except Exception as e:
        print("Failed to process payload:", e)

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.loop_forever()