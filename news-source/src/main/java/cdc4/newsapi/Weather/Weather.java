package cdc4.newsapi.Weather;

import java.time.LocalDateTime;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import org.hibernate.annotations.CreationTimestamp;

@Entity
public class Weather {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    // Changed from 'temp' to 'temperature' to match Controller
    // Changed from double to int to match LoRa payload
    private int temperature;
    private int humidity;
    private int windSpeed;
    
    // Added missing fields required by Controller
    private int airQuality;
    private String flag;

    @CreationTimestamp
    @Column(updatable = false, nullable = false)
    private LocalDateTime created;

    // --- Constructors ---
    public Weather() {
    }

    public Weather(int temperature, int humidity, int windSpeed, int airQuality, String flag) {
        this.temperature = temperature;
        this.humidity = humidity;
        this.windSpeed = windSpeed;
        this.airQuality = airQuality;
        this.flag = flag;
    }

    // --- Getters and Setters ---

    public int getId() {
        return this.id;
    }

    public void setId(final int id) {
        this.id = id;
    }

    public int getTemperature() {
        return this.temperature;
    }

    public void setTemperature(final int temperature) {
        this.temperature = temperature;
    }

    public int getHumidity() {
        return this.humidity;
    }

    public void setHumidity(final int humidity) {
        this.humidity = humidity;
    }

    public int getWindSpeed() {
        return this.windSpeed;
    }

    public void setWindSpeed(final int windSpeed) {
        this.windSpeed = windSpeed;
    }

    public int getAirQuality() {
        return this.airQuality;
    }

    public void setAirQuality(final int airQuality) {
        this.airQuality = airQuality;
    }

    public String getFlag() {
        return this.flag;
    }

    public void setFlag(final String flag) {
        this.flag = flag;
    }

    public LocalDateTime getCreated() {
        return this.created;
    }

    public void setCreated(final LocalDateTime created) {
        this.created = created;
    }
}