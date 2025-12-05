#include "Arduino.h"
#include "images.h"
#include "LoRaWan_APP.h"
#include <Wire.h>  
#include "HT_SSD1306Wire.h"

/********************************* LoRa Config *********************************************/
#define RF_FREQUENCY        915000000 // Hz
#define TX_OUTPUT_POWER     10        // dBm
#define LORA_BANDWIDTH      0         // 125 kHz
#define LORA_SPREADING_FACTOR 7       // SF7
#define LORA_CODINGRATE     1         // 4/5
#define LORA_PREAMBLE_LENGTH 8
#define LORA_FIX_LENGTH_PAYLOAD_ON false
#define LORA_IQ_INVERSION_ON        false
#define BUFFER_SIZE         17       // Max payload for SF7
#define FIRST_WRITABLE_PACKET_POSITION 1
#define TEAM_NUMBER 0x28
#define TRANSMITTAL_ITERATION 1

/********************************* Globals *********************************************/
uint8_t txpacket[BUFFER_SIZE] = {TEAM_NUMBER};
static RadioEvents_t RadioEvents;

SSD1306Wire factoryDisplay(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED);
uint64_t chipid;

/********************************* Hardware Helpers *********************************************/
void VextON()  { pinMode(Vext, OUTPUT); digitalWrite(Vext, LOW);  }
void VextOFF() { pinMode(Vext, OUTPUT); digitalWrite(Vext, HIGH); }

/********************************* OLED Helpers *********************************************/
void initDisplay() {
  factoryDisplay.init();
  factoryDisplay.clear();
  factoryDisplay.display();
}

void showLogo() {
  factoryDisplay.clear();
  factoryDisplay.drawXbm(0, 5, logo_width, logo_height, (const unsigned char *)logo_bits);
  factoryDisplay.display();
}

/********************************* LoRa Helpers *********************************************/
void lora_init() {
  Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
  Radio.Init(&RadioEvents);
  Radio.SetChannel(RF_FREQUENCY);
  Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                    LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                    LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                    true, 0, 0, LORA_IQ_INVERSION_ON, 3000);
}

// Generate a random 6-character "geo" string
String randomStringBytes(int length) {
    String s = "";
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (int i = 0; i < length; i++) {
        s += charset[random(0, sizeof(charset) - 1)];
    }
    return s;
}

std::array<uint8_t, BUFFER_SIZE> generatePayloadBytes(uint8_t reserved[2]) {
    std::array<uint8_t, BUFFER_SIZE> payload;

    // Reserved bytes

    payload[1] = reserved[0];
    payload[2] = reserved[1];

    // Sensor data (scaled to 1 byte each)
    payload[3] = random(50, 101);   // Temp
    payload[4] = random(20, 91);    // Humidity
    payload[5] = random(0, 26);     // Wind speed
    payload[6] = random(0, 151);    // Air quality

/********************************* [INSERT FLAG HERE] *********************************************/
    String flag = randomStringBytes(10); //this will be done by ISEAGE
/********************************* [INSERT FLAG HERE] *********************************************/
    for (int i = 0; i < 10; i++) {
        payload[7 + i] = flag[i];
    }

    return payload;
}

/********************************* [COMPETITOR CODE] *********************************************/

