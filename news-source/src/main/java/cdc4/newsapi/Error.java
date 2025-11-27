package cdc4.newsapi;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Error {
    @GetMapping("/error")
    public String handleError() {
        System.out.println("You shouldn't be here; an error has occurred.");
        return "redirect:/broadcast/news/live";
    }
}
