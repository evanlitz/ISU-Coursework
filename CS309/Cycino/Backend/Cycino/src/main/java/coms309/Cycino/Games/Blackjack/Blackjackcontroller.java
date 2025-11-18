package coms309.Cycino.Games.Blackjack;

import coms309.Cycino.Games.GameLogic.BlackJackLogic;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
public class Blackjackcontroller {

    @Autowired
    private BlackjackService bjs;

    @PostMapping("/blackjack/create/{lobby}")
    public Map<String, Object> createGame(@PathVariable Long lobby){
        return bjs.createGame(6, lobby);
    }
    @PostMapping("/blackjack/create/{lobby}/{deck}")
    public Map<String, Object> createGame(@PathVariable int deck, @PathVariable Long lobby){
        return bjs.createGame(deck, lobby);
    }

    @PutMapping("/blackjack/hit/{lobby}/{userId}")
    public Map<String, Object> hit(@PathVariable Long lobby, @PathVariable Long userId){
        return bjs.hit(lobby, userId);
    }
    @PutMapping("/blackjack/stand/{lobby}/{userId}")
    public Map<String, Object> stand(@PathVariable Long lobby, @PathVariable Long userId){
        return bjs.stand(lobby, userId);
    }

    @PutMapping("/blackjack/double/{lobby}/{userId}")
    public Map<String, Object> doubleBlackJack(@PathVariable Long lobby, @PathVariable Long userId){
        return bjs.dou(lobby, userId);
    }
    @PutMapping("/blackjack/split/{lobby}/{userId}")
    public Map<String, Object> Split(@PathVariable Long lobby, @PathVariable Long userId){
        return bjs.split(lobby, userId);
    }

    @DeleteMapping("/blackjack/delete/{lobby}")
    public Map<String, Object> delete(@PathVariable Long lobby){
        return bjs.deleteGame(lobby);
    }

    @PutMapping("/blackjack/deal/{lobby}")
    public Map<String, Object> deal(@PathVariable Long lobby){
        return bjs.start(lobby);
    }

    @PutMapping("/blackjack/finish/{lobby}")
    public Map<String, Object> finish(@PathVariable Long lobby){
        return bjs.finish(lobby);
    }

    @GetMapping("/blackjack/gethand/{lobby}/{userId}")
    public Map<String, Object> getHand(@PathVariable Long lobby, @PathVariable Long userId){
        return bjs.getHand(lobby, userId);
    }

    @GetMapping("/blackjack/getdealer/{lobby}")
    public Map<String, Object> getDealer(@PathVariable Long lobby){
        return bjs.getDealer(lobby);
    }
    @GetMapping("/blackjack/gethands/{lobby}")
    public Map<String, Object> gethands(@PathVariable Long lobby){
        return bjs.getHands(lobby);
    }

    @PutMapping("/blackjack/bet/{lobby}/{userId}/{bet}")
    public Map<String, Object> addBet(@PathVariable long lobby, @PathVariable long userId, @PathVariable double bet){
        return bjs.setBet(lobby, userId, (int) bet);
    }

}
