package com.example.cycino;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.PickVisualMediaRequest;
import androidx.activity.result.contract.ActivityResultContracts;

import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.util.Arrays;


/**
 * The BlackjackActivity is the activity that runs the game of blackjack.
 * It handles both frontend and backend interactions.
 * Includes all functions of basic blackjack
 * @author Sam Craft
 */


public class BlackjackActivity extends AppCompatActivity {

    String url = "http://coms-3090-052.class.las.iastate.edu:8080/blackjack/";

    /**
     * ImageView for card
     */
    private ImageView dCard1,dCard2, p1Card1, p1Card2, p2Card1, p2Card2, p3Card1, p3Card2, p4Card1, p4Card2;


    /**
     * LinearLayout for card formatting
     */
    private LinearLayout dCards, p1Cards, p2Cards, p3Cards, p4Cards, cardR1, cardR2;

    /**
     * Button for Hit
     */
    private Button hitButton;
    /**
     * Button for Stand
     */
    private Button standButton;
    /**
     * Button for Start
     */
    private Button startButton;
    /**
     * Button for Deal
     */
    private Button dealButton;
    /**
     * Button for Double
     */
    private Button doubleButton;

    RequestQueue requestQueue;

    /**
     * Current Lobby ID
     */
    private static Integer lobbyID;
    /**
     * User's user ID
     */
    private static Integer userID;

    /**
     * Number of cards dealer has
     */
    private int dCardNum = 0;
    /**
     * number of cards player has
     */
    private int p1CardNum = 0;
    private int p2CardNum = 0;
    private int p3CardNum = 0;
    private int p4CardNum = 0;

    /**
     * Number of players in game
     */
    private Integer numPlayers;
    private Integer[] playerIDs;

    /**
     * ImageView for extra cards
     */
    private ImageView d1x1, d1x2, d1x3, d1x4, d1x5;
    /**
     * ImageView for extra cards
     */
    private ImageView p1x1, p1x2, p1x3, p1x4, p1x5;
    private ImageView p2x1, p2x2, p2x3, p2x4, p2x5;
    private ImageView p3x1, p3x2, p3x3, p3x4, p3x5;
    private ImageView p4x1, p4x2, p4x3, p4x4, p4x5;


    private Button raiseBet, lowerBet,betBtn;
    private TextView currBetText, resultText, currChipText;
    private Integer currBet = 0;

    /**
     * Chat Buttons
     */
    private Button sendBtn, chatToggleBtn, backBtn;
    /**
     * Chat message box
     */
    private EditText msgEtx;
    /**
     * Chat message area
     */
    private TextView msgTv;
    /**
     * Chat outer boundary
     */
    private ScrollView chatArea;
    /**
     * Boolean to check if chat is open or closed
     */
    private boolean chatOpen = true;
    /**
     * VM URL
     */
    private String serverURL = "ws://coms-3090-052.class.las.iastate.edu:8080/chat/";
    /**
     * Current user's username
     */
    private String username;

    /**
     * File that holds the emulator's external storage location
     */
    File sdcard;

    String deckName = "Deck1";

    /**
     * @param savedInstanceState
     */
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_blackjack);

        sdcard = Environment.getExternalStorageDirectory();
        requestQueue = Volley.newRequestQueue(BlackjackActivity.this);


        Intent inIntent = getIntent();
        username = inIntent.getStringExtra("USERNAME");
        userID = inIntent.getIntExtra("UUID",-1);
        lobbyID = inIntent.getIntExtra("LOBBYID",-1);

