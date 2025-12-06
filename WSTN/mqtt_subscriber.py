import os
from dotenv import load_dotenv
import pickle
import io
import logging
import sys
import paho.mqtt.client as mqtt
import requests
import urllib3

# --- 1. CONFIGURATION ---
load_dotenv()

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "TEAM_2/weather_data"

POST_URL = str(os.getenv("POST_URL"))
API_URL = str(os.getenv("API_URL"))

# --- 2. LOGGING SETUP (MAXIMUM VERBOSITY) ---
# Configure Python's standard logging to show everything (DEBUG level)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- 3. LORA / DECRYPTION CONFIG ---
TEAM_NUMBER = 0x2
PSK1 = b"SkibidiLoRa_NoCapFR_ISEAGE_Sigma"
PSK2 = b"Team0x28NoMid_Bussin_C3_2025_420"
PSK3 = b"Gyatt_WeatherStation_OnGod_PSK3_"
PSK4 = b"RizzEncrypt_Layer4_Fanum_Tax_Yeet"
PSK5 = b"IonlyFW_Ligma_PSK5_Vibes_Lowkey_L"

PAYLOAD_LEN = 14  # 14 bytes (4 sensor + 10 flag)
PACKET_LEN = 17   # 1 byte Team + 2 byte Seq + 14 byte Data
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

# --- 4. DECRYPTION LOGIC ---
def decrypt_packet(packet_bytes: bytes) -> tuple[int, bytes]:
    logger.debug(f"Starting decryption on {len(packet_bytes)} bytes")
    
    if len(packet_bytes) < PACKET_LEN:
        logger.error(f"Packet too short: {len(packet_bytes)} bytes")
        raise ValueError(f"Packet too short")
    
    if packet_bytes[0] != TEAM_NUMBER:
        logger.error(f"Team mismatch: Got {packet_bytes[0]:#x}, Expected {TEAM_NUMBER:#x}")
        raise ValueError(f"Unexpected team number")

    # Extract Sequence
    seq = (packet_bytes[1] << 8) | packet_bytes[2]
    logger.debug(f"Extracted Sequence Number: {seq}")

    # Extract Encrypted Payload
    encrypted = packet_bytes[3:17]
    logger.debug(f"Encrypted payload segment (hex): {encrypted.hex()}")

    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    plaintext = bytearray(PAYLOAD_LEN)

    for i in range(PAYLOAD_LEN):
        ks1 = PSK1[i % 32] ^ seq_high ^ PSK1[(i + 1) % 32]
        ks2 = PSK2[i % 32] ^ seq_low ^ PSK2[(i + 3) % 32]
        ks3 = PSK3[i % 32] ^ seq_high ^ PSK3[(i + 5) % 32]
        ks4 = PSK4[i % 32] ^ seq_low ^ PSK4[(i + 7) % 32]
        ks5 = PSK5[i % 32] ^ seq_high ^ PSK5[(i + 11) % 32]
        
        keystream_byte = ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5
        plaintext[i] = encrypted[i] ^ keystream_byte
        
        # Super verbose per-byte log (optional, can be noisy)
        # logger.debug(f"Byte {i}: Enc={encrypted[i]:02x} Key={keystream_byte:02x} Plain={plaintext[i]:02x}")

    return seq, bytes(plaintext)

# --- 5. MQTT CALLBACKS ---

def on_connect(client, userdata, flags, rc):
    """Called when the broker responds to our connection request."""
    if rc == 0:
        logger.info(f"Connected to MQTT Broker! (Result Code: {rc})")
        logger.info(f"Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        logger.error(f"Failed to connect. Result Code: {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    """Called when the broker confirms our subscription."""
    logger.info(f"Subscription Confirmed! (Message ID: {mid}, QoS: {granted_qos})")

def on_log(client, userdata, level, buf):
    """Catches internal Paho MQTT log messages."""
    # This prints protocol level stuff like PINGREQ, PINGRESP, SEND, RECV
    print(f"[PAHO-LOG] {buf}")

def on_message(client, userdata, msg):
    logger.info(f"MSG RECEIVED | Topic: {msg.topic} | Payload Size: {len(msg.payload)}")
    
    try:
        # Attempt pickle decode
        try:
            raw_bytes = safe_loads(msg.payload)
            packet = bytes(raw_bytes)
            logger.info(f"Unpickled Bytes: {packet.hex()}")
        except Exception as e:
            logger.error(f"Pickle error: {e}. Trying raw payload as bytes...")
            packet = msg.payload

        # Attempt Decrypt
        seq, plaintext = decrypt_packet(packet)

        # Replay Check
        global last_sequence_seen
        if seq <= last_sequence_seen:
             # Soft warning for testing loop
             if last_sequence_seen > 65000 and seq < 100:
                 logger.warning("Sequence rollover detected (Safe to ignore if testing)")
             else:
                 logger.warning(f"REPLAY DETECTED: Seq {seq} <= Last {last_sequence_seen}")
                 # raise ValueError("Replay detected") # Uncomment to enforce strictness
        
        last_sequence_seen = seq
        hex_str = plaintext.hex()

        # Parse Data
        flag_bytes = plaintext[4:]
        try:
            flag_str = flag_bytes.decode('utf-8')
        except:
            flag_str = "<binary_garbage>"

        logger.info(f"DECRYPTION SUCCESS | Seq: {seq}")
        logger.info(f" > Hex Payload: {hex_str}")
        logger.info(f" > Flag Found:  {flag_str}")
        
        # Prepare API Payloads
        go_payload = {"hex": packet.hex(), "seq": seq}
        java_payload = {"hex": packet.hex()}
        # api_data = {
        #     "temp": plaintext[0],
        #     "humidity": plaintext[1],
        #     "windSpeed": plaintext[2],
        #     "airQuality": plaintext[3],
        #     "flag": flag_str
        # }

        # Send to Backend
        if client is not None:
            logger.debug(f"Sending POST to {POST_URL}...")
            try:
                resp = requests.post(POST_URL, data=go_payload, timeout=2, verify=False, headers={"User-Agent": "WSTN-MQTT-Subscriber/1.0", "X-Api-Key-Flag": os.getenv("API_KEY_FLAG")})
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                logger.info(f"POST Response: {resp.status_code}")
            except Exception as e:
                logger.error(f"POST Failed: {e}")

            logger.debug(f"Sending API to {API_URL}...")
            try:
                resp = requests.post(API_URL, json=java_payload, timeout=2, headers={"User-Agent": "WSTN-MQTT-Subscriber/1.0"})
                logger.info(f"API Response: {resp.status_code}")
            except Exception as e:
                logger.error(f"API Failed: {e}")

    except Exception as e:
        logger.exception("CRITICAL FAILURE processing message")

# --- 6. MAIN EXECUTION ---
if __name__ == "__main__":
    client = mqtt.Client()
    
    # Enable internal client logging (pipes to on_log)
    client.enable_logger(logger)
    
    # Attach Callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_log  # <--- This is the key for maximum verbosity

    logger.info(f"Connecting to broker {MQTT_BROKER}:{MQTT_PORT}...")
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except ConnectionRefusedError:
        logger.critical("Could not connect to MQTT Broker! Is it running?")
    except KeyboardInterrupt:
        logger.info("Stopping subscriber...")
        client.disconnect()
