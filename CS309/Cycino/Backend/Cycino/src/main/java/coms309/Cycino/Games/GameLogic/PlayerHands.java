package coms309.Cycino.Games.GameLogic;

import coms309.Cycino.Games.Game;
import coms309.Cycino.users.User;
import jakarta.persistence.*;

import java.io.Serializable;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

@Entity
public class PlayerHands implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @ManyToOne(optional = true)
    @JoinColumn(name = "hand_id", nullable = true)
    private User player;
    @OneToMany
    private final Set<Card> hand;
    private final ArrayList<String> ordered;
    private int score;
    private boolean stand = false;
    private int bet;
    private boolean split = false;
    private boolean dealer = false;

    @ManyToOne(optional = true) // Allow null
    @JoinColumn(name = "game_id", nullable = true) // Allow null in the database
    private Game game;



    public PlayerHands(){
        hand = new HashSet<>();
        ordered = new ArrayList<>();
    }
    public PlayerHands(User player, Game game){
        this.player = player;
        this.game = game;
        hand = new HashSet<>();
        ordered = new ArrayList<>();
    }

    public PlayerHands(Game b){
        this.game = b;
        hand = new HashSet<>();
        ordered = new ArrayList<>();
        dealer = true;
    }

    public void setBlackJack(Game bj){
        game = bj;
    }

    public int getScore(){
        score = 0;
        for(Card c: hand){
            if(c.getValue() >= 10){
                score += 10;
                continue;
            }
            score += c.getValue();
        }
        return score;
    }

    public ArrayList<Card> getHand(){
        ArrayList<Card> c = new ArrayList<>();
        while(c.size() < hand.size()){
            for(Card card : hand){
                if(c.size() < hand.size() && card.img().equals(ordered.get(c.size()))){
                    c.add(card);
                }
            }
        }
        return c;
    }

    public void add(Card c){
        ordered.add(c.img());
        hand.add(c);
    }

    public User getPlayer(){
        return player;
    }

    public void flip(){
        stand = true;
    }

    public boolean stand(){
        return stand;
    }

    public void addBet(int bet){
        this.bet = bet;
    }

    public int getBet(){
        return bet;
    }

    public void split(boolean split){
        this.split = split;
    }

    public boolean getSplit(){
        return split;
    }

    public Card splitHand(){
        ArrayList<Card> hand = new ArrayList<>(this.hand);
        Card c = hand.remove(1);
        ordered.remove(c.img());
        this.hand.remove(c);
        return c;
    }

    public boolean isDealer(){
        return dealer;
    }

    public boolean contains(Card c){
        for(Card card: hand){
            if(card.equals(c))
                return true;
        }
        return false;
    }

    public void addAll(Collection<Card> cards){
        hand.addAll(cards);
        cards.forEach(card -> ordered.add(card.img()));
    }

    public void reset(){
        hand.removeAll(hand);
        ordered.removeAll(ordered);
        score = 0;
        bet = 0;
        split = false;
    }

    public Card containsValue(int i){
        for(Card c: hand){
            if(c.getValue() == i)
                return c;
        }
        return null;
    }
}
