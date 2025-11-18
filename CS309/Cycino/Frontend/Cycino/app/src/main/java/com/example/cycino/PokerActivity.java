package com.example.cycino;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.os.Environment;
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
import java.util.Objects;

public class PokerActivity extends AppCompatActivity {

    String url = "http://coms-3090-052.class.las.iastate.edu:8080/poker/";

    private ImageView dc1,dc2,dc3,dc4,dc5,p1c1,p1c2,p2c1,p2c2,p3c1,p3c2,p4c1,p4c2,p5c1,p5c2,p6c1,p6c2;
    private LinearLayout dcs,p1cs,p2cs,p3cs,p4cs,p5cs,p6cs;
    private LinearLayout pcr1, pcr2, pcr3;
    private TextView currBetText, playerChipText;
    private Button checkCallBtn, raiseBtn, foldBtn,startBtn;
    private Button raiseBet, lowerBet;


    private Integer userID;
    private Integer lobbyID;
    private String username;

    private Integer currBet = 0;
    private Integer minBet = 0;
    private Integer numPlayers = 0;


    private Button sendBtn, chatToggleBtn, backBtn;
    private EditText msgEtx;
    private TextView msgTv;
    private ScrollView chatArea;
    private boolean chatOpen = true;
    private String serverURL = "ws://coms-3090-052.class.las.iastate.edu:8080/chat/";

    String deckName = "Deck1";
    private Boolean isHost = false;

