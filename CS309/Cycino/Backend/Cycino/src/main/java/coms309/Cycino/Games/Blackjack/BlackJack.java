package coms309.Cycino.Games.Blackjack;

import coms309.Cycino.Games.Game;
import coms309.Cycino.Games.GameLogic.Deck;
import coms309.Cycino.Games.GameLogic.HandsRepo;
import coms309.Cycino.Games.GameLogic.PlayerHands;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.users.User;
import jakarta.persistence.*;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

@Entity
public class BlackJack extends Game {

    // private Long gameHist;

    public BlackJack(){

    }

    public BlackJack(Lobby l, Deck d){
        super(l,d);
        //this.gameHist = gameHist;

    }

//    public Long getGameHist(){
//        return gameHist;
//    }
}
