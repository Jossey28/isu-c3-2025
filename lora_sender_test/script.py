import os
import random

TEAM_NUMBER = 0x28  # set to 0x02 if you changed the sender for Team 2
PSK1 = b"SkibidiLoRa_NoCapFR_ISEAGE_Sigma"
PSK2 = b"Team0x28NoMid_Bussin_C3_2025_420"
PSK3 = b"Gyatt_WeatherStation_OnGod_PSK3_"
PSK4 = b"RizzEncrypt_Layer4_Fanum_Tax_Yeet"
PSK5 = b"IonlyFW_Ligma_PSK5_Vibes_Lowkey_L"

def build_payload():
    # bytes: reserved[0], reserved[1], temp, humidity, wind, airq, flag[10]
    payload = bytearray(12)
    payload[0:2] = b"\x01\x02"             # reserved
    payload[2] = random.randint(50, 100)   # temp
    payload[3] = random.randint(20, 90)    # humidity
    payload[4] = random.randint(0, 25)     # wind
    payload[5] = random.randint(0, 150)    # air quality
    flag = os.urandom(10)                  # demo flag
    payload[6:16] = flag
    return payload

def encrypt(payload, seq):
    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    encrypted = bytearray(12)
    for i in range(12):
        ks1 = PSK1[i % 32] ^ seq_high ^ PSK1[(i + 1) % 32]
        ks2 = PSK2[i % 32] ^ seq_low ^ PSK2[(i + 3) % 32]
        ks3 = PSK3[i % 32] ^ seq_high ^ PSK3[(i + 5) % 32]
        ks4 = PSK4[i % 32] ^ seq_low ^ PSK4[(i + 7) % 32]
        ks5 = PSK5[i % 32] ^ seq_high ^ PSK5[(i + 11) % 32]
        encrypted[i] = payload[i] ^ ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5
    return encrypted

def tag(encrypted, seq):
    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    tag0 = TEAM_NUMBER ^ seq_high ^ seq_low
    tag1 = 0
    for i, b in enumerate(encrypted):
        tag0 ^= b
        tag1 ^= PSK1[i % 32] ^ PSK2[i % 32] ^ PSK3[i % 32] ^ PSK4[i % 32] ^ PSK5[i % 32]
    return tag0 & 0xFF, tag1 & 0xFF

def build_packet(seq):
    payload = build_payload()
    encrypted = encrypt(payload, seq)
    t0, t1 = tag(encrypted, seq)
    pkt = bytearray(17)
    pkt[0] = TEAM_NUMBER
    pkt[1] = (seq >> 8) & 0xFF
    pkt[2] = seq & 0xFF
    pkt[3:15] = encrypted
    pkt[15] = t0
    pkt[16] = t1
    return pkt

if __name__ == "__main__":
    for seq in range(1, 4):
        pkt = build_packet(seq)
        print(f"seq {seq}: {pkt.hex()}")