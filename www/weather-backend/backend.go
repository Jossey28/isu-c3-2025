package main

import (
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/joho/godotenv/autoload"
)

var API_KEY_FLAG = os.Getenv("API_KEY_FLAG")
var DATABASE_URL = os.Getenv("DATABASE_URL")

// --- 1. DEFINE PSKS (Must match Transmitter) ---
var PSK1 = []byte("SkibidiLoRa_NoCapFR_ISEAGE_Sigma")
var PSK2 = []byte("Team0x28NoMid_Bussin_C3_2025_420")
var PSK3 = []byte("Gyatt_WeatherStation_OnGod_PSK3_")
var PSK4 = []byte("RizzEncrypt_Layer4_Fanum_Tax_Yeet")
var PSK5 = []byte("IonlyFW_Ligma_PSK5_Vibes_Lowkey_L")

type WeatherEntry struct {
	ID          int    `json:"id"`
	CreatedAt   string `json:"created_at"`
	Temperature int    `json:"temperature"`
	Humidity    int    `json:"humidity"`
	WindSpeed   int    `json:"wind_speed"`
	AirQuality  int    `json:"air_quality"`
	Flag        string `json:"flag"`
}

func validateAPIKey(r *http.Request) bool {
	return r.Header.Get("X-Api-Key-Flag") == API_KEY_FLAG
}

func validateUserAgent(r *http.Request) bool {
	return r.Header.Get("User-Agent") == "WSTN-MQTT-Subscriber/1.0"
}

func decryptPayload(packet []byte) ([]byte, error) {
	if len(packet) != 17 {
		return nil, fmt.Errorf("invalid packet length")
	}

	// Extract Sequence (Bytes 1-2)
	seq := (uint16(packet[1]) << 8) | uint16(packet[2])

	// Extract Encrypted Payload (Bytes 3-16)
	encrypted := packet[3:]
	plaintext := make([]byte, 14)

	seqHigh := uint8((seq >> 8) & 0xff)
	seqLow := uint8(seq & 0xff)

	for i := 0; i < 14; i++ {
		// Apply 5-layer keystream logic
		ks1 := PSK1[i%32] ^ seqHigh ^ PSK1[(i+1)%32]
		ks2 := PSK2[i%32] ^ seqLow ^ PSK2[(i+3)%32]
		ks3 := PSK3[i%32] ^ seqHigh ^ PSK3[(i+5)%32]
		ks4 := PSK4[i%32] ^ seqLow ^ PSK4[(i+7)%32]
		ks5 := PSK5[i%32] ^ seqHigh ^ PSK5[(i+11)%32]

		keystream := ks1 ^ ks2 ^ ks3 ^ ks4 ^ ks5
		plaintext[i] = encrypted[i] ^ keystream
	}

	return plaintext, nil
}

func main() {
	db, err := sql.Open("mysql", DATABASE_URL)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS weather (
		id INT AUTO_INCREMENT PRIMARY KEY,
		timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		temperature INT,
		humidity INT,
		wind_speed INT,
		air_quality INT,
		flag VARCHAR(255)
	);`)
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/weather", func(w http.ResponseWriter, r *http.Request) {

		if r.Method != http.MethodPost {
			http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
			return
		}

		if !validateAPIKey(r) {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		if !validateUserAgent(r) {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		rawHex := r.FormValue("hex")
		if rawHex == "" {
			http.Error(w, "No data provided", http.StatusBadRequest)
			return
		}

		packetData, err := hex.DecodeString(rawHex)
		if err != nil || len(packetData) != 17 {
			http.Error(w, "Invalid raw data", http.StatusBadRequest)
			return
		}

		if packetData[0] != 0x02 {
			http.Error(w, "Invalid data", http.StatusBadRequest)
			return
		}

		bytesData, err := decryptPayload(packetData)
		if err != nil {
			http.Error(w, "Decryption failed", http.StatusInternalServerError)
			return
		}

		temperature := int(bytesData[3])
		humidity := int(bytesData[4])
		windSpeed := int(bytesData[5])
		airQuality := int(bytesData[6])
		flag := string(bytesData[7:])

		stmt := `INSERT INTO weather (temperature, humidity, wind_speed, air_quality, flag)
          VALUES (?, ?, ?, ?, ?)`

		_, err = db.Exec(stmt, temperature, humidity, windSpeed, airQuality, flag)
		if err != nil {
			log.Printf("DB Error: %v", err)
			http.Error(w, "DB insert failed", http.StatusInternalServerError)
			return
		}

		fmt.Fprintf(w, "Data saved! Temp=%d Humidity=%d Wind=%d AQ=%d Flag=%s",
			temperature, humidity, windSpeed, airQuality, flag)
	})

	http.HandleFunc("/weather/latest", func(w http.ResponseWriter, r *http.Request) {
		// Validate API key
		if !validateAPIKey(r) {
			http.Error(w, "Unauthorized: Invalid API Key", http.StatusUnauthorized)
			return
		}

		row := db.QueryRow(`SELECT id, created_at, temperature, humidity, wind_speed, air_quality, flag
                    FROM weather ORDER BY created_at DESC LIMIT 1`)

		var entry WeatherEntry
		err := row.Scan(&entry.ID, &entry.CreatedAt, &entry.Temperature,
			&entry.Humidity, &entry.WindSpeed, &entry.AirQuality, &entry.Flag)
		if err != nil {
			log.Printf("Query error: %v\n", err)
			http.Error(w, "DB query failed", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(entry)
	})

	fmt.Println("Server running on https://localhost:8080")
	log.Fatal(http.ListenAndServeTLS(":8080", "server.crt", "server.key", nil))
}
