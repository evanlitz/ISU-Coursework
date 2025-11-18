package coms309;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PathVariable;

import javax.swing.*;
import java.awt.*;

@RestController
class WelcomeController {

    @GetMapping("/")
    public String welcome() {
        return "Hello and welcome to COMS 3090";
    }

    @GetMapping("/{name}")
    public String welcome(@PathVariable String name) {
        return "Hello and welcome to COMS 3090: " + name;
    }

    @GetMapping("/secret/{animal}")
    public String secret(@PathVariable String animal) {return "Your favorite animal is a(n) " + animal;}
}
