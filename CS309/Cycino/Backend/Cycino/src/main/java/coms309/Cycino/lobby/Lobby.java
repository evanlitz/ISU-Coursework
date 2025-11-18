package coms309.Cycino.lobby;

import coms309.Cycino.users.User;
import jakarta.persistence.*;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

@Entity
public class Lobby {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private long lobbyId;

    @OneToMany
    private Set<User> players = new HashSet<>();

    private Long gameId;

    public Lobby(){

    }
    public Lobby(User u){
        players.add(u);
    }

    public Lobby(Collection<User> users){
        players.addAll(users);
    }

    public void addPlayer(User u){
        players.add(u);
    }

    public void removePlayer(User u){
        players.remove(u);
    }

    public long getLobbyId(){
        return lobbyId;
    }

    public Set<User> getPlayers(){
        return players;
    }

    public void setGameId(Long id){
        gameId = id;
    }

    public long getId(){
        return gameId;
    }


}
