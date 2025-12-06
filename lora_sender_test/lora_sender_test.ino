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
    // 1. Define Keys
    static const uint8_t PSK1[] = "SkibidiLoRa_NoCapFR_ISEAGE_Sigma";
    static const uint8_t PSK2[] = "Team0x28NoMid_Bussin_C3_2025_420";
    static const uint8_t PSK3[] = "Gyatt_WeatherStation_OnGod_PSK3_";
    static const uint8_t PSK4[] = "RizzEncrypt_Layer4_Fanum_Tax_Yeet";
    static const uint8_t PSK5[] = "IonlyFW_Ligma_PSK5_Vibes_Lowkey_L";

    // 2. Manage Sequence Number
    static uint16_t packetSequenceNumber = 0;
    packetSequenceNumber++;

    // 3. Generate Data
    // We pass the reserved bytes, but we will overwrite them in the packet
    // because we need that space for the Sequence Number.
    uint8_t reserved[2] = {0x01, 0x02}; 
    std::array<uint8_t, BUFFER_SIZE> payloadBytes = generatePayloadBytes(reserved);

    /* PAYLOAD MAPPING (17 Bytes Total):
       Index 0:      Team ID (Fixed)
       Index 1-2:    Sequence Number (Overwrites 'Reserved' bytes)
       Index 3-6:    Sensor Data (Temp, Hum, Wind, AQ)
       Index 7-16:   Flag (10 Bytes) - FULLY PRESERVED
    */

    // 4. Prepare Plaintext (14 Bytes: Sensors + Flag)
    // We grab bytes 3 through 16 from the generated payload.
    uint8_t plaintext[14];
    for (int i = 0; i < 14; i++) {
        plaintext[i] = payloadBytes[i + 3]; // +3 skips unused[0] and reserved[1,2]
    }

    // 5. Encrypt (14 Bytes)
    uint8_t encrypted[14];
    for (int i = 0; i < 14; i++) {
        uint8_t seq_high = (packetSequenceNumber >> 8) & 0xff;
        uint8_t seq_low = packetSequenceNumber & 0xff;

        uint8_t ks1 = PSK1[i % 32] ^ seq_high ^ PSK1[(i + 1) % 32];
        uint8_t ks2 = PSK2[i % 32] ^ seq_low ^ PSK2[(i + 3) % 32];
        uint8_t ks3 = PSK3[i % 32] ^ seq_high ^ PSK3[(i + 5) % 32];
        uint8_t ks4 = PSK4[i % 32] ^ seq_low ^ PSK4[(i + 7) % 32];
        uint8_t ks5 = PSK5[i % 32] ^ seq_high ^ PSK5[(i + 11) % 32];

        encrypted[i] = plaintext[i] ^ ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5;
    }

    // 6. Pack the Global 'txpacket'
    txpacket[0] = TEAM_NUMBER;                      // Byte 0
    txpacket[1] = (packetSequenceNumber >> 8) & 0xff; // Byte 1 (Seq High)
    txpacket[2] = packetSequenceNumber & 0xff;        // Byte 2 (Seq Low)

    for (int i = 0; i < 14; i++) {
        txpacket[3 + i] = encrypted[i];             // Bytes 3-16 (Encrypted Data)
    }

    // Note: Integrity Tag (Bytes 15-16 in previous version) was removed 
    // to make room for the full Flag.
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