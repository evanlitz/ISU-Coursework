package coms309.Cycino.Games.poker;

import coms309.Cycino.Enums;
import coms309.Cycino.Games.GameLogic.Card;
import coms309.Cycino.Games.GameLogic.PlayerHands;

import java.util.*;

public class Evaluator {

    public static double evaluate(PlayerHands hands){
        Map<String,Object> flush = checkFlush(hands);
        Map<String, Object> straight = straight(hands);
        Map<String, Object> multi = checkMult(hands);

        Set<Double> v = new HashSet<>();
        if(straight.get("value") != null)
            v.add((double) straight.get("value"));
        if(multi.get("value") != null)
            v.add((double) multi.get("value"));
        if(flush.get("value") != null)
            v.add((double) flush.get("value"));

        double high = 0;
        for(double d: v){
            if(d > high){
                high = d;
            }
        }

        if(high == 0)
            return getHigh(hands).getValue()/100.0;
        return high;

    }

//    private Map<String, Object> checkRoyal(PlayerHands hands){
//        Map<String, Object> response = new HashMap<>();
//        for(Enums.SUIT suit: Enums.SUIT.values()){
//            for(Enums.VALUE value: Enums.VALUE.values()){
//                Card temp = new Card(value.toString(), suit, null);
//                if(hands.contains(temp)){
//                    if(value == Enums.VALUE.ACE && hands.contains(new Card("10", suit, null))){
//                        PlayerHands tempHand = new PlayerHands();
//                        tempHand.add(new Card("10", suit, null));
//                        tempHand.add(temp);
//                        for(int i = 0; i < 3; i++){
//                            tempHand.add(new Card(Enums.VALUE.values()[i].toString(), suit, null));
//                        }
//                        response.put("hand", tempHand);
//                        response.put("value", 10);
//                        break;
//                    }
//                    continue;
//                }
//                break;
//            }
//        }
//        return response;
//    }

    private static Map<String, Object> checkFlush(PlayerHands hands){
        ArrayList<Card> hearts = new ArrayList<>();
        ArrayList<Card> diamonds = new ArrayList<>();
        ArrayList<Card> clubs = new ArrayList<>();
        ArrayList<Card> spades = new ArrayList<>();
        Map<String, Object> response = new HashMap<>();
        for(Card c: hands.getHand()){
            switch(c.getSuit().toString()){
                case "HEARTS": hearts.add(c);
                break;
                case "DIAMONDS": diamonds.add(c);
                break;
                case "CLUBS": clubs.add(c);
                break;
                case "SPADES": spades.add(c);
                break;
            }
        }

        if(hearts.size() >= 5){
            response = simplify(hearts);
        } else if(clubs.size() >= 5){
            response = simplify(clubs);
        } else if(spades.size() >= 5){
            response = simplify(spades);
        } else if(diamonds.size() >= 5){
            response = simplify(diamonds);
        }
        if(!response.isEmpty())
            response.put("value", 6 + getHigh((PlayerHands) response.get("hand")).getValue()/100.0);
        return response;
    }

    private static Map<String, Object> simplify(ArrayList<Card> cards){
        Map<String, Object> response = new HashMap<>();
        while(cards.size() > 5){
            Card smallest = cards.get(0);
            for(Card c: cards){
                if(c.getValue() < smallest.getValue())
                    smallest = c;
            }
            cards.remove(smallest);
        }
        PlayerHands temp = new PlayerHands();
        temp.addAll(cards);
        response.put("hand", temp);
        return response;
    }

    private static Map<String, Object> straight(PlayerHands hand){
        Map<String, Object> response = new HashMap<>();
        for(Card c: hand.getHand()){
            PlayerHands temp = new PlayerHands();
            int start = c.getValue();
            for(int i = start; i < start + 5; i++){
                Card card = hand.containsValue(i);
                if(card != null){
                    temp.add(card);
                    continue;
                }
                break;
            }
            if(temp.getHand().size() >= 5){
                response.put("hand", temp);
            }
        }
        if(!response.isEmpty()) {
            PlayerHands flush = (PlayerHands) checkFlush((PlayerHands) response.get("hand")).get("hand");
            if(flush != null) {
                response.put("hand", flush);
                response.put("value", 9 + getHigh(flush).getValue()/100.0);
            }
            else{
                PlayerHands fin = (PlayerHands) simplify(((PlayerHands) response.get("hand")).getHand()).get("hand");
                response.put("hand", fin);
                response.put("value", 5 + getHigh(fin).getValue()/100.0);
            }
        }
        return response;
    }

    private static Card getHigh(PlayerHands hand){
        Card high = hand.getHand().get(0);
        for(Card c: hand.getHand()){
            if(c.getValue() > high.getValue())
                high = c;
        }
        return high;
    }

    private static Map<String, Object> checkMult(PlayerHands hand){
        Map<String, Object> response = new HashMap<>();
        Map<Integer, Integer> values = new HashMap<>();
        for(Card c: hand.getHand()){
            int count = 0;
            for(Card c2: hand.getHand()){
                if(c.getValue() == c2.getValue()){
                    count++;
                }
            }
            if(count > 1)
                values.put(c.getValue(), count);
        }
        if(values.isEmpty()){
            return response;
        }

        if(values.containsValue(2)){
            //values.values().remove(2);
            if(values.containsValue(3)){
                response.put("name", "Full House");
                response.put("value", 7);
            } else if(Collections.frequency(values.values(), 2) >= 2){
                response.put("name", "Two Pair");
                response.put("value", 2);
            } else {
                response.put("name", "Pair");
                response.put("value", 1);
            }
        } else if(values.containsValue(3)){
            response.put("name", "Three of a Kind");
            response.put("value", 3);
        }
        if(values.containsValue(4)){
            response.put("name", "Four of a kind");
            response.put("value", 8);
        }

        response.put("value", addDec((int) response.get("value"), values));
        return response;
    }

    private static Double addDec(int d, Map<Integer, Integer> values){
        int high = 0;
        for(Integer i: values.keySet()){
            if(i > high)
                high = i;
        }
        return d + high/100.0;

    }

}
