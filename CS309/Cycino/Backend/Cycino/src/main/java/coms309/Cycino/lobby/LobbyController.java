package coms309.Cycino.lobby;

import coms309.Cycino.users.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;
import java.util.Map;

@RestController
public class LobbyController {

    @Autowired
    private LobbyService service;



    @PostMapping("/lobby/create")
    public Map<String, Object> startLobby(){
        return service.startLobby();
    }

    @PostMapping("/lobby/create/{userId}")
    public Map<String, Object> startLobby(@PathVariable Long userId){
        return service.startLobby(userId);
    }

    @DeleteMapping("/lobby/delete/{id}/{userId}")
    public Map<String, Object> delete(@PathVariable Long id, @PathVariable long userId){
        return service.delete(id, userId);
    }

    @PutMapping("/lobby/add/{id}/{userId}")
    public Map<String, Object> addPlayer(@PathVariable Long userId, @PathVariable Long id){
        return service.addPlayer(userId, id);
    }

    @PutMapping("/lobby/remove/{id}/{userId}")
    public Map<String, Object> removePlayer(@PathVariable Long userId, @PathVariable Long id){
        return service.removePlayer(userId, id);
    }

    @GetMapping("/lobby/{id}")
    public Map<String, Object> getPlayers(@PathVariable Long id){
        return service.getPlayers(id);
    }
}
