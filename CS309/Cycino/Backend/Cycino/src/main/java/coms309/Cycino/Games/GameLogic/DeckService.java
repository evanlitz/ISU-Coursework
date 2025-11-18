package coms309.Cycino.Games.GameLogic;

import coms309.Cycino.Enums;
import coms309.Cycino.Games.Blackjack.BlackJack;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Set;

@Service
public class DeckService {

    @Autowired
    private CardRepo repo;

    @Autowired
    private DeckRepo deckRepo;

    public Deck start(int decks){
        Deck d = new Deck();
        //d.resetDeck();
        deckRepo.save(d);
        for(int i = 0; i < decks; i++){
           fill(d);
        }
        deckRepo.save(d);
        return d;
    }

    public void saveBlackJack(BlackJack bj, Deck d){
        d.setBlackJack(bj);
        deckRepo.save(d);
    }

    private ArrayList<Card> fill(Deck deck){
        ArrayList<Card> list = new ArrayList<>();
        for(int i = 0; i < 4; i++){
            for(int j = 2; j < 11; j++){
                Card c = new Card(j + "", Enums.SUIT.values()[i], deck);
                list.add(c);
                repo.save(c);
                deck.addCard(c);

            }
            for(int j = 0; j < 4; j++){
                Card c = new Card(Enums.VALUE.values()[j].toString(), Enums.SUIT.values()[i], deck);
                list.add(c);
                repo.save(c);
                deck.addCard(c);
            }
        }
        return list;
    }


    public void delete(Deck d){
        for (Card card : d.getCards()) {
        card.setDeck(null);
    }


        repo.deleteAll(d.getCards());


        d.getCards().clear();
        deckRepo.save(d);

        deckRepo.delete(d);
    }
}
