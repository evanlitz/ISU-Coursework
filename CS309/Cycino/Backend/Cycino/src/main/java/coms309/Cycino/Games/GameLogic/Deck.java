package coms309.Cycino.Games.GameLogic;

import coms309.Cycino.Enums;
import coms309.Cycino.Games.Blackjack.BlackJack;
import jakarta.persistence.*;

import java.util.*;

@Entity
public class Deck {


    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "deck", cascade = CascadeType.REMOVE, orphanRemoval = true)
    private Set<Card> cards = new HashSet<>();

    @OneToOne
    private BlackJack blackJack;

    public Deck(){

    }

    public Set<Card> getCards(){
        return cards;
    }

    public ArrayList<Card> shuffle(){
        ArrayList<Card> cardList = new ArrayList<>(cards);
        Collections.shuffle(cardList);
        return cardList;
    }

    public void resetDeck(){
        cards.removeAll(cards);
    }

    public void addCard(Card c){
        cards.add(c);
    }

    public Card draw(){
        if(cards.isEmpty()){
            return null;
        }
        ArrayList<Card> cards = shuffle();
        Card c = (Card) cards.remove(0);
        Collections.shuffle(cards);
        this.cards.remove(c);
        return c;
    }

    public void setBlackJack(BlackJack blackJack){
        this.blackJack = blackJack;
    }

}
