package cdc4.newsapi.Weather;

import java.time.LocalDate;
import java.util.List;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/weather")
public class WeatherController {

    @Autowired
    private WeatherRepository weatherRepository;
    private static final Logger logger = LogManager.getLogger(WeatherController.class);

    // Track the last sequence number seen to detect replays/drops
    private static int lastSequenceNumber = -1;

    // --- 1. DEFINE PSKS (Must match Transmitter) ---
    private static final byte[] PSK1 = "SkibidiLoRa_NoCapFR_ISEAGE_Sigma".getBytes();
    private static final byte[] PSK2 = "Team0x28NoMid_Bussin_C3_2025_420".getBytes();
    private static final byte[] PSK3 = "Gyatt_WeatherStation_OnGod_PSK3_".getBytes();
    private static final byte[] PSK4 = "RizzEncrypt_Layer4_Fanum_Tax_Yeet".getBytes();
    private static final byte[] PSK5 = "IonlyFW_Ligma_PSK5_Vibes_Lowkey_L".getBytes();

    // --- 2. DECRYPTION LOGIC ---
    private byte[] decryptPayload(byte[] packet) throws IllegalArgumentException {
        if (packet.length != 17) {
            throw new IllegalArgumentException("Invalid packet length: " + packet.length);
        }

        // Extract Sequence (Bytes 1-2)
        int seq = ((packet[1] & 0xFF) << 8) | (packet[2] & 0xFF);

        // Extract Encrypted Payload (Bytes 3-16)
        byte[] encrypted = new byte[14];
        System.arraycopy(packet, 3, encrypted, 0, 14);
        
        byte[] plaintext = new byte[14];

        int seqHigh = (seq >> 8) & 0xFF;
        int seqLow = seq & 0xFF;

        for (int i = 0; i < 14; i++) {
            // Apply 5-layer keystream logic
            int ks1 = PSK1[i % 32] ^ seqHigh ^ PSK1[(i + 1) % 32];
            int ks2 = PSK2[i % 32] ^ seqLow  ^ PSK2[(i + 3) % 32];
            int ks3 = PSK3[i % 32] ^ seqHigh ^ PSK3[(i + 5) % 32];
            int ks4 = PSK4[i % 32] ^ seqLow  ^ PSK4[(i + 7) % 32];
            int ks5 = PSK5[i % 32] ^ seqHigh ^ PSK5[(i + 11) % 32];

            int keystream = ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5;
            
            // XOR and cast back to byte
            plaintext[i] = (byte) (encrypted[i] ^ keystream);
        }

        return plaintext;
    }

    private byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                                 + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }

    // --- 3. UPDATED POST ENDPOINT ---
    @PostMapping
    public ResponseEntity<String> createWeatherEntry(
            @RequestBody EncryptedPayload payload,
            @RequestHeader(value = "User-Agent", defaultValue = "") String userAgent) {
        try {
            // Verify user agent header
            if (!"WSTN-MQTT-Subscriber/1.0".equals(userAgent)) {
                logger.warn("Unauthorized access attempt from User-Agent: " + userAgent);
                return ResponseEntity.status(401).body("Unauthorized");
            }

            if (payload.getHex() == null || payload.getHex().isEmpty()) {
                return ResponseEntity.badRequest().body("Invalid Packet");
            }

            byte[] packetData = hexStringToByteArray(payload.getHex());

            if (packetData.length != 17) {
                 return ResponseEntity.badRequest().body("Invalid Packet Length");
            }

            if (packetData[0] != 0x02) {
                 return ResponseEntity.badRequest().body("Invalid Team ID");
            }

            // --- SEQUENCE CHECK LOGIC ---
            // Extract Sequence (Bytes 1-2)
            int currentSeq = ((packetData[1] & 0xFF) << 8) | (packetData[2] & 0xFF);

            if (currentSeq <= lastSequenceNumber) {
                if (lastSequenceNumber > 65000 && currentSeq < 100) {
                     logger.info("Sequence rollover detected. Resetting tracker.");
                } else {
                     logger.warn("OUT OF ORDER PACKET DETECTED: Received Seq " + currentSeq + 
                                 " but expected > " + lastSequenceNumber);
                     // Optional: return ResponseEntity.badRequest().body("Replay Detected");
                }
            } else {
                if (lastSequenceNumber != -1 && currentSeq > lastSequenceNumber + 1) {
                    logger.warn("PACKET LOSS DETECTED: Jumped from Seq " + lastSequenceNumber + 
                                " to " + currentSeq);
                }
            }
            lastSequenceNumber = currentSeq;
            // ---------------------------

            byte[] decrypted = decryptPayload(packetData);

            Weather weather = new Weather();
            weather.setTemperature(decrypted[0] & 0xFF);
            weather.setHumidity(decrypted[1] & 0xFF);
            weather.setWindSpeed(decrypted[2] & 0xFF);
            weather.setAirQuality(decrypted[3] & 0xFF);

            String flag = new String(decrypted, 4, 10);
            weather.setFlag(flag);
            weather.setCreated(java.time.LocalDateTime.now());

            this.weatherRepository.save(weather);
            logger.info("Decrypted entry saved successfully (Seq " + currentSeq + "). Flag: " + flag);
            
            return ResponseEntity.ok("Weather entry decrypted and created");

        } catch (Exception e) {
            logger.error("Error processing payload", e);
            return ResponseEntity.badRequest().body("Failed to process payload");
        }
    }

    public static class EncryptedPayload {
        private String hex;
        public String getHex() { return hex; }
        public void setHex(String hex) { this.hex = hex; }
    }

    // --- EXISTING GET METHODS ---
    @GetMapping("/latest")
    public ResponseEntity<Weather> getLatestWeather() {
        return ResponseEntity.ok(this.weatherRepository.findTopByOrderByCreatedDesc());
    }

    @GetMapping
    public ResponseEntity<List<Weather>> getWeatherByDate(@RequestParam String date) {
        return ResponseEntity.ok(this.weatherRepository.findAllByCreatedBetween(LocalDate.parse(date).atStartOfDay(), LocalDate.parse(date).atTime(23, 59, 59)));
    }

    @GetMapping("/between")
    public ResponseEntity<List<Weather>> getWeatherBetween(@RequestParam String start, @RequestParam String end) {
        return ResponseEntity.ok(this.weatherRepository.findAllByCreatedBetween(LocalDate.parse(start).atStartOfDay(), LocalDate.parse(end).atTime(23, 59, 59)));
    }
}