package coms309.Cycino.Games.poker;

import coms309.Cycino.Games.Blackjack.BlackJack;
import coms309.Cycino.Games.GameLogic.*;
import coms309.Cycino.Games.Lobby.GameChat;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.lobby.LobbyService;
import coms309.Cycino.users.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.*;

@Service
public class PokerService {

    @Autowired
    private LobbyService lobbyService;
    @Autowired
    private DeckService deckService;
    @Autowired
    private PokerRepo repo;
    @Autowired
    private HandsRepo handsRepo;

    public Map<String, Object> createPoker(Long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = (Lobby) lobbyService.getLobby(id);
        Poker p = new Poker(l, deckService.start(1));
        repo.save(p);
        lobbyService.updateGameId(p.getId(), l);
        p.setHands(saveRepo(l, p));
        repo.save(p);
        p.setOrder();
        repo.save(p);
        response.put("id", p.getId());
        return response;
    }

    public HashSet<PlayerHands> saveRepo(Lobby l, Poker p){
        HashSet<PlayerHands> hands = new HashSet<>();
        for (User player : l.getPlayers()) {
            PlayerHands hand = new PlayerHands(player, p);
            hands.add(hand);
            handsRepo.save(hand);
        }
        PlayerHands hand = new PlayerHands(p);
        hands.add(hand);
        handsRepo.save(hand);
        return hands;
    }

    public Map<String, Object> getEval(long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = (Lobby) lobbyService.getLobby(id);
        Poker p = repo.findById(id).orElse(null);
        assert p != null;
        Map<PlayerHands, String> evalHands = PokerLogic.finishHand(p);
        for(PlayerHands hand: evalHands.keySet()){
            response.put(hand.getPlayer().getId() + "", evalHands.get(hand));
        }
        response.put("status", "200 ok");
        return response;
    }

    public Map<String, Object> startGame(long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = (Lobby) lobbyService.getLobby(id);
        Poker p = repo.findById(l.getId()).orElse(null);
        PlayerHands dealer = null;
        for(int i = 0; i < 2; i++){
            assert p != null;
            for(PlayerHands hand: p.getHands()){
                if(hand.getPlayer() == null){
                    dealer = hand;
                    continue;
                }
                hand.getPlayer().addChips(-25);
                hand.addBet(25);
                p.increasePot(25);
                Card c = p.getCards().draw();
                hand.add(c);
            }
        }
        for(int i = 0; i < 3; i ++){
            Card c = p.getCards().draw();

            assert dealer != null;
            dealer.add(c);
        }
        for(PlayerHands hands: p.getHands()){
            handsRepo.save(hands);
        }
        response.put("status", "200 ok");
        response.putAll(getHands(id));
        GameChat.broadcast(id, "#Poker next: " + p.getOrder().get(0));
        return response;
    }

    public Map<String, Object> getHands(long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(id);
        Poker p = repo.findById(l.getId()).orElse(null);
        assert p != null;
        for(PlayerHands hand: p.getHands()){
            if(hand.getPlayer() == null){
                response.put("dealer", hand.getHand());
                continue;
            }
            response.put(hand.getPlayer().getId() + "", hand.getHand());
        }
        response.put("status", "200 ok");
        return response;
    }

    public Map<String, Object> finish(long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(id);
        Poker p = repo.findById(l.getId()).orElse(null);
        assert p != null;
        PlayerHands d = null;
        for(PlayerHands hand: p.getHands()){
            if(hand.getPlayer() == null)
                d = hand;

        }
        while(d.getHand().size() < 5){
            d.add(p.getCards().draw());
        }
        Map<PlayerHands, String> winners = PokerLogic.finishHand(p);
        for(PlayerHands hand: winners.keySet()){
            if(hand.getPlayer() == null){
                continue;
            }
            response.put(hand.getPlayer().getId()+ "", winners.get(hand));
        }
        return response;
    }

