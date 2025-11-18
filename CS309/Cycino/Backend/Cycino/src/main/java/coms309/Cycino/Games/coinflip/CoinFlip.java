package coms309.Cycino.Games.coinflip;

import coms309.Cycino.Games.Lobby.GameChat;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

public class CoinFlip {
    private static final String serverMessage = "#COINFLIP:";
    private static final Map<Long, CoinFlipGameState> gameStates = new HashMap<Long, CoinFlipGameState>();


    private static final GameChat gameChat = new GameChat();

    public CoinFlip() {}


    private void addNewGame(Long lobbyId, Collection<String> players){
        // If key is not in gameStates --> New game!
        if(!gameStates.containsKey(lobbyId)){
            gameStates.put(lobbyId, new CoinFlipGameState(players));
        }
    }
    public void gameAction(Long lobbyId, String player, String message){
        // Adds to mapping if game is new
        addNewGame(lobbyId, gameChat.getLobbyMembers(lobbyId));
        // retrieve correct gameState
        CoinFlipGameState gameState = gameStates.get(lobbyId);
        // use player and message to alter gamestate (let player make moves)
        String[] args = message.split(" ");
        String command = args[1];
        String commandArgument = args[2];
        if (command.equals("PICK")){
            gameState.setPlayerMove(player, commandArgument);
        } else if (command.equals("BET")){
            gameState.setPlayerBets(player, Integer.parseInt(commandArgument));
        }

        //gameChat.broadcast(lobbyId, serverMessage + " " + player + " " + command + " " + commandArgument);
        gameChat.broadcast(lobbyId, serverMessage + "\n" + gameState.toString());
        // Always check if you can flip the coin, this alters the gameState that is returned
        if (gameState.readyToFlip()){
            gameState.flip();
            gameChat.broadcast(lobbyId, serverMessage + "\n" + gameState.toString());
        }
    }
}
