package cdc4.newsapi;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class CustomErrorController {
    @GetMapping("/error")
    public String handleError() {
        System.out.println("You shouldn't be here; an error has occurred.");
        return "redirect:/broadcast/news/live";
    }
}