//        username = "Sam";
//        userID = 4;
//        lobbyID = 0;

        getXMLIDs();
        setNumHands();


        currBetText.setText(currBet.toString());

        hitButton.setVisibility(View.GONE);
        standButton.setVisibility(View.GONE);
        doubleButton.setVisibility(View.GONE);
        dealButton.setVisibility(View.GONE);
        betBtn.setVisibility(View.GONE);
        resultText.setVisibility(View.GONE);

        String serverUrl = serverURL + "/" + lobbyID + "/" + username;
        Intent serviceIntent = new Intent(this, WebSocketService.class);
        serviceIntent.setAction("CONNECT");
        serviceIntent.putExtra("key", "chat1");
        serviceIntent.putExtra("url", serverUrl);
        startService(serviceIntent);

        sendBtn.setOnClickListener(v -> {

            String msgStr = msgEtx.getText().toString();

            if (!(msgStr.isEmpty())) {

                // broadcast this message to the WebSocketService
                // tag it with the key - to specify which WebSocketClient (connection) to send
                // in this case: "chat1"
                Intent intent = new Intent("SendWebSocketMessage");
                intent.putExtra("key", "chat1");
                intent.putExtra("message", msgStr);
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
                msgEtx.setText("");

            }


        });

        /* back button listener */
        chatToggleBtn.setOnClickListener(view -> {

                    if (chatOpen) {
                        sendBtn.setVisibility(View.GONE);
                        msgEtx.setVisibility(View.GONE);
                        chatArea.setVisibility(View.GONE);
                        chatToggleBtn.setText("Open Chat");

                        chatOpen = false;
                    } else {

                        sendBtn.setVisibility(View.VISIBLE);
                        msgEtx.setVisibility(View.VISIBLE);
                        chatArea.setVisibility(View.VISIBLE);
                        chatToggleBtn.setText("Close Chat");

                        chatOpen = true;

                    }
                });

        backBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.DELETE, url+"delete/"+lobbyID, null,
                        new Response.Listener<JSONObject>() {
                            @Override
                            public synchronized void onResponse(JSONObject response) {


                            }
                        }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        error.printStackTrace();
                        Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
                    }
                });

                requestQueue.add(jsonObjectRequest2);

                Intent i = new Intent(BlackjackActivity.this,LobbyPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",userID);
                i.putExtra("LOBBYID",lobbyID);
                startActivity(i);
            }
        });

        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startGame(numPlayers,lobbyID);
                startButton.setVisibility(View.GONE);
                betBtn.setVisibility(View.VISIBLE);
                dCards.setVisibility(View.VISIBLE);


            }
        });

        dealButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                deal();
            }
        });

        hitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                hit();
            }
        });

        standButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                stand();
            }
        });

        betBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if (currBet > 0) {
                    bet();
                    betBtn.setVisibility(View.GONE);
                }

                else {
                    Toast.makeText(BlackjackActivity.this, "Bet can not be 0", Toast.LENGTH_SHORT).show();
                }

            }
        });

        lowerBet.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if (currBet > 0) {
                    currBet -= 10;
                }
                currBetText.setText(currBet.toString());

            }

        });
        raiseBet.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {

                currBet += 10;
                currBetText.setText(currBet.toString());
            }

        });



    }

    /**
     *
     * Starts the game. Sets up all frontend components, makes calls to backend to start a new game.
     * @param numPlayers
     * @param lobbyID
     */
    private void startGame(int numPlayers, int lobbyID) {


        p1CardNum = 2;
        p2CardNum = 2;
        p3CardNum = 2;
        p4CardNum = 2;
        dCardNum = 2;

        resultText.setVisibility(View.GONE);

        p1Cards.removeView(p1x1);
        p1Cards.removeView(p1x2);
        p1Cards.removeView(p1x3);
        p1Cards.removeView(p1x4);
        p1Cards.removeView(p1x5);
        p2Cards.removeView(p2x1);
        p2Cards.removeView(p2x2);
        p2Cards.removeView(p2x3);
        p2Cards.removeView(p2x4);
        p2Cards.removeView(p2x5);
        p3Cards.removeView(p3x1);
        p3Cards.removeView(p3x2);
        p3Cards.removeView(p3x3);
        p3Cards.removeView(p3x4);
        p3Cards.removeView(p3x5);
        p4Cards.removeView(p4x1);
        p4Cards.removeView(p4x2);
        p4Cards.removeView(p4x3);
        p4Cards.removeView(p4x4);
        p4Cards.removeView(p4x5);
        dCards.removeView(d1x1);
        dCards.removeView(d1x2);
        dCards.removeView(d1x3);
        dCards.removeView(d1x4);
        dCards.removeView(d1x5);

        String cardBack = "card_back";

        dCard1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        dCard2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p1Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p1Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p2Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p2Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p3Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p3Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p4Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p4Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));



            JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.DELETE, url + "delete/" + lobbyID, null,
                    new Response.Listener<JSONObject>() {
                        @Override
                        public synchronized void onResponse(JSONObject response) {


                        }
                    }, new Response.ErrorListener() {
                @Override
                public void onErrorResponse(VolleyError error) {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
                }
            });

            JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                    (Request.Method.POST, url + "create/" + lobbyID, null, new Response.Listener<JSONObject>() {
                        @Override
                        public void onResponse(JSONObject response) {
                            // Handle the successful response here
                            try {
                                String status = response.getString("status");
                                System.out.println(response);
                            } catch (JSONException e) {
                                e.printStackTrace();
                                Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                            }
                        }
                    }, new Response.ErrorListener() {
                        @Override
                        public void onErrorResponse(VolleyError error) {
                            // Handle the error response
                            Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                            error.printStackTrace();
                        }
                    });
            // Add the request to the RequestQueue
            RequestQueue queue = Volley.newRequestQueue(this);

            queue.add(jsonObjectRequest2);
            myWait(1000);
            queue.add(jsonObjectRequest);


    }

    /**
     *Deals the hand for the game. Deals for everyone at the table
     */
    private void deal(){



                standButton.setVisibility(View.VISIBLE);
                hitButton.setVisibility(View.VISIBLE);
                dealButton.setVisibility(View.GONE);
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"deal/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {

                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });

        JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.GET, url+"getdealer/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {


                        try {
                            JSONObject card1 = response.getJSONObject("card1");
                            JSONObject card2 = response.getJSONObject("card2");

                            Integer score = response.getInt("score");

                            String card1S = card1.getString("suit").toLowerCase() + "_" + card1.getString("number");
                            String card2S = card2.getString("suit").toLowerCase() + "_" + card2.getString("number");

                            dCard1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+card1S+".png")));
                            //dCard2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+card2S+".png")));
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }


                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });



                try {
                    requestQueue.add(jsonObjectRequest);
                    Thread.sleep(500);
                    requestQueue.add(jsonObjectRequest2);
                    Thread.sleep(500);
                    updateHands();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }

    }

    /**
     *Sends a request to the backend to hit for the user connected from the device
     */
    private void hit(){
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"hit/"+lobbyID+"/"+userID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                        updateHands();
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });


        // Add the request to the RequestQueue

                requestQueue.add(jsonObjectRequest);



    }
    /**
     *Sends a request to the backend to stand for the user connected from the device
     */
    private void stand() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"stand/"+lobbyID+"/"+userID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });


        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }

    private void bet() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"bet/"+lobbyID+"/"+userID+"/"+currBet, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });


        // Add the request to the RequestQueue

        requestQueue.add(jsonObjectRequest);

    }

    /**
     *Shows the rest of the dealers hand and finishes up the game
     */
    private void finishGame() {

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"finish/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                        System.out.println(response);
                        try {

                            JSONArray dealerCards = response.getJSONArray("dealer");
                            Integer score = response.getInt("dscore");



                            String result = response.getString(userID.toString());
                            resultText.setText("You " + result + " " + currBet.toString());
                            resultText.setVisibility(View.VISIBLE);

                            for (int i = 0; i < dealerCards.length(); i++) {
                                JSONObject card = dealerCards.getJSONObject(i);
                                if (i == 1) {
                                    JSONObject card2 = dealerCards.getJSONObject(1);

                                    String card2S = card2.getString("suit").toLowerCase() + "_" + card2.getString("number");
                                    dCard2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+card2S+".png")));

                                }

                                if (i > 1) {
                                    String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                    addDealerCard(cardS);
                                }

                                System.out.println(card);

                            }

                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }

                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });



        requestQueue.add(jsonObjectRequest);

        standButton.setVisibility(View.GONE);
        hitButton.setVisibility(View.GONE);
        startButton.setVisibility(View.VISIBLE);


    }

    private void finishUpdate() {


        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url+"gethands/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                        System.out.println(response);
                        try {

                            JSONArray dealerCards = response.getJSONArray("dealer");

                            String result = response.getString(userID.toString());
                            resultText.setText("You " + result + " " + currBet.toString());
                            resultText.setVisibility(View.VISIBLE);

                            for (int i = 0; i < dealerCards.length(); i++) {
                                JSONObject card = dealerCards.getJSONObject(i);
                                if (i == 1) {
                                    JSONObject card2 = dealerCards.getJSONObject(1);

                                    String card2S = card2.getString("suit").toLowerCase() + "_" + card2.getString("number");
                                    dCard2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+card2S+".png")));

                                }

                                if (i > 1) {
                                    String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                    addDealerCard(cardS);
                                }

                                System.out.println(card);

                            }

                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }

                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });



        requestQueue.add(jsonObjectRequest);

        standButton.setVisibility(View.GONE);
        hitButton.setVisibility(View.GONE);
        startButton.setVisibility(View.VISIBLE);


    }

    private void updateHands() {
        getUserChips();
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url+"gethands/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {

                        JSONArray dealerCards;
                        JSONArray user1Cards;
                        JSONArray user2Cards;
                        JSONArray user3Cards;
                        JSONArray user4Cards;

                        try {

                            dealerCards = response.getJSONArray("dealer");
                            JSONObject dcard1 = dealerCards.getJSONObject(0);
                            String dcard1S = dcard1.getString("suit").toLowerCase() + "_" + dcard1.getString("number");
                            dCard1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard1S+".png")));

                            user1Cards = response.getJSONArray(playerIDs[0].toString());
                            JSONObject p1card1 = user1Cards.getJSONObject(0);
                            JSONObject p1card2 = user1Cards.getJSONObject(1);
                            String p1card1S = p1card1.getString("suit").toLowerCase() + "_" + p1card1.getString("number");
                            String p1card2S = p1card2.getString("suit").toLowerCase() + "_" + p1card2.getString("number");
                            p1Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p1card1S+".png")));
                            p1Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p1card2S+".png")));

                            if (user1Cards.length() > 2 && p1CardNum != user1Cards.length()) {
                                for (int i = p1CardNum; i < user1Cards.length(); i++) {
                                    JSONObject card = user1Cards.getJSONObject(i);
                                    String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                    addPlayer1Card(cardS);
                                }
                            }

                            if (numPlayers > 1) {
                                user2Cards = response.getJSONArray(playerIDs[1].toString());
                                JSONObject p2card1 = user2Cards.getJSONObject(0);
                                JSONObject p2card2 = user2Cards.getJSONObject(1);
                                String p2card1S = p2card1.getString("suit").toLowerCase() + "_" + p2card1.getString("number");
                                String p2card2S = p2card2.getString("suit").toLowerCase() + "_" + p2card2.getString("number");
                                p2Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p2card1S+".png")));
                                p2Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p2card2S+".png")));

                                if (user2Cards.length() > 2 && p2CardNum != user2Cards.length()) {
                                    for (int i = p2CardNum; i < user2Cards.length(); i++) {
                                        JSONObject card = user2Cards.getJSONObject(i);
                                        String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                        addPlayer2Card(cardS);
                                    }
                                }
                            }
                            if (numPlayers > 2) {
                                user3Cards = response.getJSONArray(playerIDs[2].toString());
                                JSONObject p3card1 = user3Cards.getJSONObject(0);
                                JSONObject p3card2 = user3Cards.getJSONObject(1);
                                String p3card1S = p3card1.getString("suit").toLowerCase() + "_" + p3card1.getString("number");
                                String p3card2S = p3card2.getString("suit").toLowerCase() + "_" + p3card2.getString("number");
                                p3Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p3card1S+".png")));
                                p3Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p3card2S+".png")));
                                if (user3Cards.length() > 2 && p3CardNum != user3Cards.length()) {
                                    for (int i = p3CardNum; i < user3Cards.length(); i++) {
                                        JSONObject card = user3Cards.getJSONObject(i);
                                        String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                        addPlayer3Card(cardS);
                                    }
                                }
                            }
                            if (numPlayers > 3) {
                                user4Cards = response.getJSONArray(playerIDs[3].toString());
                                JSONObject p4card1 = user4Cards.getJSONObject(0);
                                JSONObject p4card2 = user4Cards.getJSONObject(1);
                                String p4card1S = p4card1.getString("suit").toLowerCase() + "_" + p4card1.getString("number");
                                String p4card2S = p4card2.getString("suit").toLowerCase() + "_" + p4card2.getString("number");
                                p4Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p4card1S+".png")));
                                p4Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+p4card2S+".png")));
                                if (user4Cards.length() > 2 && p4CardNum != user4Cards.length()) {
                                    for (int i = p4CardNum; i < user4Cards.length(); i++) {
                                        JSONObject card = user4Cards.getJSONObject(i);
                                        String cardS = card.getString("suit").toLowerCase() + "_" + card.getString("number");
                                        addPlayer4Card(cardS);
                                    }
                                }
                            }

                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }


                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });

        requestQueue.add(jsonObjectRequest);

    }

    /**
     * Adds a card to dealer's hand
     * @param cardS
     */
    private void addDealerCard(String cardS) {

        dCardNum++;
        LinearLayout.LayoutParams param = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);


        ImageView dCardNew = new ImageView(this);
        dCardNew.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardS+".png")));
        dCardNew.setLayoutParams(param);
        dCardNew.setPadding(2,2,2,2);
        dCards.addView(dCardNew);

        switch (dCardNum){
            case 3:
                d1x1 = dCardNew;
                break;
            case 4:
                d1x2 = dCardNew;
                break;
            case 5:
                d1x3 = dCardNew;
                break;
            case 6:
                d1x4 = dCardNew;
                break;
            case 7:
                d1x5 = dCardNew;
                break;
        }

    }

    /**
     * Adds a card to player's hand
     * @param cardS
     */
    private void addPlayer1Card(String cardS) {

        p1CardNum++;
        LinearLayout.LayoutParams param = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);


        ImageView p1CardNew = new ImageView(this);
        p1CardNew.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardS+".png")));
        p1CardNew.setLayoutParams(param);
        p1CardNew.setPadding(2,2,2,2);
        p1Cards.addView(p1CardNew);

        switch (p1CardNum){
            case 3:
                p1x1 = p1CardNew;
                break;
            case 4:
                p1x2 = p1CardNew;
                break;
            case 5:
                p1x3 = p1CardNew;
                break;
            case 6:
                p1x4 = p1CardNew;
                break;
            case 7:
                p1x5 = p1CardNew;
                break;
        }

    }

    private void addPlayer2Card(String cardS) {

        p2CardNum++;
        LinearLayout.LayoutParams param = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);


        ImageView p2CardNew = new ImageView(this);
        p2CardNew.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardS+".png")));
        p2CardNew.setLayoutParams(param);
        p2CardNew.setPadding(2,2,2,2);
        p2Cards.addView(p2CardNew);

        switch (p2CardNum){
            case 3:
                p2x1 = p2CardNew;
                break;
            case 4:
                p2x2 = p2CardNew;
                break;
            case 5:
                p2x3 = p2CardNew;
                break;
            case 6:
                p2x4 = p2CardNew;
                break;
            case 7:
                p2x5 = p2CardNew;
                break;
        }

    }

    private void addPlayer3Card(String cardS) {

        p3CardNum++;
        LinearLayout.LayoutParams param = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);


        ImageView p3CardNew = new ImageView(this);
        p3CardNew.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardS+".png")));
        p3CardNew.setLayoutParams(param);
        p3CardNew.setPadding(2,2,2,2);
        p1Cards.addView(p3CardNew);

        switch (p3CardNum){
            case 3:
                p3x1 = p3CardNew;
                break;
            case 4:
                p3x2 = p3CardNew;
                break;
            case 5:
                p3x3 = p3CardNew;
                break;
            case 6:
                p3x4 = p3CardNew;
                break;
            case 7:
                p3x5 = p3CardNew;
                break;
        }

    }

    private void addPlayer4Card(String cardS) {

        p4CardNum++;
        LinearLayout.LayoutParams param = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);


        ImageView p4CardNew = new ImageView(this);
        p4CardNew.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardS+".png")));
        p4CardNew.setLayoutParams(param);
        p4CardNew.setPadding(2,2,2,2);
        p1Cards.addView(p4CardNew);

        switch (p4CardNum){
            case 3:
                p4x1 = p4CardNew;
                break;
            case 4:
                p4x2 = p4CardNew;
                break;
            case 5:
                p4x3 = p4CardNew;
                break;
            case 6:
                p4x4 = p4CardNew;
                break;
            case 7:
                p4x5 = p4CardNew;
                break;
        }

    }


    /**
     * Timer in a new thread
     * @param waitTime
     */
    private void myWait(int waitTime) {
        class MyRunnable implements Runnable {
            public synchronized void run() {
                // Code to be executed in the new thread

                try {
                    wait(waitTime);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }

            }
        }
        Thread thread = new Thread(new MyRunnable());
        thread.start();
    }

    private void setNumHands() {

        String cardBack = "card_back";

        dCard1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        dCard2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p1Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p1Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p2Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p2Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p3Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p3Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        p4Card1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));
        p4Card2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+cardBack+".png")));

        JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.GET, "http://coms-3090-052.class.las.iastate.edu:8080/lobby/" + lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {

                        JSONArray playersArray;

                        try {
                            Integer np = response.getInt("size");
                            playersArray = response.getJSONArray("players");

                            playerIDs = new Integer[np];

                            for (int i = 0; i < playersArray.length(); i++) {

                                playerIDs[i] = playersArray.getInt(i);

                            }
                            hideHands(np);


    System.out.println(Arrays.toString(playerIDs));

                            System.out.println("NUMPLAYERS" + response.getInt("size"));
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }


                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });
        requestQueue.add(jsonObjectRequest2);
    }

    private void hideHands(Integer numP) {
        numPlayers = numP;

        dCards.setVisibility(View.VISIBLE);
        p1Cards.setVisibility(View.VISIBLE);
        if (playerIDs[0] == userID) {
            p1Cards.setBackgroundColor(0xFF32CD32);
        }
        if(numP > 1) {
            p2Cards.setVisibility(View.VISIBLE);
            if (playerIDs[1] == userID) {
                p2Cards.setBackgroundColor(0xFF32CD32);
            }
        }
        if(numP > 2) {
            p3Cards.setVisibility(View.VISIBLE);
            if (playerIDs[2] == userID) {
                p3Cards.setBackgroundColor(0xFF32CD32);
            }
        }
        if(numP > 3) {
            p4Cards.setVisibility(View.VISIBLE);
            if (playerIDs[3] == userID) {
                p4Cards.setBackgroundColor(0xFF32CD32);
            }
        }
    }

    private void getUserChips() {

        String url = "http://coms-3090-052.class.las.iastate.edu:8080/chips/get/"+userID;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {

                        try {
                            int currChips = response.getInt("chips");
                            setChipText(currChips);

                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }

                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(),"view failed", Toast.LENGTH_LONG).show();
            }
        });

        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }

    private void setChipText(Integer chips) {

        currChipText.setText("Chips: " + chips.toString());
    }

    private void getXMLIDs() {

        dCard1 = findViewById(R.id.dealerCard1);
        dCard2 = findViewById(R.id.dealerCard2);
        p1Card1 = findViewById(R.id.player1Card1);
        p1Card2 = findViewById(R.id.player1Card2);
        p2Card1 = findViewById(R.id.player2Card1);
        p2Card2 = findViewById(R.id.player2Card2);
        p3Card1 = findViewById(R.id.player3Card1);
        p3Card2 = findViewById(R.id.player3Card2);
        p4Card1 = findViewById(R.id.player4Card1);
        p4Card2 = findViewById(R.id.player4Card2);

        dCards = findViewById(R.id.dealerCards);
        p1Cards = findViewById(R.id.player1Cards);
        p2Cards = findViewById(R.id.player2Cards);
        p3Cards = findViewById(R.id.player3Cards);
        p4Cards = findViewById(R.id.player4Cards);

        cardR1 = findViewById(R.id.cardsR1);
        cardR2 = findViewById(R.id.cardsR2);

        hitButton = findViewById(R.id.hitButton);
        standButton = findViewById(R.id.standButton);
        startButton = findViewById(R.id.startButton);
        dealButton = findViewById(R.id.dealButton);
        doubleButton = findViewById(R.id.doubleButton);

        sendBtn = (Button) findViewById(R.id.bsendBtn);
        chatToggleBtn = (Button) findViewById(R.id.bbackMainBtn);
        msgEtx = (EditText) findViewById(R.id.bmsgEdt);
        msgTv = (TextView) findViewById(R.id.btx1);
        chatArea = findViewById(R.id.bchatView);
        backBtn = findViewById(R.id.bbackButton);

        currBetText = findViewById(R.id.bCurrBet);
        resultText = findViewById(R.id.bResult);
        currChipText = findViewById(R.id.bCurrChips);
        raiseBet = findViewById(R.id.bRaiseBet);
        lowerBet = findViewById(R.id.bLowerBet);
        betBtn = findViewById(R.id.bbetButton);

    }

        private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String key = intent.getStringExtra("key");
                if ("chat1".equals(key)) {
                    String message = intent.getStringExtra("message");

                    if (message.contains("#Blackjack")) {
                        updateHands();
                        String[] commands = message.split(",");

                        for (String cmd : commands) {

                            if (cmd.contains("next")) {
                                String intMessage = cmd.replaceAll("[^\\d.]", "");
                                int nextPlayer = Integer.parseInt(intMessage);
                                System.out.println("Next player "+ nextPlayer);
                                if (nextPlayer == userID) {
                                    hitButton.setVisibility(View.VISIBLE);
                                    standButton.setVisibility(View.VISIBLE);
                                }
                                else {
                                    hitButton.setVisibility(View.INVISIBLE);
                                    standButton.setVisibility(View.INVISIBLE);
                                }
                            }
                            if (cmd.contains("finish")) {
                                finishGame();
                            }

//                            if (cmd.contains("finish") && playerIDs[0] == userID) {
//                                finishGame();
//                            }
//                            if (cmd.contains("finish") && playerIDs[0] != userID) {
//                                finishUpdate();
//                            }



                        }

                    }
                    else {
                        runOnUiThread(() -> {
                            String s = msgTv.getText().toString();
                            msgTv.setText(s + message + "\n");
                            chatArea.fullScroll(View.FOCUS_DOWN);


                        });
                    }
                }

            }
        };

        @Override
        protected void onStart() {
            super.onStart();
            LocalBroadcastManager.getInstance(this).registerReceiver(messageReceiver,
                    new IntentFilter("WebSocketMessageReceived"));
        }

        @Override
        protected void onStop() {
            super.onStop();
            LocalBroadcastManager.getInstance(this).unregisterReceiver(messageReceiver);
        }
}


