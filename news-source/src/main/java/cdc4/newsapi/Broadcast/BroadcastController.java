package cdc4.newsapi.Broadcast;

import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/broadcast")
public class BroadcastController {
   private final ResourceLoader resourceLoader;

   public BroadcastController(ResourceLoader resourceLoader) {
      this.resourceLoader = resourceLoader;
   }

   @GetMapping(value = "/news/live", produces = "video/mp4")
   public ResponseEntity<Resource> streamLiveNews() throws Exception {
      Resource resource = this.resourceLoader.getResource("classpath:static/news.mp4");
      return !resource.exists() ? ResponseEntity.notFound().build() : ResponseEntity.ok().contentType(MediaType.valueOf("video/mp4")).body(resource);
   }
}
