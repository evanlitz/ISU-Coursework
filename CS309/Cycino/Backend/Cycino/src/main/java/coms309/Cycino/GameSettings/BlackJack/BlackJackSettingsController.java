package coms309.Cycino.GameSettings.BlackJack;

import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/gameSettings/blackjack")
public class BlackJackSettingsController {

    @Autowired
    private UserService userService;

    @Autowired
    private BlackJackSettingsService blackJackSettingsService;

    @GetMapping("/user/{id}")
    public BlackJackSettings getBlackJackSettings(@PathVariable Long id) {
        BlackJackSettings settings = blackJackSettingsService.getBlackJackSettings(id);
        return settings;
    }

    @PutMapping("/user/{id}/update")
    public Map<String, Object> updateBlackJackSettings(@PathVariable Long id, @RequestBody BlackJackSettings settings) {
        Map<String, Object> response = new HashMap<>();
        if(blackJackSettingsService.updateBlackJackSettings(settings, id)) {
            response.put("status", "200 OK");
        } else {
            response.put("status", "400 Bad Request");
        }
        return response;
    }
}
