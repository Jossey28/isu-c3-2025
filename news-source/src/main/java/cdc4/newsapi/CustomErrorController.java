package cdc4.newsapi;

import org.springframework.boot.web.servlet.error.ErrorController;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import jakarta.servlet.http.HttpServletResponse;

@Controller
public class CustomErrorController implements ErrorController {
    @GetMapping("/error")
    public String handleError() {
        System.out.println("You shouldn't be here; an error has occurred.");
        return "redirect:/broadcast/news/live";
    }
}
