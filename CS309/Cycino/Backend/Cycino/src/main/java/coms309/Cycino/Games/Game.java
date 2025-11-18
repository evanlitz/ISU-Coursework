package coms309.Cycino.Games;

import coms309.Cycino.Games.GameLogic.Deck;
import coms309.Cycino.Games.GameLogic.PlayerHands;
import coms309.Cycino.Games.Lobby.GameChat;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.users.User;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Game {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @OneToOne(cascade = CascadeType.ALL)
    private Deck cards;

    @OneToMany(mappedBy = "game", cascade = CascadeType.REMOVE, orphanRemoval = true)
    private Set<PlayerHands> hands = new HashSet<>();

    @Column(name = "`order`")
    private ArrayList<Long> order = new ArrayList<>();

    @OneToOne
    private Lobby lobby;


    public Game(){}
    public Game(Lobby l, Deck d){
        lobby = l;
        cards = d;
    }

    public Set<PlayerHands> getHands() {
        return hands;
    }

    public PlayerHands getHand(User u){
        System.out.println(hands);
        for(PlayerHands hand: hands){
            if(hand.getPlayer() == null)
                continue;
            if(hand.getPlayer().getId() == u.getId() && !hand.stand())
                return hand;
        }
        return null;
    }

    public Deck getCards(){
        return cards;
    }

    public void setOrder(){
        order = new ArrayList<>();
        for(PlayerHands hand: hands){
            if(hand.getPlayer() != null)
                order.add(hand.getPlayer().getId());
        }
    }

    public void addHand(PlayerHands hand){
        hands.add(hand);
    }

    public void setHands(Set<PlayerHands> hands){
        this.hands.addAll(hands);
    }

    public long getId(){
        return id;
    }

    public void deleteHands(){
        hands.clear();
        cards = null;
    }

    public ArrayList<Long> getOrder(){
        return order;
    }

    public void resetDeck(Deck d){
        this.cards = d;
    }


}
