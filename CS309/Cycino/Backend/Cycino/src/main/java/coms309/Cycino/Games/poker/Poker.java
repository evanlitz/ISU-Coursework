package coms309.Cycino.Games.poker;

import coms309.Cycino.Games.Game;
import coms309.Cycino.Games.GameLogic.Deck;
import coms309.Cycino.Games.GameLogic.PlayerHands;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.users.User;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

@Entity
public class Poker extends Game {

    private double pot = 0;

    private int lastBet = 0;

    private Set<Long> folded = new HashSet<>();

    public Poker(){
    }

    public Poker(Lobby l, Deck d){
        super(l,d);
    }

    public void increasePot(double raise){
        pot += raise;
    }

    public double getPot(){
        return pot;
    }

    public void setLastBet(int bet){
        lastBet = bet;
    }

    public double getLastBet(){
        return lastBet;
    }

    public Set<Long> getFolded(){
        return folded;
    }

    public Set<Long> getIn(){
        Set<Long> temp = new HashSet<>();
        for(PlayerHands hand: getHands()){
            if(!folded.contains(hand.getPlayer().getId())){
                temp.add(hand.getPlayer().getId());
            }
        }
        return temp;
    }

    public void fold(long user){
        folded.add(user);
    }

    public void reset(){
        folded.removeAll(folded);
        lastBet = 0;
        pot = 0;
    }

}
