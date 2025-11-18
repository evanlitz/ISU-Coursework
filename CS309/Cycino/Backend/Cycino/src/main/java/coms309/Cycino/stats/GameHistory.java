package coms309.Cycino.stats;

import coms309.Cycino.users.User;
import jakarta.persistence.*;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

@Entity
public class GameHistory {

    @Id
    @GeneratedValue
    private Long id;

    private String game;

    private final LocalDateTime startTime;

    private LocalDateTime endTime;

    private Duration duration;

    @ManyToMany
    @JoinTable(
            name = "user_game_history",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "game_history_id")
    )
    private Set<User> players;

    public GameHistory(){
        startTime = LocalDateTime.now();
    }

    public GameHistory(String game, Set<User> players){
        startTime = LocalDateTime.now();
        this.game = game;
        this.players = players;
    }

    public Map<String, Object> addUser(User user){
        Map<String, Object> response = new HashMap<>();
        if(players.contains(user)){
            response.put("status", "500");
            response.put("error", "user already in gameHistory");
            return response;
        }
        players.add(user);
        response.put("status", "200 ok");
        return response;
    }

    public Set<User> getPlayers(){
        return players;
    }

    public String getGame(){
        return game;
    }

    public void endGame(){
        endTime = LocalDateTime.now();
        duration = Duration.between(startTime,endTime);
    }

    public long getId(){
        return id;
    }

}
