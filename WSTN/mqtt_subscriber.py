import os
import pickle
import io


import paho.mqtt.client as mqtt
import requests

#Can leave this as 127.0.0.1 for now
#but you will need to change it come comp day
#(address TBD)
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

#Change this to match your team number
MQTT_TOPIC = "TEAM_2/weather_data"
#Change this to the address of your WWW box
POST_URL = os.getenv("POST_URL", "http://localhost:8000/post")
#Change this to the address of your NEWS box
API_URL = os.getenv("API_URL", "http://localhost:8001/api")

# LoRa 5-layer PSK values and packet expectations (mirrors transmitter)
TEAM_NUMBER = 0x28  # sample packets use 0x28 as the team byte
PSK1 = b"SkibidiLoRa_NoCapFR_ISEAGE_Sigma"
PSK2 = b"Team0x28NoMid_Bussin_C3_2025_420"
PSK3 = b"Gyatt_WeatherStation_OnGod_PSK3_"
PSK4 = b"RizzEncrypt_Layer4_Fanum_Tax_Yeet"
PSK5 = b"IonlyFW_Ligma_PSK5_Vibes_Lowkey_L"
PAYLOAD_LEN = 12  # bytes 3-14 (encrypted section)
PACKET_LEN = 17

# Track last valid sequence to reject replays
last_sequence_seen = -1

SAFE_BUILTINS = {
    "builtins": {"bytes", "bytearray", "str", "tuple", "list", "dict", "int", "float"}
}

class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in SAFE_BUILTINS and name in SAFE_BUILTINS[module]:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Deserialization attempt rejected: {module}.{name}")

def safe_loads(s):
    return SafeUnpickler(io.BytesIO(s)).load()


def _compute_tags(encrypted: bytes, seq: int) -> tuple[int, int]:
    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    tag0 = TEAM_NUMBER ^ seq_high ^ seq_low
    tag1 = 0
    for i, byte in enumerate(encrypted):
        tag0 ^= byte
        tag1 ^= PSK1[i % 32] ^ PSK2[i % 32] ^ PSK3[i % 32] ^ PSK4[i % 32] ^ PSK5[i % 32]
    return tag0 & 0xFF, tag1 & 0xFF


def decrypt_packet(packet_bytes: bytes) -> tuple[int, bytes]:
    if len(packet_bytes) < PACKET_LEN:
        raise ValueError(f"Packet too short: {len(packet_bytes)} bytes")
    if packet_bytes[0] != TEAM_NUMBER:
        raise ValueError(f"Unexpected team number: {packet_bytes[0]:#x}")

    seq = (packet_bytes[1] << 8) | packet_bytes[2]
    encrypted = packet_bytes[3:15]
    tag_expected = packet_bytes[15], packet_bytes[16]
    tag_calc = _compute_tags(encrypted, seq)
    if tag_calc != tag_expected:
        raise ValueError("Integrity tag mismatch; rejecting packet")

    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    plaintext = bytearray(PAYLOAD_LEN)
    for i in range(PAYLOAD_LEN):
        ks1 = PSK1[i % 32] ^ seq_high ^ PSK1[(i + 1) % 32]
        ks2 = PSK2[i % 32] ^ seq_low ^ PSK2[(i + 3) % 32]
        ks3 = PSK3[i % 32] ^ seq_high ^ PSK3[(i + 5) % 32]
        ks4 = PSK4[i % 32] ^ seq_low ^ PSK4[(i + 7) % 32]
        ks5 = PSK5[i % 32] ^ seq_high ^ PSK5[(i + 11) % 32]
        plaintext[i] = encrypted[i] ^ ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5

    return seq, bytes(plaintext)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}")
    try:
        raw_bytes = safe_loads(msg.payload)
        packet = bytes(raw_bytes)
        print(f"Raw bytes: {packet.hex()}")

        seq, plaintext = decrypt_packet(packet)

        global last_sequence_seen
        if seq <= last_sequence_seen:
            raise ValueError(f"Replay detected (seq {seq} <= {last_sequence_seen})")
        last_sequence_seen = seq

        hex_str = plaintext.hex()
        print(f"Decrypted payload (seq {seq}): {hex_str}")

        payload = {"hex": hex_str, "seq": seq}
        print(f"Payload to send: {payload}")
        # Optionally forward to endpoints when running live via MQTT
        if client is not None:
            response = requests.post(POST_URL, data=payload)
            print(f"POST response: {response.status_code}")

            api_data = {
                "temp": plaintext[2],
                "humidity": plaintext[3],
                "windSpeed": plaintext[4],
                "airQuality": plaintext[5],
            }
            response = requests.post(API_URL, json=api_data)
            print(f"API response: {response.status_code}")
    except Exception as e:
        print("Failed to process payload:", e)

client = mqtt.Client()
messages = {1: "2800011c651144356d4c3c584f15406f57", 2: "2800021c654c363c715c0c1e6b51120257", 3: "2800031c656e693365673c4d6b0c7a0857", 4: "010001", 5: "2800011c656d4b261b149f2a9ba54d9157"}

if __name__ == "__main__":
    # Decrypt the three sample packets using the existing on_message logic
    class DummyMsg:
        def __init__(self, topic: str, payload: bytes):
            self.topic = topic
            self.payload = payload

    for seq_num, hex_pkt in messages.items():
        print("\n--- Decrypting sample seq", seq_num, "---")
        pickled_payload = pickle.dumps(bytes.fromhex(hex_pkt))
        on_message(None, None, DummyMsg(MQTT_TOPIC, pickled_payload))

    # Uncomment to run as MQTT subscriber instead of offline samples
    # client.on_message = on_message
    # client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # client.subscribe(MQTT_TOPIC)
    # client.loop_forever()