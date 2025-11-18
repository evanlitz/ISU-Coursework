package coms309.Cycino.Games.coinflip;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class CoinFlipGameState {
    private Map<String, String> playerMoves = new HashMap<>();
    private Map<String, Integer> playerBets = new HashMap<>();
    private String coin = "NONE";
    private boolean gameOver = false;

    public CoinFlipGameState(Collection<String> players) {
        for (String player : players) {
            this.playerMoves.put(player, "UNDECIDED");
            this.playerBets.put(player, 0);
        }
    }

    public void setPlayerBets(String player, int bet) {
        playerBets.put(player, bet);
    }

    public void setPlayerMove(String player, String move) {
        playerMoves.put(player, move);
    }

    public boolean readyToFlip(){
        boolean responseMoves = true;
        Collection<String> moves = playerMoves.values();
        for (String move : moves) {
            if (move.equals("UNDECIDED")) {
                responseMoves = false;
            }
        }
        boolean responseBets = true;
        Collection<Integer> bets = playerBets.values();
        for (Integer bet : bets) {
            if (bet == 0){
                responseBets = false;
            }
        }
        return responseMoves && responseBets;
    }

    public void flip(){
        if (readyToFlip()) {
            Random random = new Random();
            int randomNumber = random.nextInt(2);
            if (randomNumber == 0) {
                coin = "HEADS";
            } else if (randomNumber == 1) {
                coin = "TAILS";
            }
            updateState();
        }
    }

    private void updateState(){
        playerMoves.forEach((player, move) -> {
            if (move.equals(coin)) {
                playerMoves.put(player, "IN");
            } else{
                playerMoves.put(player, "LOST");
            }
        });
        checkWinner();
    }

    private void checkWinner(){
        int standingPlayers = 0;
        Collection<String> moves = playerMoves.values();
        for (String move : moves) {
            if (move.equals("IN")) {
                standingPlayers++;
            }
        }
        if (standingPlayers == 1) {
            gameOver = true;
            playerMoves.forEach((player, move) -> {
                if (move.equals("IN")) {
                    playerMoves.put(player, "WIN");
                }
            });
        } else if (standingPlayers == 0){
            gameOver = true;
            /*
            playerMoves.forEach((player, move) -> {
                playerMoves.put(player, "UNDECIDED");
            });
            */
        } else {
            playerMoves.forEach((player, move) -> {
                if (move.equals("IN")) {
                    playerMoves.put(player, "UNDECIDED");
                }
            });
        }
    }

    private void changeChipCount(String player, int betAmount, boolean win){
        if (win){
            playerBets.put(player, betAmount);
        } else {
            playerBets.put(player, betAmount * -1);
        }
    }

    private void resetState(){
        playerMoves.forEach((player, move) -> {
            playerMoves.put(player, "UNDECIDED");
        });
        playerBets.forEach((player, bet) -> {
            playerBets.put(player, 0);
        });
        this.coin = "NONE";
        this.gameOver = false;
    }

    @Override
    public String toString() {
        String gameState = "";
        gameState += "\n" + "COIN: " + coin;
        gameState += "\n";
        gameState += "CALLS: ";
        for(Map.Entry<String, String> entry : playerMoves.entrySet()) {
            gameState += entry.getKey() + " " + entry.getValue() + ", ";
        }
        gameState = gameState.trim();
        gameState = gameState.substring(0, gameState.length()-1);
        gameState += "\n";
        gameState += "BETS: ";
        if (gameOver){
            playerMoves.forEach((player, move) -> {
                if (move.equals("WIN")) {
                    // Add betted money
                    changeChipCount(player, playerBets.get(player), true);
                } else if (move.equals("LOST")) {
                    // Withdraw betted money
                    changeChipCount(player, playerBets.get(player), false);
                }
            });
        }
        for(Map.Entry<String, Integer> entry : playerBets.entrySet()) {
            gameState += entry.getKey() + " " + entry.getValue() + ", ";
        }
        gameState = gameState.trim();
        gameState = gameState.substring(0, gameState.length()-1);
        gameState += "\n" + "GAME: ";
        if (gameOver){
            gameState +=  "OVER";
            /*
            for(Map.Entry<String, String> entry : playerMoves.entrySet()) {
                if (entry.getValue().equals("WIN")) {
                    gameState += " " + entry.getKey() + " " + entry.getValue();
                }
            }
            */
            resetState();
        }
        else{
            gameState += "ONGOING";
            /*
            for(Map.Entry<String, String> entry : playerMoves.entrySet()) {
                gameState += " " + entry.getKey() + " " + entry.getValue();
            }
            */
        }
        return gameState;
    }
}
