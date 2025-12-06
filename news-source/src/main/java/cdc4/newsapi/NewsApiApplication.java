package cdc4.newsapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SpringBootApplication
public class NewsApiApplication {

   private static final Logger logger = LoggerFactory.getLogger(NewsApiApplication.class);

   public static void main(String[] args) {
      SpringApplication.run(NewsApiApplication.class, args);

      //test log line
      logger.info("Application started successfully, Log4j2 is active");
   }
}
