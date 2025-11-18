package coms309.Cycino;


import com.fasterxml.jackson.databind.ObjectMapper;
import coms309.Cycino.Games.GameLogic.Card;
import coms309.Cycino.Games.GameLogic.PlayerHands;
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

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static net.bytebuddy.matcher.ElementMatchers.is;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;


@RunWith(SpringRunner.class)
@AutoConfigureMockMvc
@SpringBootTest(classes = CycinoApplication.class, properties = "spring.profiles.active=test", webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class BenSystemTest {

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
    public void testStraight() throws Exception{
        Set<Card> cardSet = new HashSet<>();
        cardSet.add(new Card("5", Enums.SUIT.DIAMONDS, null));
        cardSet.add(new Card("3", Enums.SUIT.HEARTS, null));
        cardSet.add(new Card("3", Enums.SUIT.HEARTS, null));
        cardSet.add(new Card("6", Enums.SUIT.DIAMONDS, null));
        cardSet.add(new Card("7", Enums.SUIT.HEARTS, null));
        cardSet.add(new Card("4", Enums.SUIT.DIAMONDS, null));
        cardSet.add(new Card("10", Enums.SUIT.HEARTS, null));

        PlayerHands hand = new PlayerHands(new User(), null);
        hand.addAll(cardSet);

        System.out.println(Evaluator.evaluate(hand));
        Assert.assertEquals(Evaluator.evaluate(hand), 5.07, 0.009);
    }

    @Test
    public void testCreation() throws Exception {
        User u = new User();
        repo.save(u);
        long id = u.getId();
        RequestBuilder request = (RequestBuilder) post("/lobby/create/{id}", id);
        MvcResult result = controller.perform(request).andReturn();
        String jsonResponse = result.getResponse().getContentAsString();
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, Object> responseMap = objectMapper.readValue(jsonResponse, Map.class);
        int lobbyId = (int) responseMap.get("lobbyId");
        RequestBuilder request2 = (RequestBuilder) post("/poker/create/{id}", lobbyId);
        MvcResult result2 = controller.perform(request2).andReturn();
        String jsonResponse2 = result.getResponse().getContentAsString();
        ObjectMapper objectMapper2 = new ObjectMapper();
        Map<String, Object> responseMap2 = objectMapper.readValue(jsonResponse2, Map.class);
        Assert.assertEquals(responseMap2.get("status"), "200 ok");

    }

    @Test
    public void testDeal() throws Exception{
        User u = new User();
        repo.save(u);
        long id = u.getId();

        RequestBuilder request = (RequestBuilder) post("/lobby/create/{id}", id);
        MvcResult result = controller.perform(request).andReturn();
        String jsonResponse = result.getResponse().getContentAsString();
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, Object> responseMap = objectMapper.readValue(jsonResponse, Map.class);
        int lobbyId = (int) responseMap.get("lobbyId");

        RequestBuilder request2 = (RequestBuilder) post("/poker/create/{id}", lobbyId);
        controller.perform(request2);

        RequestBuilder request3 = (RequestBuilder) put("/poker/start/{id}", lobbyId);
        controller.perform(request3);

        RequestBuilder request4 = (RequestBuilder) get("/poker/hands/{id}", lobbyId);
        MvcResult result2 = controller.perform(request4).andReturn();
        String jsonResponse2 = result2.getResponse().getContentAsString();
        System.out.println(jsonResponse2);
        ObjectMapper objectMapper2 = new ObjectMapper();
        Map<String, Object> responseMap2 = objectMapper2.readValue(jsonResponse2, Map.class);

        for(String s: responseMap2.keySet()){
            if(s != "dealer" && !s.equals("status")){
                Assert.assertEquals(((ArrayList<Card>)(responseMap2.get(s))).size(), 2);
            } else if(s == "dealer"){
                Assert.assertEquals(((ArrayList<Card>)(responseMap2.get(s))).size(), 3);
            }
        }
    }

    @Test
    public void testEnd() throws Exception{
        User u = new User();
        repo.save(u);
        long id = u.getId();

        RequestBuilder request = (RequestBuilder) post("/lobby/create/{id}", id);
        MvcResult result = controller.perform(request).andReturn();
        String jsonResponse = result.getResponse().getContentAsString();
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, Object> responseMap = objectMapper.readValue(jsonResponse, Map.class);
        int lobbyId = (int) responseMap.get("lobbyId");

        RequestBuilder request2 = (RequestBuilder) post("/poker/create/{id}", lobbyId);
        controller.perform(request2);

        RequestBuilder request3 = (RequestBuilder) put("/poker/start/{id}", lobbyId);
        controller.perform(request3);

        RequestBuilder request4 = (RequestBuilder) get("/poker/finish/{id}", lobbyId);
        MvcResult result2 = controller.perform(request4).andReturn();
        String jsonResponse2 = result2.getResponse().getContentAsString();
        System.out.println(jsonResponse2);
        ObjectMapper objectMapper2 = new ObjectMapper();
        Map<String, Object> responseMap2 = objectMapper2.readValue(jsonResponse2, Map.class);

        Assert.assertFalse(responseMap2.keySet().isEmpty());
    }

}
