package cdc4.newsapi.Weather;

import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.Immutable;

@Entity
@Immutable
public class Weather {
   @Id
   @GeneratedValue(strategy = GenerationType.IDENTITY)
   private int id;
   private double temp;
   private double humidity;
   private double airPressure;
   private double windSpeed;
   private double uvIndex;
   private double precipitation;
   @CreationTimestamp
   @Column(updatable = false, nullable = false)
   private LocalDateTime created;

   public Weather(double temp, double humidity, double airPressure, double windSpeed, double uvIndex, double precipitation) {
      this.temp = temp;
      this.humidity = humidity;
      this.airPressure = airPressure;
      this.windSpeed = windSpeed;
      this.uvIndex = uvIndex;
      this.precipitation = precipitation;
   }

   public int getId() {
      return this.id;
   }

   public double getTemp() {
      return this.temp;
   }

   public double getHumidity() {
      return this.humidity;
   }

   public double getAirPressure() {
      return this.airPressure;
   }

   public double getWindSpeed() {
      return this.windSpeed;
   }

   public double getUvIndex() {
      return this.uvIndex;
   }

   public double getPrecipitation() {
      return this.precipitation;
   }

   public LocalDateTime getCreated() {
      return this.created;
   }

   public void setId(final int id) {
      this.id = id;
   }

   public void setTemp(final double temp) {
      this.temp = temp;
   }

   public void setHumidity(final double humidity) {
      this.humidity = humidity;
   }

   public void setAirPressure(final double airPressure) {
      this.airPressure = airPressure;
   }

   public void setWindSpeed(final double windSpeed) {
      this.windSpeed = windSpeed;
   }

   public void setUvIndex(final double uvIndex) {
      this.uvIndex = uvIndex;
   }

   public void setPrecipitation(final double precipitation) {
      this.precipitation = precipitation;
   }

   public void setCreated(final LocalDateTime created) {
      this.created = created;
   }

   public Weather() {
   }
}
