package coms309.Cycino;


import com.fasterxml.jackson.databind.ObjectMapper;
import coms309.Cycino.Games.GameLogic.Card;
import coms309.Cycino.Games.GameLogic.PlayerHands;
import coms309.Cycino.Games.baccarat.BaccaratCard;
import coms309.Cycino.Games.baccarat.BaccaratGameState;
import coms309.Cycino.Games.coinflip.CoinFlipGameState;
import coms309.Cycino.Games.poker.Evaluator;
import coms309.Cycino.users.User;
import coms309.Cycino.users.UsersRepository;
import io.restassured.RestAssured;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.RequestBuilder;

import java.util.*;

import static net.bytebuddy.matcher.ElementMatchers.is;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;


@RunWith(SpringRunner.class)
@AutoConfigureMockMvc
@SpringBootTest(classes = CycinoApplication.class, properties = "spring.profiles.active=test", webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class FilipSystemTest {

    @Autowired
    private MockMvc controller;
    @LocalServerPort
    int port;
    @Autowired
    private UsersRepository repo;

    @Before
    public void setUp() {
        RestAssured.port = port;
        RestAssured.baseURI = "http://localhost";
    }

    @Test
    public void testHandValue() throws Exception {
        ArrayList<BaccaratCard> cards = new ArrayList<>();
        cards.add(new BaccaratCard("ace", "hearts", 1));
        cards.add(new BaccaratCard("8", "hearts", 8));

        Collection<String> players = new ArrayList<>();
        players.add("player1");
        BaccaratGameState baccaratGameState = new BaccaratGameState(players);

        Assert.assertEquals(baccaratGameState.handValue(cards), 9);
    }

    @Test
    public void testHandValueWithFacecards() throws Exception {
        ArrayList<BaccaratCard> cards = new ArrayList<>();
        cards.add(new BaccaratCard("king", "hearts", 13));
        cards.add(new BaccaratCard("queen", "hearts", 12));
        cards.add(new BaccaratCard("jack", "hearts", 11));

        Collection<String> players = new ArrayList<>();
        players.add("player1");
        BaccaratGameState baccaratGameState = new BaccaratGameState(players);

        Assert.assertEquals(baccaratGameState.handValue(cards), 0);
    }

    @Test
    public void testCoinFlipGameState() throws Exception {
        Collection<String> players = new ArrayList<>();
        players.add("player1");
        players.add("player2");
        CoinFlipGameState game = new CoinFlipGameState(players);
        game.setPlayerMove("player1", "HEADS");
        game.setPlayerMove("player2", "TAILS");
        game.setPlayerBets("player1", 1);
        game.setPlayerBets("player2", 2);
        Assert.assertEquals("COIN: NONE\n" +
                "CALLS: player1 HEADS, player2 TAILS\n" +
                "BETS: player1 1, player2 2\n" +
                "GAME: ONGOING", game.toString());
    }

    @Test
    public void testBaccaratGameState() throws Exception {
        Collection<String> players = new ArrayList<>();
        players.add("player1");
        players.add("player2");
        BaccaratGameState game = new BaccaratGameState(players);
        game.setPlayerMove("player1", "HEADS");
        game.setPlayerMove("player2", "TAILS");
        game.setPlayerBets("player1", 1);
        game.setPlayerBets("player2", 2);
        Assert.assertEquals("GAMESTATE: ONGOING\n" +
                "CALLS: player1 HEADS player2 TAILS\n" +
                "BETS: player1 1 player2 2\n" +
                "PLAYER_HAND NONE\n" +
                "BANKER_HAND NONE\n" +
                "GAMERESULT: NONE\n" +
                "PLAYER_CARDS NONE\n" +
                "BANKER_CARDS NONE", game.toString());
    }
}
