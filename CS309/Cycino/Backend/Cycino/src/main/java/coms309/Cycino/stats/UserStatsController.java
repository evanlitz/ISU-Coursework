package coms309.Cycino.stats;

import coms309.Cycino.Enums;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
public class UserStatsController {

    @Autowired
    private UserStatsRepo userStatsRepo;

    @GetMapping("/stats/{game}")
    public UserStats getStats(@PathVariable String game, @RequestHeader("userId") Long userId){
       return userStatsRepo.findById(userId + game.toUpperCase()).orElse(null);
    }

    @GetMapping("/stats/all/{game}")
    public List<UserStats> getStats(@PathVariable String game){
        List<UserStats> userStats = new ArrayList<>();
        for(UserStats u : userStatsRepo.findAll()){
            String id = u.getUserStatsId();
            id = id.substring((u.getUserId() + "").length());
            if(id.equalsIgnoreCase(game))
                userStats.add(u);
        }
        userStats.sort((o2, o1) -> (int) ((o1.getNet() - o2.getNet()) / (Math.abs(o1.getNet() - o2.getNet()))));
        return userStats;
    }

    @PostMapping("/stats/create/{game}")
    public Map<String, Object> createStats(@PathVariable String game, @RequestHeader("userId") Long userId ){
        Map<String, Object> response = new HashMap<>();
        if(!userStatsRepo.existsById(userId + game.toUpperCase())){
            response.put("status", "200 ok");
            userStatsRepo.save(new UserStats(userId, Enums.GameEnums.valueOf(game)));
            response.put("Id", userId + game.toUpperCase());
            return response;
        }
        response.put("status", "500");
        response.put("error", "user already exists");
        return response;
    }

    @DeleteMapping("/stats/delete/{game}")
    public Map<String, Object> delete(@PathVariable String game,@RequestHeader Long userId){
        Map<String, Object> response = new HashMap<>();
        if(userStatsRepo.existsById(userId + game.toUpperCase())){
            userStatsRepo.deleteById(userId + game.toUpperCase());
            response.put("status", "200 ok");
            return response;
        }
        response.put("status", "404");
        response.put("error", "No user with that id");
        return response;
    }
    @PutMapping("/stats/update/{win}/{loss}/{chips}/{game}")
    public Map<String, Object> update(@PathVariable int win, @PathVariable int loss, @PathVariable int chips, @PathVariable String game, @RequestHeader("userId") Long userId){
        Map<String,Object> response = new HashMap<>();
        UserStats u = userStatsRepo.findById(userId + game.toUpperCase()).orElse(null);
        if(u != null) {
            u.updateWins(win, loss, chips);
            userStatsRepo.save(u);
            response.put("status", "200 ok");
            response.put("userStats", u);
            return response;
        }
        response.put("status", "404");
        response.put("error", "no user found");
        return response;
    }
}
