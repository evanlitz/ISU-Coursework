package coms309.Cycino.Games.GameLogic;

import coms309.Cycino.Games.Blackjack.BlackJack;
import coms309.Cycino.Games.Lobby.GameChat;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.users.User;

import java.lang.reflect.Array;
import java.util.*;

public class BlackJackLogic {

    public static Map<String, Object> hit(BlackJack b, PlayerHands hand, Deck cards){
        Map<String, Object> result = new HashMap<>();
        int score = hand.getScore();
        hand.split(false);

        if(score >= 21){
            result.put("error", "cannot hit. score >= 21");
            return result;
        }
        Card c = cards.draw();
        score = checkAce(hand.getHand(), score, c);
        hand.add(c);
        result.put("card", c);
        result.put("score", hand.getScore());
        if(score > 21){
            result.put("result", "bust");
            if(hand.getPlayer() != null)
                result.put("string", createMessage(b, hand, "hit", c));
            return result;
        }

        if(score == 21){
            result.put("result", "blackjack");
            if(hand.getPlayer() != null)
                result.put("string", createMessage(b, hand, "hit", c));
            return result;
        }
        return result;
    }

    public static void start(Set<PlayerHands> hands, BlackJack black){
        for(int i = 0; i < 2; i ++){
            for(PlayerHands hand: hands){
                Card c = black.getCards().draw();
                c.setDeck(null);
                checkAce(hand.getHand(), hand.getScore(), c);
                hand.add(c);

                //c.setPlayerHand(hand);
            }
        }
        for(PlayerHands hand: hands){
            if(hand.getPlayer() == null)
                continue;
            checkSplit(hand);
            if(hand.getScore() == 21)
                hand.getPlayer().addChips(hand.getBet() * 0.5);
        }
    }


    public static void checkSplit(PlayerHands hand){
        if(hand.getHand().size() == 2 && hand.getHand().get(0).getValue1() == hand.getHand().get(1).getValue1()){
            hand.split(true);
        }
    }

    private static int checkAce(ArrayList<Card> hand, int score, Card c){
        if(c.getNumber().equals("ACE")){
            if(score <= 10)
                return score + 11;
            c.setNumber(1);
            return score + 1;
        }

        if(score + c.getValue1() > 21){
            for(Card card: hand){
                if(card.getNumber().equals("ACE") && card.getValue1() != 1){
                    card.setNumber(1);
                    score -= 10;
                    break;
                }
            }
        }

        return score + c.getValue1();
    }

    public static Map<String, Object> stand(PlayerHands hand, BlackJack b){
        Map<String, Object> response = new HashMap<>();
        hand.stand();
        response.put("status", "200 ok");
        response.put("hand", hand);
        response.put("score", hand.getScore());
        if(hand.getScore() > 21)
            response.put("bust", true);
        else response.put("bust", false);
        response.put("string", createMessage(b, hand, "stand", null));

        return response;
    }

    public static Map<String, Object> doubleBJ(BlackJack b,PlayerHands hand, Deck deck, User user){
        Map<String, Object> response = new HashMap<>();
        if(hand.getBet() > user.getChips()){
            response.put("status", "500");
            response.put("error", "not enough chips");
            return response;
        }
        user.addChips(-(hand.getBet()));
        hand.addBet(hand.getBet());
        Card c = deck.draw();
        hand.add(c);
        response = check(hand);
        response.put("card", c);
        hand.stand();
        response.put("string", createMessage(b, hand, "double", c));
        return response;
    }

    public static Map<String, Object> split(PlayerHands hand, BlackJack blackJack, User user){
        Map<String, Object> response = new HashMap<>();
        if(!hand.getSplit()){
            response.put("status", "500");
            response.put("error", "cannot split");
            return response;
        }
        if(hand.getBet() > user.getChips()){
            response.put("status", "500");
            response.put("error", "not enough chips");
            return response;
        }
        PlayerHands temp = new PlayerHands(hand.getPlayer(), blackJack);
        temp.add(hand.splitHand());
        blackJack.addHand(temp);
        hand.split(false);
        response.put("hand", hand);
        response.put("hand1", temp);
        response.put("status", "200 ok");
        return response;
    }

    private static Map<String, Object> check(PlayerHands hand){
        Map<String, Object> response = new HashMap<>();
        response.put("status", "200 ok");
        if(hand.getScore() > 21){
            response.put("bust", true);
        } else response.put("bust", false);
        response.put("score", hand.getScore());
        return response;
    }

    private static String createMessage(BlackJack b, PlayerHands hand, String action, Card c){
        User user = hand.getPlayer();
        String result = "#Blackjack User: ";
        result += user.getId() + " img: ";
        if(c != null)
            result += c.img() + " action: ";
        else
            result += " action: ";
        result += action;
        result += ",update";
        if(Objects.equals(action, "stand") || hand.getScore() >= 21) {
            int index = b.getOrder().indexOf(user.getId());
            if (index + 1 >= b.getOrder().size()) {
                result += ",finish";
            } else {
                result += ",next: " + b.getOrder().get(index + 1);
            }
        }
        return result;
    }
}
