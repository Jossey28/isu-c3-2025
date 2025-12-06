# NOTICE this code is purely for testing. The mqtt publisher, what this script
# is doing, is out of scope for teams, this code will be running outside of your
# teams infrastructure. This is provided to test your mqtt subscriber script, which
# is in scope for teams/teams are responsible for.

# | OUT OF SCOPE FOR TEAMS                          | IN SCOPE FOR TEAMS
# | LoRa Tx (mostly), Rx, publishing data to the mqtt topic |  Receiving that data via the mqtt subscriber
import pickle
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
BASE_TOPIC = "TEAM_{}/weather_data"

# List of RAW_HEX strings to test
TEST_PACKETS = [
    "02 00 01 59 4D 35 68 53 42 41 2F 71 5C 0C 42 54 3C",
    "02 00 02 2A 45 3A 17 53 42 41 2F 71 5C 0C 42 54 3C",
    "02 00 03 2A 5D 25 0A 53 42 41 2F 71 5C 0C 42 54 3C",
    "02 00 04 48 5D 2F 6E 53 42 41 2F 71 5C 0C 42 54 3C",
    "02 00 05 54 46 3D 2D 53 42 41 2F 71 5C 0C 42 54 3C"
]

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        # Loop through the list of packets endlessly
        while True:
            for i, raw_hex in enumerate(TEST_PACKETS):
                print(f"\n--- Sending Packet {i+1}/5 ---")
                print(f"Using raw hex string: {raw_hex}")

                # Convert hex string to bytes
                raw_bytes = bytes.fromhex(raw_hex.replace(" ", ""))
                print(f"Converted to bytes: {raw_bytes.hex()}")

                team_number = raw_bytes[0]
                print(f"Extracted team number: {team_number}")

                if 1 <= team_number <= 40:
                    topic = BASE_TOPIC.format(team_number)
                else:
                    topic = "UNKNOWN_TEAM/weather_data"
                    print(f"⚠️ Unknown team number {team_number}, using fallback topic")

                # Pickle the bytes (mimicking the competition infrastructure)
                payload = pickle.dumps(raw_bytes)
                print(f"Publishing {len(payload)} bytes to topic '{topic}'")

                client.publish(topic, payload)

                # Wait 5 seconds before sending the next one
                time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()