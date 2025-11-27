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

		rawHex := r.FormValue("hex")
		if rawHex == "" {
			http.Error(w, "No data provided", http.StatusBadRequest)
			return
		}

		bytesData, err := hex.DecodeString(rawHex)
		if err != nil {
			http.Error(w, "Invalid hex", http.StatusBadRequest)
			return
		}

		if len(bytesData) < 8 {
			http.Error(w, "Invalid data", http.StatusBadRequest)
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

	fmt.Println("Server running on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
