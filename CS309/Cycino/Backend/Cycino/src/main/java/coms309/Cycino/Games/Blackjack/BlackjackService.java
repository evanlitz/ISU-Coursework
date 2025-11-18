package coms309.Cycino.Games.Blackjack;

import coms309.Cycino.Games.GameLogic.*;
import coms309.Cycino.Games.Lobby.GameChat;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.lobby.LobbyService;
import coms309.Cycino.stats.GameHistory;
import coms309.Cycino.stats.GameHistoryService;
import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class BlackjackService {
    @Autowired
    private HandsRepo repo;

    @Autowired
    private LobbyService lobbyService;
    @Autowired
    private BlackJackRepo blackJackRepo;
    @Autowired
    private UserService userService;
    @Autowired
    private DeckService ds;
    @Autowired
    private GameHistoryService histService;

    public HashSet<PlayerHands> saveRepo(Lobby l, BlackJack bj){
        HashSet<PlayerHands> hands = new HashSet<>();
        for (User player : l.getPlayers()) {
            PlayerHands hand = new PlayerHands(player, bj);
            hands.add(hand);
            repo.save(hand);
        }
        PlayerHands hand = new PlayerHands(bj);
        hands.add(hand);
        repo.save(hand);
        return hands;
    }

    public Map<String, Object> createGame(int decks, Long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = (Lobby) lobbyService.getLobby(lobbyId);
        Deck d = ds.start(decks);
        //Long i = histService.startGame("Blackjack", l.getPlayers());
        BlackJack blackJack = new BlackJack(l, d);
        blackJackRepo.save(blackJack);
        l.setGameId(blackJack.getId());
        blackJack.setHands(saveRepo(l, blackJack));
        blackJackRepo.save(blackJack);
        blackJack.setOrder();
        blackJackRepo.save(blackJack);
        response.put("status", "200 ok");
        response.put("blackjack", blackJackRepo.findById(blackJack.getId()));
        response.put("players", l.getPlayers().size());
        response.put("order", blackJack.getOrder());
        return response;
    }

    public Map<String, Object> deleteGame(Long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        for(PlayerHands hand: blj.getHands()){
            hand.setBlackJack(null);
        }
        repo.deleteAll(blj.getHands());
        ds.delete(blj.getCards());
        blj.deleteHands();
        blackJackRepo.save(blj);
        //histService.endGame(blj.getGameHist());
        blackJackRepo.delete(blj);
        lobbyService.updateGameId(null, l);
        response.put("status", "200 ok");
        return response;
    }

    public Map<String, Object> setBet(Long lobby, Long id, int bet){
        Map<String, Object> response = new HashMap<>();
        User user = userService.getUser(id);
        Lobby l = lobbyService.getLobby(lobby);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        if(user.getChips() < bet){
            response.put("status", 405);
            response.put("error", "not enough chips");
            return response;
        }
        user.addChips(-1 * bet);
        blj.getHand(user).addBet(bet);
        boolean bets = true;
        for(PlayerHands hand: blj.getHands()){
            if (hand.getPlayer() != null && hand.getBet() == 0) {
                System.out.println(hand.getBet());
                bets = false;
                break;
            }
        }
        if(bets){
            start(lobby);
            //GameChat.broadcast(l.getId(), "#Blackjack start next: " + blj.getOrder().get(0));
        }
        repo.save(blj.getHand(user));
        response.put("status", 200);
        return response;
    }

    public Map<String, Object> hit(Long lobbyId, Long id){
        Map<String, Object> response = new HashMap<>();
        User user = userService.getUser(id);
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response = BlackJackLogic.hit(blj, blj.getHand(user),blj.getCards());
        for(PlayerHands hand: blj.getHands()){
            repo.save(hand);
        }
        if(end(blj, id) && response.containsKey("string")){
            response.putAll(finish(lobbyId));
            String temp = (String) response.get("string");
            temp += " finish";
            response.put("string", temp);
        }
        if(response.containsKey("string"))
            GameChat.broadcast(lobbyId, (String) response.get("string"));
        else
            GameChat.broadcast(lobbyId, "#Blackjack");
        return response;
    }

    private boolean end(BlackJack blj, Long id){
        return Objects.equals(blj.getOrder().get(blj.getOrder().size() - 1), id);
    }

    public Map<String, Object> stand(Long lobbyId, Long id){
        User user = userService.getUser(id);
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response = BlackJackLogic.stand(blj.getHand(user), blj);
        if(end(blj, id) && response.containsKey("string")){
            response.putAll(finish(lobbyId));
            String temp = (String) response.get("string");
            temp += " finish";
            response.put("string", temp);
        }
        GameChat.broadcast(lobbyId, (String) response.get("string"));

        return response;
    }

    public Map<String, Object> dou(Long lobbyId, Long id){
        User user = userService.getUser(id);
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response = BlackJackLogic.doubleBJ(blj, blj.getHand(user),blj.getCards() ,user);
        for(PlayerHands hand: blj.getHands()){
            repo.save(hand);
        }
        if(end(blj, id) && response.containsKey("string")){
            response.putAll(finish(lobbyId));
            String temp = (String) response.get("string");
            temp += " finish";
            response.put("string", temp);

        }

        GameChat.broadcast(lobbyId, (String) response.get("string"));

        return response;
    }

    public Map<String, Object> split(Long lobbyId, Long id){
        User user = userService.getUser(id);
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response =  BlackJackLogic.split(blj.getHand(user), blj,user);
        if(response.containsValue("string")){
            GameChat.broadcast(lobbyId, (String) response.get("string"));
        }
        repo.save((PlayerHands) response.get("hand"));
        repo.save((PlayerHands) response.get("hand1"));
        blackJackRepo.save(blj);
        return response;
    }

    public Map<String, Object> getHand(Long lobbyId, Long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        User user = userService.getUser(id);
        if(blj.getHand(user) == null){
            response.put("status", "404 not found");
            response.put("error", "That user is not in this game");
            return response;
        }
        response.put("status", "200 ok");
        PlayerHands hand = blj.getHand(user);
        int i = 0;
        for(Card c: hand.getHand()){
            response.put("card" + (i + 1), hand.getHand().get(i));
            i++;
        }
        response.put("score", hand.getScore());
        return response;
    }

    public Map<String, Object> start(Long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack bj = blackJackRepo.findById(l.getId()).orElse(null);
        if(bj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        for(PlayerHands hands: bj.getHands()){
            if(hands.getPlayer() != null && hands.getBet() == 0.0){
                response.put("error", "not all players bet");
                response.put("status", 405);
                return response;
            }
        }
        BlackJackLogic.start(bj.getHands(), bj);
        for(PlayerHands hand: bj.getHands()){
            repo.save(hand);
        }
        response.put("status", "200 ok");
        GameChat.broadcast(lobbyId, "#Blackjack ,next: " + bj.getOrder().get(0));
        return response;
    }

    public Map<String, Object> getDealer(Long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack bj = blackJackRepo.findById(l.getId()).orElse(null);
        if(bj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        for(PlayerHands hand: bj.getHands()){
            if(hand.getPlayer() == null) {
                int i = 0;
                for(Card c: hand.getHand()){
                    response.put("card" + (i + 1), hand.getHand().get(i));
                    i++;
                }
                response.put("score", hand.getScore());
            }
        }
        return response;
    }

    public Map<String, Object> getHands(Long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response.put("status", "200 ok");
        Set<PlayerHands> hands = blj.getHands();
        for(PlayerHands hand: hands){
            if(hand.getPlayer() == null){
                response.put("dealer", hand.getHand());
                continue;
            }
            response.put(hand.getPlayer().getId() + "", hand.getHand());
        }
        return response;
    }

    public Map<String, Object> finish(long lobbyId){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobbyId);
        if(l == null){
            response.put("status", "404 not found");
            response.put("error", "no lobby with that id");
            return response;
        }
        BlackJack blj = blackJackRepo.findById(l.getId()).orElse(null);
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        response.put("status", "200 ok");
        PlayerHands playerHands = null;
        for(PlayerHands hand: blj.getHands()){
            if(hand.isDealer()) {
                playerHands = hand;
                break;
            }
        }
        while(playerHands.getScore() < 17){
            BlackJackLogic.hit(blj, playerHands, blj.getCards());
            repo.save(playerHands);
        }
        response.put("dealer", playerHands.getHand());
        response.put("dscore", playerHands.getScore());
        for(PlayerHands hand: blj.getHands()){
            if(hand == playerHands)
                continue;
            if(hand.getScore() > 21 || hand.getScore() < playerHands.getScore() && playerHands.getScore() <= 21)
                response.put(hand.getPlayer().getId() + "", "lose");
            else if(hand.getScore() > playerHands.getScore()) {
                response.put(hand.getPlayer().getId() + "", "win");
                response.put("won", hand.getBet());
                hand.getPlayer().addChips(hand.getBet() * 2);
            }
            else if(hand.getScore() == playerHands.getScore()) {
                response.put(hand.getPlayer().getId() + "", "push");
                hand.getPlayer().addChips(hand.getBet());
            }
        }
        if(response.containsValue("string")){
            GameChat.broadcast(lobbyId, "finish");
        }
        return response;
    }



}
