package coms309.Cycino.Games.poker;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class PokerController {

    @Autowired
    private PokerService service;

    @PostMapping("/poker/create/{lobby}")
    public Map<String, Object> createPoker(@PathVariable long lobby){
        return service.createPoker(lobby);
    }

    @GetMapping("/poker/eval/{lobby}")
    public Map<String, Object> getEval(@PathVariable long lobby){
        return service.getEval(lobby);
    }

    @PutMapping("poker/start/{lobby}")
    public Map<String, Object> start(@PathVariable long lobby){
        return service.startGame(lobby);
    }

    @GetMapping("poker/hands/{lobby}")
    public Map<String, Object> getHands(@PathVariable long lobby){
        return service.getHands(lobby);
    }

    @GetMapping("poker/finish/{lobby}")
    public Map<String, Object> finish(@PathVariable long lobby){
        return service.finish(lobby);
    }

    @PutMapping("/poker/fold/{lobby}/{id}")
    public Map<String, Object> fold(@PathVariable long lobby, @PathVariable long id){
        return service.fold(lobby, id);
    }
    @PutMapping("/poker/call/{lobby}/{id}")
    public Map<String, Object> call(@PathVariable long lobby, @PathVariable long id){
        return service.call(lobby, id);
    }

    @PutMapping("/poker/raise/{lobby}/{id}/{bet}")
    public Map<String, Object> raise(@PathVariable long lobby, @PathVariable long id, @PathVariable double bet){
        return service.raise(lobby, id, (int)bet);
    }

    @DeleteMapping("/poker/delete/{lobby}")
    public Map<String, Object> delete(@PathVariable long lobby){
        return service.deleteGame(lobby);
    }

    @PutMapping("/poker/reset/{lobby}")
    public Map<String, Object> reset(@PathVariable long lobby){
        return service.reset(lobby);
    }
}