void manipulateOutgoingPayloadData() {
    static const uint8_t PSK1[32] = "SkibidiLoRa_NoCapFR_ISEAGE_Sigma";
    static const uint8_t PSK2[32] = "Team0x28NoMid_Bussin_C3_2025_420";
    static const uint8_t PSK3[32] = "Gyatt_WeatherStation_OnGod_PSK3_";
    static const uint8_t PSK4[32] = "RizzEncrypt_Layer4_Fanum_Tax_Yeet";
    static const uint8_t PSK5[32] = "IonlyFW_Ligma_PSK5_Vibes_Lowkey_L";

    // Global sequence number
    static uint16_t packetSequenceNumber = 0;

    uint8_t reserved[2] = {0x01, 0x02};
    std::array<uint8_t, BUFFER_SIZE> payloadBytes = generatePayloadBytes(reserved);

    /*
    Decrypted packet format (17 bytes total):
    TEAM_NUMBER
    reserved[0] = 01
    reserved[1] = 02
    temp = 0x45 or 69
    humidity = 0x3e or 62
    wind speed = 0x0b or 11
    air quality = 0x73 or 115
    flag = 0x70 4a 66 72 44 45 56 4b 68 31 or pJfrDEVKh1
    */

    // Secure packet format (17 bytes total):
    // Byte 0:     TEAM_NUMBER (unchanged)
    // Bytes 1-2:  Sequence number (big-endian, 16-bit) - prevents replay
    // Bytes 3-14: XOR-encrypted payload (12 bytes) - confidentiality with 5-layer PSK
    // Bytes 15-16: Integrity tag (2 bytes) - detects tampering

    packetSequenceNumber++;

    // Extract plaintext payload (12 bytes)
    uint8_t plaintext[12];
    for (int i = 0; i < 12; i++) {
        plaintext[i] = payloadBytes[i + 1];
    }

    // Apply 5-layer XOR encryption with sequence-derived keystreams
    uint8_t encrypted[12];
    for (int i = 0; i < 12; i++) {
        // Derive 5 keystream bytes (one from each PSK layer) based on sequence number
        uint8_t seq_high = (packetSequenceNumber >> 8) & 0xff;
        uint8_t seq_low = packetSequenceNumber & 0xff;

        uint8_t ks1 = PSK1[i % 32] ^ seq_high ^ PSK1[(i + 1) % 32];
        uint8_t ks2 = PSK2[i % 32] ^ seq_low ^ PSK2[(i + 3) % 32];
        uint8_t ks3 = PSK3[i % 32] ^ seq_high ^ PSK3[(i + 5) % 32];
        uint8_t ks4 = PSK4[i % 32] ^ seq_low ^ PSK4[(i + 7) % 32];
        uint8_t ks5 = PSK5[i % 32] ^ seq_high ^ PSK5[(i + 11) % 32];

        // XOR plaintext with all 5 keystream layers
        encrypted[i] = plaintext[i] ^ ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5;
    }

    // Build secure packet
    txpacket[0] = TEAM_NUMBER;  // Preserve team identifier
    txpacket[1] = (packetSequenceNumber >> 8) & 0xff;  // Sequence (high byte)
    txpacket[2] = packetSequenceNumber & 0xff;         // Sequence (low byte)

    // Copy encrypted payload
    for (int i = 0; i < 12; i++) {
        txpacket[3 + i] = encrypted[i];
    }

    // Compute integrity tag by XOR-mixing across all 5 PSKs, sequence, and ciphertext
    uint8_t tag_byte_0 = TEAM_NUMBER ^ txpacket[1] ^ txpacket[2];
    uint8_t tag_byte_1 = 0;

    for (int i = 0; i < 12; i++) {
        tag_byte_0 ^= encrypted[i];
        tag_byte_1 ^= (PSK1[i % 32] ^ PSK2[i % 32] ^ PSK3[i % 32] ^ PSK4[i % 32] ^ PSK5[i % 32]);
    }

    txpacket[15] = tag_byte_0;
    txpacket[16] = tag_byte_1;

    //
    // BACKEND DECRYPTION (e.g., mqtt_subscriber.py or weather-backend):
    // 1. Extract seq (bytes 1-2), encrypted (bytes 3-14), tag (bytes 15-16)
    // 2. Recompute tag and verify against bytes 15-16 (reject on mismatch = tampering)
    // 3. Check seq: reject if seq <= last_seen_seq[device_id] (replay protection)
    // 4. Update last_seen_seq[device_id] = seq
    // 5. Decrypt by XOR with 5-layer keystreams:
    //    - for i in 0..11:
    //        seq_high = (seq >> 8) & 0xff
    //        seq_low = seq & 0xff
    //        ks1 = PSK1[i%32] ^ seq_high ^ PSK1[(i+1)%32]
    //        ks2 = PSK2[i%32] ^ seq_low ^ PSK2[(i+3)%32]
    //        ks3 = PSK3[i%32] ^ seq_high ^ PSK3[(i+5)%32]
    //        ks4 = PSK4[i%32] ^ seq_low ^ PSK4[(i+7)%32]
    //        ks5 = PSK5[i%32] ^ seq_high ^ PSK5[(i+11)%32]
    //        plaintext[i] = encrypted[i] ^ ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5
    // 6. Restore and save plaintext payload to DB
    //
}

int oledLine = 1; 

void sendPacket() {
    // Print to Serial
    Serial.print("Sending packet bytes: ");
    for (int i = 0; i < BUFFER_SIZE; i++) {
        Serial.print(txpacket[i], HEX);
        Serial.print(" ");
    }
    Serial.println();

    // Display on OLED
    String line = "";
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (txpacket[i] < 0x10) line += "0";
        line += String(txpacket[i], HEX) + " ";
    }

    factoryDisplay.drawString(0, oledLine * 8, line); 
    factoryDisplay.display();

    oledLine++;
    if (oledLine >= 8) { 
        factoryDisplay.clear();
        oledLine = 0;
    }

    // Send over LoRa
    Radio.Send(txpacket, BUFFER_SIZE);
}

/********************************* Setup & Loop *********************************************/
void setup() {
    Serial.begin(115200);
    randomSeed(analogRead(0));

    VextON();
    initDisplay();
    showLogo(); delay(3000);
    factoryDisplay.clear();
    lora_init();

    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);

    uint8_t reserved[3] = {0x01, 0x02, 0x03};
    manipulateOutgoingPayloadData();
    for (int i = 0; i < 3; i++) {
        delay(5000);
        sendPacket();
    }
    oledLine++;
    factoryDisplay.drawString(0, oledLine * 8, "Complete!"); 
    factoryDisplay.display();
}

void loop() {
}