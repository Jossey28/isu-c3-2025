#NOTICE this code is purely for testing. The mqtt publisher, what this script
#is doing, is out of scope for teams, this code will be running outside of your
#teams infrastructure. This is provided to test your mqtt subscriber script, which
#is in scope for teams/teams are responsible for. 

#| OUT OF SCOPE FOR TEAMS                                   | IN SCOPE FOR TEAMS 
#| LoRa Tx (mostly), Rx, publishing data to the mqtt topic  |  Receiving that data via the mqtt subscriber
import pickle
import time

import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
BASE_TOPIC = "TEAM_{}/weather_data"

# Hardcoded raw data string (hex format)
#NOTE: You will need to change the first byte i.e the first "28"
#to match your team number if you set your team number in the subscriber script.
#Remember this is hex so 28 in hex equals 40 in decimal thus this is for team 40
RAW_HEX = "28 01 02 3A 2F 10 52 75 4A 55 53 6F 64 41 6E 59 70"  # Example
#      |Team#|res  |t| h | w| a| flag                        |
# res=reserved bytes, t=temperature, h=humidity, w=wind speed, a=air quality

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            print(f"Using hardcoded raw hex string: {RAW_HEX}")

            raw_bytes = bytes.fromhex(RAW_HEX.replace(" ", ""))
            print(f"Converted to bytes: {raw_bytes}")

            team_number = raw_bytes[0]
            print(f"Extracted team number: {team_number}")

            if 1 <= team_number <= 40:
                topic = BASE_TOPIC.format(team_number)
            else:
                topic = "UNKNOWN_TEAM/weather_data"
                print(f"⚠️ Unknown team number {team_number}, using fallback topic")

            payload = pickle.dumps(raw_bytes)
            print(f"Publishing {len(payload)} bytes to topic '{topic}'")

            client.publish(topic, payload)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()