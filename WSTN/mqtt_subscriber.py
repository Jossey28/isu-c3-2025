import pickle
import environ
import io
import logging

import paho.mqtt.client as mqtt
import requests

# Configure logging for security events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Can leave this as 127.0.0.1 for now
#but you will need to change it come comp day
#(address TBD)
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

#Change this to match your team number
MQTT_TOPIC = "TEAM_2/weather_data"
#Change this to the address of your WWW box
POST_URL = environ.Env().str("POST_URL")
#Change this to the address of your NEWS box
API_URL = environ.Env().str("API_URL")

# SECURITY: Pickle Deserialization Protection
# 
# WARNING: Python's pickle module is inherently insecure. Deserializing untrusted
# pickle data can lead to arbitrary code execution. The SafeUnpickler class below
# provides defense-in-depth by restricting which classes can be instantiated during
# deserialization.
#
# This protection works by:
# 1. Intercepting all class lookups during unpickling via find_class()
# 2. Only allowing a strict whitelist of safe primitive types
# 3. Rejecting any attempt to deserialize objects that could execute code
#
# IMPORTANT: While SafeUnpickler mitigates many attacks, pickle should ideally
# be replaced with a safer format (e.g., JSON, MessagePack) if you control
# the publisher. Since the MQTT publisher is out of scope for teams, this
# subscriber must handle pickle data defensively.

# Strict whitelist of allowed types for deserialization
# Only primitive types that cannot execute code are allowed
SAFE_BUILTINS = {
    "builtins": {"bytes", "bytearray"}  # Restricted to only byte types needed for weather data
}

class SafeUnpickler(pickle.Unpickler):
    """
    A restricted unpickler that only allows deserialization of safe primitive types.
    
    This class overrides find_class() to prevent deserialization of dangerous objects
    that could lead to arbitrary code execution (e.g., os.system, subprocess.call).
    
    Security: Rejects any class not in the SAFE_BUILTINS whitelist, which prevents
    attacks using __reduce__, __reduce_ex__, or other pickle exploitation techniques.
    """
    def find_class(self, module, name):
        if module in SAFE_BUILTINS and name in SAFE_BUILTINS[module]:
            return super().find_class(module, name)
        logger.warning(f"SECURITY: Blocked pickle deserialization of {module}.{name}")
        raise pickle.UnpicklingError(f"Deserialization attempt rejected: {module}.{name}")

def safe_loads(s):
    """
    Safely deserialize pickle data using the restricted SafeUnpickler.
    
    Args:
        s: Bytes containing pickled data
        
    Returns:
        Deserialized object (only bytes or bytearray types allowed)
        
    Raises:
        pickle.UnpicklingError: If deserialization of non-whitelisted types is attempted
    """
    return SafeUnpickler(io.BytesIO(s)).load()

def validate_weather_data(raw_bytes):
    """
    Validate that the weather data has the expected format.
    
    Expected format (minimum 8 bytes):
    - Byte 0: Team number
    - Bytes 1-2: Reserved
    - Byte 3: Temperature
    - Byte 4: Humidity
    - Byte 5: Wind speed
    - Byte 6: Air quality
    - Bytes 7+: Flag
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    if not isinstance(raw_bytes, (bytes, bytearray)):
        logger.warning(f"SECURITY: Invalid data type received: {type(raw_bytes)}")
        return False
    if len(raw_bytes) < 8:
        logger.warning(f"SECURITY: Data too short: {len(raw_bytes)} bytes (minimum 8 required)")
        return False
    return True

def on_message(client, userdata, msg):
    logger.info(f"Received message on topic {msg.topic}")
    try:
        # SECURITY: Use SafeUnpickler to prevent arbitrary code execution
        raw_bytes = safe_loads(msg.payload)
        
        # Validate the data format
        if not validate_weather_data(raw_bytes):
            logger.error("Invalid weather data received, skipping")
            return
            
        logger.info(f"Raw bytes: {raw_bytes}")

        hex_str = raw_bytes.hex()
        logger.info(f"Hex string: {hex_str}")

        payload = {"hex": hex_str}

        response = requests.post(POST_URL, data=payload, timeout=10)
        logger.info(f"POST response: {response.status_code}")

        api_data = {
            "temp": raw_bytes[3],
            "humidity": raw_bytes[4],
            "windSpeed": raw_bytes[5]
        }
        response = requests.post(API_URL, json=api_data, timeout=10)
        logger.info(f"API response: {response.status_code}")
    except pickle.UnpicklingError as e:
        logger.error(f"SECURITY: Pickle deserialization blocked: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
    except Exception as e:
        logger.error(f"Failed to process payload: {e}")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.loop_forever()