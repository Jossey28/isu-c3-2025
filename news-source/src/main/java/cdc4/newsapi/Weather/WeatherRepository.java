package cdc4.newsapi.Weather;

import java.time.LocalDateTime;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WeatherRepository extends JpaRepository<Weather, Integer> {
   Weather findTopByOrderByCreatedDesc();

   List<Weather> findAllByCreatedBetween(LocalDateTime start, LocalDateTime end);
}
