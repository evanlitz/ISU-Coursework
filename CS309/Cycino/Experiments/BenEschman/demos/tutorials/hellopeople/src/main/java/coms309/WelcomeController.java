package coms309;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.swing.*;

/**
 * Simple Hello World Controller to display the string returned
 *
 * @author Vivek Bengre
 */

@RestController
class WelcomeController {

    @GetMapping("/")
    public String welcome() {
        return "Hello and welcome to COMS 309";
    }

    @GetMapping("/secret")
    public String secret(){return "you found a secret";}

    @GetMapping("/secret2")
    public String displayImage() {
        return "<html><body><img src='dog.jpg' /></body></html>";
    }
}