    RequestQueue requestQueue;
    File sdcard;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_poker);

        sdcard = Environment.getExternalStorageDirectory();
        requestQueue = Volley.newRequestQueue(PokerActivity.this);

        Intent inIntent = getIntent();
        username = inIntent.getStringExtra("USERNAME");
        userID = inIntent.getIntExtra("UUID", -1);
        lobbyID = inIntent.getIntExtra("LOBBYID",-1);


        getXMLIDs();
        setNumHands();
        createGame();

        currBetText.setText(currBet.toString());

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


        raiseBet.setOnClickListener(new View.OnClickListener() {

            public void onClick(View view) {

                currBet += 10;
                currBetText.setText(currBet.toString());
            }

        });
        backBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.DELETE, url+"delete/"+lobbyID, null,
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
                requestQueue.add(jsonObjectRequest);

                Intent i = new Intent(PokerActivity.this,LobbyPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",userID);
                i.putExtra("LOBBYID",lobbyID);
                startActivity(i);
            }
        });

        lowerBet.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if (currBet > minBet) {
                    currBet -= 10;
                }
                currBetText.setText(currBet.toString());

            }

        });

        raiseBtn.setOnClickListener(new View.OnClickListener()  {
            @Override
            public void onClick(View view) {
            raise();
        }});

        foldBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
            fold();
        }});

        checkCallBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
            checkCall();
        }});

        startBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startGame();
            }
        });


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

        playerChipText.setText("Chips: " + chips.toString());
    }

    private void getXMLIDs() {
        dc1 = findViewById(R.id.pDCard1);
        dc2 = findViewById(R.id.pDCard2);
        dc3 = findViewById(R.id.pDCard3);
        dc4 = findViewById(R.id.pDCard4);
        dc5 = findViewById(R.id.pDCard5);

        p1c1 = findViewById(R.id.pP1Card1);
        p1c2 = findViewById(R.id.pP1Card2);
        p2c1 = findViewById(R.id.pP2Card1);
        p2c2 = findViewById(R.id.pP2Card2);
        p3c1 = findViewById(R.id.pP3Card1);
        p3c2 = findViewById(R.id.pP3Card2);
        p4c1 = findViewById(R.id.pP4Card1);
        p4c2 = findViewById(R.id.pP4Card2);
        p5c1 = findViewById(R.id.pP5Card1);
        p5c2 = findViewById(R.id.pP5Card2);
        p6c1 = findViewById(R.id.pP6Card1);
        p6c2 = findViewById(R.id.pP6Card2);

        dcs = findViewById(R.id.pDCards);
        p1cs = findViewById(R.id.pP1Cards);
        p2cs = findViewById(R.id.pP2Cards);
        p3cs = findViewById(R.id.pP3Cards);
        p4cs = findViewById(R.id.pP4Cards);
        p5cs = findViewById(R.id.pP5Cards);
        p6cs = findViewById(R.id.pP6Cards);

        pcr1 = findViewById(R.id.pPCardsR1);
        pcr2 = findViewById(R.id.pPCardsR2);
        pcr3 = findViewById(R.id.pPCardsR3);

        sendBtn = (Button) findViewById(R.id.psendBtn);
        chatToggleBtn = (Button) findViewById(R.id.pbackMainBtn);
        chatArea = findViewById(R.id.pchatView);
        msgEtx = (EditText) findViewById(R.id.pmsgEdt);
        msgTv = (TextView) findViewById(R.id.ptx1);
        backBtn = findViewById(R.id.pbackButton);


        currBetText = findViewById(R.id.pCurrBet);
        playerChipText = findViewById(R.id.pCurrChips);
        raiseBet = findViewById(R.id.pRaiseBet);
        lowerBet = findViewById(R.id.pLowerBet);

        raiseBtn = findViewById(R.id.pRaiseButton);
        checkCallBtn = findViewById(R.id.pCheckButton);
        foldBtn = findViewById(R.id.pFoldButton);
        startBtn = findViewById(R.id.pStartButton);

    }

    private void raise() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"raise/"+lobbyID+"/"+userID+"/"+currBet, null,
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

    private void fold() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"fold/"+lobbyID+"/"+userID, null,
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
        requestQueue.add(jsonObjectRequest);
    }

    private void checkCall() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"call/"+lobbyID+"/"+userID, null,
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
        requestQueue.add(jsonObjectRequest);
    }

    private void setNumHands() {

        JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.GET, "http://coms-3090-052.class.las.iastate.edu:8080/lobby/" + lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {


                        try {
                            hideHands(response.getInt("size"));
//                            Integer hostID = response.getInt("host");
//
//                            if (Objects.equals(userID, hostID)) {
//                                isHost = true;
//                            }


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

    private void hideHands(Integer numPlayers) {
        if (numPlayers < 6) {
            p6cs.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 5) {
            p5cs.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 4) {
            p4cs.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 3) {
            p3cs.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 2) {
            p2cs.setVisibility(View.INVISIBLE);
        }
    }

    private void startGame() {

        resetCards();
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"start/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                        JSONArray dealerCards;
                        JSONArray playerCards;

                        try {
                            dealerCards = response.getJSONArray("dealer");
                            playerCards = response.getJSONArray(userID.toString());

                            JSONObject dco1 = dealerCards.getJSONObject(0);
                            JSONObject dco2 = dealerCards.getJSONObject(1);
                            JSONObject dco3 = dealerCards.getJSONObject(2);

                            JSONObject pco1 = playerCards.getJSONObject(0);
                            JSONObject pco2 = playerCards.getJSONObject(1);

                            String dcard1S = dco1.getString("suit").toLowerCase() + "_" + dco1.getString("number");
                            String dcard2S = dco2.getString("suit").toLowerCase() + "_" + dco2.getString("number");
                            String dcard3S = dco3.getString("suit").toLowerCase() + "_" + dco3.getString("number");
                            String pcard1S = pco1.getString("suit").toLowerCase() + "_" + pco1.getString("number");
                            String pcard2S = pco2.getString("suit").toLowerCase() + "_" + pco2.getString("number");

                            dc1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard1S+".png")));
                            dc2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard2S+".png")));
                            dc3.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard3S+".png")));
                            p1c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+pcard1S+".png")));
                            p1c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+pcard2S+".png")));

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

    private void createGame() {

        resetCards();
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

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.POST, url+"create/"+lobbyID, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        // Handle the successful response here
                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // Handle the error response
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                        error.printStackTrace();
                    }
                });
        requestQueue.add(jsonObjectRequest2);
        requestQueue.add(jsonObjectRequest);




    }

    private void updateDealer() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url+"hands/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {


                        try {
                            JSONArray dealerCards = response.getJSONArray("dealer");

                            if (dealerCards.length() == 4) {

                                JSONObject dco1 = dealerCards.getJSONObject(0);
                                JSONObject dco2 = dealerCards.getJSONObject(1);
                                JSONObject dco3 = dealerCards.getJSONObject(2);
                                JSONObject dco4 = dealerCards.getJSONObject(3);

                                String dcard1S = dco1.getString("suit").toLowerCase() + "_" + dco1.getString("number");
                                String dcard2S = dco2.getString("suit").toLowerCase() + "_" + dco2.getString("number");
                                String dcard3S = dco3.getString("suit").toLowerCase() + "_" + dco3.getString("number");
                                String dcard4S = dco4.getString("suit").toLowerCase() + "_" + dco4.getString("number");



                                dc1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard1S+".png")));
                                dc2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard2S+".png")));
                                dc3.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard3S+".png")));
                                dc4.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard4S+".png")));

                            } else if (dealerCards.length() == 5) {

                                JSONObject dco1 = dealerCards.getJSONObject(0);
                                JSONObject dco2 = dealerCards.getJSONObject(1);
                                JSONObject dco3 = dealerCards.getJSONObject(2);
                                JSONObject dco4 = dealerCards.getJSONObject(3);
                                JSONObject dco5 = dealerCards.getJSONObject(4);

                                String dcard1S = dco1.getString("suit").toLowerCase() + "_" + dco1.getString("number");
                                String dcard2S = dco2.getString("suit").toLowerCase() + "_" + dco2.getString("number");
                                String dcard3S = dco3.getString("suit").toLowerCase() + "_" + dco3.getString("number");
                                String dcard4S = dco4.getString("suit").toLowerCase() + "_" + dco4.getString("number");
                                String dcard5S = dco5.getString("suit").toLowerCase() + "_" + dco5.getString("number");



                                dc1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard1S+".png")));
                                dc2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard2S+".png")));
                                dc3.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard3S+".png")));
                                dc4.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard4S+".png")));
                                dc5.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard5S+".png")));

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

    private void resetCards() {
        dc1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        dc2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        dc3.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        dc4.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        dc5.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p1c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p1c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p2c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p2c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p3c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p3c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p4c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p4c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p5c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p5c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));

        p6c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
        p6c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+"card_back.png")));
    }

    private void finishGame() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url+"finish/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {

                        System.out.println(response.toString());

                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });
        JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.GET, url+"hands/"+lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {


                        try {
                            JSONArray dealerCards = response.getJSONArray("1");


                                JSONObject dco1 = dealerCards.getJSONObject(0);
                                JSONObject dco2 = dealerCards.getJSONObject(1);

                                String dcard1S = dco1.getString("suit").toLowerCase() + "_" + dco1.getString("number");
                                String dcard2S = dco2.getString("suit").toLowerCase() + "_" + dco2.getString("number");

                                p2c1.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard1S+".png")));
                                p2c2.setImageURI(Uri.fromFile(new File(sdcard,"Android/media/"+deckName+"/"+dcard2S+".png")));


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
        requestQueue.add(jsonObjectRequest2);

    }

    private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String key = intent.getStringExtra("key");
            if ("chat1".equals(key)) {
                String message = intent.getStringExtra("message");

                if (message.contains("#Poker")) {
                    getUserChips();
                    String[] commands = message.split(",");

                    for (String cmd : commands) {
                        System.out.println(cmd);
                        if (cmd.contains("update")) {
                            updateDealer();
                        }
                        if (cmd.contains("finish")) {
                            finishGame();
                        }
                        if (cmd.contains("next")) {
                            String intMessage = cmd.replaceAll("[^\\d.]", "");
                            int nextPlayer = Integer.parseInt(intMessage);
                            System.out.println("Next player "+ nextPlayer);
                            if (nextPlayer == userID) {
                                raiseBtn.setVisibility(View.VISIBLE);
                                checkCallBtn.setVisibility(View.VISIBLE);
                                foldBtn.setVisibility(View.VISIBLE);
                            }
                            else {
                                raiseBtn.setVisibility(View.INVISIBLE);
                                checkCallBtn.setVisibility(View.INVISIBLE);
                                foldBtn.setVisibility(View.INVISIBLE);
                            }
                        }
                        if (cmd.contains("raise")){
                            String raiseStr = cmd.replaceAll("[^\\d.]", "");
                            int raiseAmt = Integer.parseInt(raiseStr);
                            System.out.println("Raised "+raiseAmt);
                            minBet = raiseAmt;
                        }

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
