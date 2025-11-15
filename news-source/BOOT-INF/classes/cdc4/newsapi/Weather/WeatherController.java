package cdc4.newsapi.Weather;

import java.time.LocalDate;
import java.util.List;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/weather")
public class WeatherController {
   @Autowired
   private WeatherRepository weatherRepository;
   private static final Logger logger = LogManager.getLogger(WeatherController.class);

   @PostMapping
   public ResponseEntity<String> createWeatherEntry(@RequestBody Weather weather) {
      this.weatherRepository.save(weather);
      logger.info("Weather entry for " + weather.getCreated() + " saved successfully");
      return ResponseEntity.ok("Weather entry created");
   }

   @GetMapping("/latest")
   public ResponseEntity<Weather> getLatestWeather() {
      logger.info("Getting latest weather entry");
      return ResponseEntity.ok(this.weatherRepository.findTopByOrderByCreatedDesc());
   }

   @GetMapping
   public ResponseEntity<List<Weather>> getWeatherByDate(@RequestParam String date) {
      logger.info("Getting weather entries for " + date);
      return ResponseEntity.ok(this.weatherRepository.findAllByCreatedBetween(LocalDate.parse(date).atStartOfDay(), LocalDate.parse(date).atTime(23, 59, 59)));
   }

   @GetMapping("/between")
   public ResponseEntity<List<Weather>> getWeatherBetween(@RequestParam String start, @RequestParam String end) {
      logger.info("Getting weather entries between " + start + " and " + end);
      return ResponseEntity.ok(this.weatherRepository.findAllByCreatedBetween(LocalDate.parse(start).atStartOfDay(), LocalDate.parse(end).atTime(23, 59, 59)));
   }
}
