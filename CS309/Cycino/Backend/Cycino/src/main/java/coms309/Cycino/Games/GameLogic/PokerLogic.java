package coms309.Cycino.Games.GameLogic;

import coms309.Cycino.Games.poker.Evaluator;
import coms309.Cycino.Games.poker.Poker;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class PokerLogic {

    public static Map<PlayerHands, String> finishHand(Poker poker){
        Map<String, Object> response = new HashMap<>();
        PlayerHands table = null;
        for(PlayerHands hand: poker.getHands()){
            if(hand.getPlayer() == null) {
                table = hand;
            }
        }
        Map<PlayerHands, Double> temp = new HashMap<>();
        Map<PlayerHands, String> winners = new HashMap<>();
        for(PlayerHands hand: poker.getHands()){
            assert table != null;
            hand.addAll(table.getHand());
            double score = Evaluator.evaluate(hand);
            temp.put(hand, score);
        }
        double high = 0;
        for(double d: temp.values()){
            if(d > high)
                high = d;
        }
        for(PlayerHands hand: temp.keySet()){
            if(temp.get(hand) == high){
                winners.put(hand, getName(high));
            }
        }
        for(PlayerHands hand: winners.keySet()){
            if(hand.getPlayer() != null)
                hand.getPlayer().addChips(poker.getPot() / winners.size());
        }
        return winners;
    }

    private static String getName(double d){
        if(d == 9.13)
            return "Royal Flush";
        return switch ((int) d) {
            case 0 -> "Nothing";
            case 1 -> "Pair";
            case 2 -> "Two Pair";
            case 3 -> "Three of a Kind";
            case 5 -> "Straight";
            case 6 -> "Flush";
            case 7 -> "Full House";
            case 8 -> "Four of a Kind";
            case 9 -> "Straight FLush";
            default -> "error";
        };
    }
}
