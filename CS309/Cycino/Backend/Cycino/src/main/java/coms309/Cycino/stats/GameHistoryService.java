package coms309.Cycino.stats;

import coms309.Cycino.users.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Set;

@Service
public class GameHistoryService {

    @Autowired
    private GameHistoryRepo repo;

    public long startGame(String game, Set<User> players){
        GameHistory hist = new GameHistory(game, players);
        for(User u: players){
            u.addGameHistory(hist);
        }
        repo.save(hist);
        return hist.getId();
    }

    public void endGame(long id){
        GameHistory hist = repo.findById(id).orElse(null);
        assert hist != null;
        hist.endGame();
        repo.save(hist);
    }

}
