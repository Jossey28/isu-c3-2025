package main

import (
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/joho/godotenv/autoload"
)

var API_KEY_FLAG = os.Getenv("API_KEY_FLAG")
var DATABASE_URL = os.Getenv("DATABASE_URL")

// Structured loggers
var (
	infoLog     *log.Logger
	warningLog  *log.Logger
	errorLog    *log.Logger
	securityLog *log.Logger
)

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

func logRequest(logger *log.Logger, r *http.Request, msg string) {
	logger.Printf("[%s] %s %s | RemoteAddr=%s | UserAgent=%s | %s",
		time.Now().Format(time.RFC3339),
		r.Method,
		r.URL.Path,
		r.RemoteAddr,
		r.UserAgent(),
		msg)
}

func validateAPIKey(r *http.Request) bool {
	return r.Header.Get("X-Api-Key-Flag") == API_KEY_FLAG
}

func validateUserAgentPost(r *http.Request) bool {
	return r.Header.Get("User-Agent") == "WSTN-MQTT-Subscriber/1.0"
}

func validateUserAgentGet(r *http.Request) bool {
	return r.Header.Get("User-Agent") == "WWW-NEWS-Website/1.0"
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
	// Open main log file for all logs
	allLogsFile, err := os.OpenFile("app.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal("Failed to open app.log: ", err)
	}
	defer allLogsFile.Close()

	// Open security log file
	securityLogFile, err := os.OpenFile("security.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal("Failed to open security.log: ", err)
	}
	defer securityLogFile.Close()

	// Initialize structured logging - all write to app.log only (no console output)
	infoLog = log.New(allLogsFile, "INFO: ", log.Ldate|log.Ltime)
	warningLog = log.New(allLogsFile, "WARNING: ", log.Ldate|log.Ltime)
	errorLog = log.New(allLogsFile, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)

	// Security logs go to both app.log and security.log
	securityLog = log.New(io.MultiWriter(allLogsFile, securityLogFile), "SECURITY: ", log.Ldate|log.Ltime)

	db, err := sql.Open("mysql", DATABASE_URL)
	if err != nil {
		errorLog.Fatal(err)
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
			logRequest(warningLog, r, "Method not allowed")
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		if !validateUserAgentPost(r) {
			logRequest(securityLog, r, "Invalid User-Agent for POST")
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		if !validateAPIKey(r) {
			logRequest(securityLog, r, "Invalid API key")
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		rawHex := r.FormValue("hex")
		if rawHex == "" {
			logRequest(warningLog, r, "Missing hex parameter")
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		packetData, err := hex.DecodeString(rawHex)
		if err != nil || len(packetData) != 17 {
			logRequest(warningLog, r, fmt.Sprintf("Invalid hex data: err=%v, len=%d", err, len(packetData)))
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		if packetData[0] != 0x02 {
			logRequest(warningLog, r, fmt.Sprintf("Invalid packet header: 0x%02x", packetData[0]))
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		bytesData, err := decryptPayload(packetData)
		if err != nil {
			errorLog.Printf("Decryption failed for %s: %v", r.RemoteAddr, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		temperature := int(bytesData[0]) // Index 0
		humidity := int(bytesData[1])    // Index 1
		windSpeed := int(bytesData[2])   // Index 2
		airQuality := int(bytesData[3])  // Index 3
		flag := string(bytesData[4:])    // Index 4 to end

		stmt := `INSERT INTO weather (temperature, humidity, wind_speed, air_quality, flag)
          VALUES (?, ?, ?, ?, ?)`

		_, err = db.Exec(stmt, temperature, humidity, windSpeed, airQuality, flag)
		if err != nil {
			errorLog.Printf("Database insert failed for %s: %v", r.RemoteAddr, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		infoLog.Printf("Data saved from %s: Temp=%d Humidity=%d Wind=%d AQ=%d",
			r.RemoteAddr, temperature, humidity, windSpeed, airQuality)
		fmt.Fprintf(w, "OK")
	})

	http.HandleFunc("/weather/latest", func(w http.ResponseWriter, r *http.Request) {

		if !validateUserAgentGet(r) {
			logRequest(securityLog, r, "Invalid User-Agent for GET")
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		// Validate API key
		if !validateAPIKey(r) {
			logRequest(securityLog, r, "Invalid API key")
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		row := db.QueryRow(`SELECT id, created_at, temperature, humidity, wind_speed, air_quality, flag
                    FROM weather ORDER BY created_at DESC LIMIT 1`)

		var entry WeatherEntry
		err := row.Scan(&entry.ID, &entry.CreatedAt, &entry.Temperature,
			&entry.Humidity, &entry.WindSpeed, &entry.AirQuality, &entry.Flag)
		if err != nil {
			errorLog.Printf("Database query failed for %s: %v", r.RemoteAddr, err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(entry)
	})

	infoLog.Println("Starting weather backend server on https://localhost:8080")
	if err := http.ListenAndServeTLS(":8080", "server.crt", "server.key", nil); err != nil {
		errorLog.Fatal("Server failed to start: ", err)
	}
}
