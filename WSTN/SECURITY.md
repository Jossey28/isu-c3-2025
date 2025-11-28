# WSTN Security Guide - Pickle Deserialization Protection

## System Architecture Overview

The Weather Station Network (WSTN) connects external data sources to the WWW website through the following data flow:

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│   Arduino/LoRa      │       │    MQTT Broker      │       │   MQTT Subscriber   │
│   (External)        │──────▶│   (Competition)     │──────▶│   mqtt_subscriber.py│
│   Weather Sensors   │       │                     │       │                     │
└─────────────────────┘       └─────────────────────┘       └──────────┬──────────┘
                                                                       │
                                                                       ▼
                              ┌─────────────────────┐       ┌─────────────────────┐
                              │    News Website     │       │   Weather Backend   │
                              │   (Nuxt.js)         │◀──────│   (Go @ :8080)      │
                              │   /api/weather.ts   │       │   /weather          │
                              └─────────────────────┘       └─────────────────────┘
```

### Data Flow Details:

1. **External Source** (Out of Scope): Arduino transmits weather data via LoRa to an ISEAGE machine
2. **MQTT Publisher** (Out of Scope): Pickles the raw bytes and publishes to MQTT topic
3. **MQTT Subscriber** (In Scope - `mqtt_subscriber.py`):
   - Subscribes to `TEAM_X/weather_data` topic
   - Deserializes pickle data using SafeUnpickler
   - POSTs hex-encoded data to Weather Backend
   - POSTs parsed weather data to News API
4. **Weather Backend** (`www/weather-backend/backend.go`):
   - Receives hex data at `/weather` endpoint
   - Stores data in MySQL database
   - Provides `/weather/latest` endpoint (API key protected)
5. **News Website** (`www/news-website`):
   - Fetches weather from backend via `/api/weather.ts`
   - Displays weather alongside news articles

## Pickle Deserialization Vulnerability

### The Threat

Python's `pickle` module is inherently insecure. When deserializing (unpickling) data, Python can execute arbitrary code embedded in the pickle stream. An attacker who controls the pickled data can:

- Execute system commands (e.g., `os.system("rm -rf /")`)
- Spawn reverse shells
- Read/write files
- Escalate privileges

### Attack Vector in This System

Since the MQTT publisher is external and potentially untrusted, an attacker could:
1. Publish a malicious pickle payload to your team's MQTT topic
2. The subscriber would deserialize it, executing the embedded malicious code
3. The attacker gains code execution on the WSTN box

### Protection Implemented

The `SafeUnpickler` class in `mqtt_subscriber.py` provides defense-in-depth:

```python
SAFE_BUILTINS = {
    "builtins": {"bytes", "bytearray"}  # Only byte types allowed
}

class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in SAFE_BUILTINS and name in SAFE_BUILTINS[module]:
            return super().find_class(module, name)
        logger.warning(f"SECURITY: Blocked pickle deserialization of {module}.{name}")
        raise pickle.UnpicklingError(f"Deserialization attempt rejected: {module}.{name}")
```

This works by:
1. Intercepting all class lookups during unpickling
2. Only allowing `bytes` and `bytearray` types from the `builtins` module
3. Rejecting and logging any attempt to deserialize dangerous types

## Additional Security Recommendations

### 1. Network Segmentation
- Restrict which hosts can connect to your MQTT subscriber
- Use firewall rules to limit inbound connections

### 2. Input Validation
The subscriber validates weather data:
- Type checking (must be bytes or bytearray)
- Length validation (minimum 8 bytes required)

### 3. Logging and Monitoring
Security events are logged:
- Blocked deserialization attempts
- Network errors
- Invalid data formats

Monitor logs for patterns like:
```
SECURITY: Blocked pickle deserialization of posix.system
SECURITY: Invalid data type received
```

### 4. Rate Limiting
Consider adding rate limiting to prevent DoS attacks via message flooding.

### 5. API Security
- The Weather Backend uses API key authentication for sensitive endpoints
- Ensure `API_KEY_FLAG` is set and kept secret

## Testing Security

To verify that the SafeUnpickler protection is working correctly, you can send a test message
that contains a non-whitelisted type. The SafeUnpickler will block any class that is not in
the strict whitelist of allowed types (only `bytes` and `bytearray`).

When an attacker attempts to send a malicious payload (e.g., using Python's `__reduce__` method
to execute arbitrary code), the SafeUnpickler will intercept the class lookup and reject it.

The subscriber will log blocked attempts:
```
SECURITY: Blocked pickle deserialization of posix.system
```

Monitor your logs for these messages to detect potential attack attempts.

## Best Practices

1. **Keep pickle whitelist minimal** - Only allow types you actually need
2. **Monitor security logs** - Watch for blocked deserialization attempts
3. **Update dependencies** - Keep paho-mqtt, requests, and other packages current
4. **Principle of least privilege** - Run the subscriber with minimal permissions
5. **Consider alternatives** - If you control the publisher, use JSON instead of pickle