    public Map<String, Object> fold(long lobby, long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobby);
        Poker p = repo.findById(l.getId()).orElse(null);
        User u = null;
        for(User user: l.getPlayers()){
            if(user.getId() == id){
                u = user;
                break;
            }
        }
        if(u == null){
            response.put("error", "no user found");
            response.put("status", 404);
            return response;
        }
        assert p != null;
        p.fold(id);
        response.put("message", message(p, id));
        if(((String)(response.get("message"))).contains("finish: true")){
            Map<String, Object> temp = finish(lobby);
            temp.putAll(response);
            GameChat.broadcast(lobby, (String) response.get("message"));
            return temp;
        } else if(((String)(response.get("message"))).contains("update: true")){
            nextRound(id, p);
        }
        GameChat.broadcast(lobby, (String) response.get("message"));
        return response;
    }

    public Map<String, Object> call(long lobby, long id){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobby);
        Poker p = repo.findById(l.getId()).orElse(null);
        User u = null;
        for(User user: l.getPlayers()){
            if(user.getId() == id){
                u = user;
                break;
            }
        }
        if(u == null){
            response.put("error", "no user found");
            response.put("status", 404);
            return response;
        }
        assert p != null;
        if(p.getLastBet() != 0) {
            if (u.getChips() < p.getLastBet()) {
                response.put("error", "not enough chips");
                response.put("status", 405);
                return response;
            }
            u.addChips(-1 * p.getLastBet());
        }
        response.put("message", message(p, id));
        if(((String)(response.get("message"))).contains("finish: true")){
            Map<String, Object> temp = finish(lobby);
            temp.putAll(response);
            GameChat.broadcast(lobby, (String) response.get("message"));
            return temp;
        } else if(((String)(response.get("message"))).contains("update: true")){
            nextRound(id, p);
        }
        GameChat.broadcast(lobby, (String) response.get("message"));
        return response;
    }

    public Map<String, Object> raise(long lobby, long id, int raise){
        Map<String, Object> response = new HashMap<>();
        Lobby l = lobbyService.getLobby(lobby);
        Poker p = repo.findById(l.getId()).orElse(null);
        User u = null;
        for(User user: l.getPlayers()){
            if(user.getId() == id){
                u = user;
                break;
            }
        }
        if(u == null){
            response.put("error", "no user found");
            response.put("status", 404);
            return response;
        }
        assert p != null;
        if(u.getChips() < raise){
            response.put("status", 500);
            response.put("error", "not enough chips");
            return response;
        }
        p.increasePot(raise);
        p.setLastBet(raise);
        response.put("message", message(p, id));
        if(((String)(response.get("message"))).contains("finish: true")){
            Map<String, Object> temp = finish(lobby);
            temp.putAll(response);
            GameChat.broadcast(lobby, (String) response.get("message"));
            return temp;
        } else if(((String)(response.get("message"))).contains("update: true")){
            String message = (String) response.get("message");
            int i = message.indexOf("update: true");
            message = message.substring(0, i) + message.substring(i + 12) + ", raise: " + raise;
            response.put("message", message);
        } else {
            String message = (String) response.get("message");
            message +=  ", raise: " + raise;
            response.put("message", message);
        }
        GameChat.broadcast(lobby, (String) response.get("message"));
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
        Poker blj = null;
        try {
            blj = repo.findById(l.getId()).orElse(null);
        } catch(Exception e){
            response.put("status", 404);
            return response;
        }
        if(blj == null){
            response.put("status", "404 not found");
            response.put("error", "game not started yet");
            return response;
        }
        for(PlayerHands hand: blj.getHands()){
            hand.setBlackJack(null);
        }
        handsRepo.deleteAll(blj.getHands());
        deckService.delete(blj.getCards());
        blj.deleteHands();
        repo.save(blj);
        //histService.endGame(blj.getGameHist());
        repo.delete(blj);
        lobbyService.updateGameId(null, l);
        response.put("status", "200 ok");
        return response;
    }

    private void nextRound(long id, Poker p){
        PlayerHands dealer = null;
        for(PlayerHands hand: p.getHands()){
            if(hand.getPlayer() == null) {
                dealer = hand;
                break;
            }
        }
        assert dealer != null;
        if(dealer.getHand().size() == 5){
           Map<String, Object> response = finish(id);
           String message = "#Poker winners: ";
           for(String s: response.keySet()){
               message += s + " ";
           }
           message += "finish";
           GameChat.broadcast(id, message);
           return;
        }
        dealer.add(p.getCards().draw());
        p.setLastBet(0);
        handsRepo.save(dealer);
    }

    public Map<String, Object> reset(long lobby){
        Lobby l = lobbyService.getLobby(lobby);
        Poker poker = repo.findById(l.getId()).orElse(null);
        assert poker != null;
        for(PlayerHands hand: poker.getHands()){
            hand.reset();
        }
        handsRepo.saveAll(poker.getHands());
        poker.reset();
        poker.resetDeck(deckService.start(1));
        return startGame(lobby);
    }

    private String message(Poker p, long id){
        ArrayList<Long> order = p.getOrder();
        int f = order.indexOf(id);
        long next = getnext(p, f);
        PlayerHands dealer = null;
        for(PlayerHands hands: p.getHands()){
            if(hands.getPlayer() == null){
                dealer = hands;
                break;
            }
        }
        if(f == order.size() - 1){
            if(dealer.getHand().size() >= 5)
                return "#Poker finish";
            return "#Poker update: true, next: " + next;
        }
        if(next == -1){
            return "#Poker finish";
        }
        else if(next == 0){
            return "#Poker finish: true";
        }
        return "#Poker next: " + next;
    }

    private long getnext(Poker p, int after){

        ArrayList<Long> order = p.getOrder();
        Set<Long> folded = p.getFolded();
        for(int i = after + 1; i < order.size(); i++){
            if(!folded.contains(order.get(i)))
                return order.get(i);
        }
        order.removeAll(folded);
        if(order.size() <= 1)
            return -1;
        return 0;
    }
}
