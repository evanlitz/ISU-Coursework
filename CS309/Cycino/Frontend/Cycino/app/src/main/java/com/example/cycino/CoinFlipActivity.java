package com.example.cycino;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Arrays;

public class CoinFlipActivity extends AppCompatActivity{

    private Integer userID;
    private Integer lobbyID;
    private String username;

    private TextView p1,p2,p3,p4,p5,p6, coinText,playerChipText;

    private Button sendBtn, chatToggleBtn, backBtn;
    private EditText msgEtx;
    private TextView msgTv;
    private ScrollView chatArea;
    private boolean chatOpen = true;
    private String serverURL = "ws://coms-3090-052.class.las.iastate.edu:8080/chat/";

    private Button raiseBet, lowerBet, headsBtn, tailsBtn, betBtn, startBtn;
    private TextView currBetText;
    private Integer currBet = 0;
    private Integer playerChips = 0;

    private Integer numPlayers = 0;

    private CoinFlipUser[] userArray;

    RequestQueue requestQueue;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_coinflip);

        requestQueue = Volley.newRequestQueue(CoinFlipActivity.this);

        Intent inIntent = getIntent();
        username = inIntent.getStringExtra("USERNAME");
        userID = inIntent.getIntExtra("UUID", -1);
        lobbyID = inIntent.getIntExtra("LOBBYID",-1);



        getXMLIDs();
        getUserChips();
        setNumHands();

        currBetText.setText(currBet.toString());
        coinText.setText("Start Game");


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
            @Override
            public void onClick(View view) {
                currBet += 10;
                currBetText.setText(currBet.toString());
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

        betBtn.setOnClickListener(v -> {

            String msgStr = "#COINFLIP: BET " + currBet.toString();

            Intent intent = new Intent("SendWebSocketMessage");
            intent.putExtra("key", "chat1");
            intent.putExtra("message", msgStr);
            LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
        });

        headsBtn.setOnClickListener(v -> {
            String msgStr = "#COINFLIP: PICK HEADS";

            Intent intent = new Intent("SendWebSocketMessage");
            intent.putExtra("key", "chat1");
            intent.putExtra("message", msgStr);
            LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

        });

        tailsBtn.setOnClickListener(v -> {
            String msgStr = "#COINFLIP: PICK TAILS";

            Intent intent = new Intent("SendWebSocketMessage");
            intent.putExtra("key", "chat1");
            intent.putExtra("message", msgStr);
            LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

        });

        startBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startBtn.setVisibility(View.GONE);
                startGame();
            }
        });
        backBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                Intent i = new Intent(CoinFlipActivity.this,LobbyPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",userID);
                i.putExtra("LOBBYID",lobbyID);
                startActivity(i);
            }
        });
    }

    private void setNumHands() {

        JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.GET, "http://coms-3090-052.class.las.iastate.edu:8080/lobby/" + lobbyID, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {


                        try {
                            Integer size = response.getInt("size");
                            setNumPlayers(size);
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

    private void setNumPlayers(Integer np) {

        numPlayers = np;

        userArray = new CoinFlipUser[np];

        for (int i = 0; i < np; i++) {
            userArray[i] = new CoinFlipUser();

        }


    }

    private void getXMLIDs(){

        sendBtn = (Button) findViewById(R.id.csendBtn);
        chatToggleBtn = (Button) findViewById(R.id.cbackMainBtn);
        chatArea = findViewById(R.id.cchatView);
        msgEtx = (EditText) findViewById(R.id.cmsgEdt);
        msgTv = (TextView) findViewById(R.id.ctx1);
        backBtn = findViewById(R.id.cbackButton);

        raiseBet = findViewById(R.id.cRaiseBet);
        lowerBet = findViewById(R.id.cLowerBet);
        tailsBtn = findViewById(R.id.cTailsBtn);
        headsBtn = findViewById(R.id.cHeadsBtn);
        betBtn = findViewById(R.id.cBetBtn);
        startBtn = findViewById(R.id.cStartGame);
        currBetText = findViewById(R.id.cCurrBet);
        
        p1 = findViewById(R.id.cP1);
        p2 = findViewById(R.id.cP2);
        p3 = findViewById(R.id.cP3);
        p4 = findViewById(R.id.cP4);
        p5 = findViewById(R.id.cP5);
        p6 = findViewById(R.id.cP6);
        coinText = findViewById(R.id.cCoinText);
        playerChipText = findViewById(R.id.cChipText);




    }

    private void updateScreen() {
        p1.setText(userArray[0].getUsername() + " " + userArray[0].getPick() + " " + userArray[0].getBet().toString());
        p2.setText(userArray[1].getUsername() + " " + userArray[1].getPick() + " " + userArray[1].getBet().toString());
        if (numPlayers > 2) {
            p3.setText(userArray[2].getUsername() + " " + userArray[2].getPick() + " " + userArray[2].getBet().toString());
        }
        if (numPlayers > 3) {
            p3.setText(userArray[3].getUsername() + " " + userArray[3].getPick() + " " + userArray[3].getBet().toString());
        }
        if (numPlayers > 4) {
            p3.setText(userArray[4].getUsername() + " " + userArray[4].getPick() + " " + userArray[4].getBet().toString());
        }
        if (numPlayers > 5) {
            p3.setText(userArray[5].getUsername() + " " + userArray[5].getPick() + " " + userArray[5].getBet().toString());
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

        playerChips = chips;
        playerChipText.setText("Chips: " + chips.toString());
    }

    private void updateChips() {

        Integer newChipAmt = 0;

        for (CoinFlipUser user: userArray) {

            if (user.getUsername().equals(username)){
                    newChipAmt = user.getBet();
            }
        }

        String url = "http://coms-3090-052.class.las.iastate.edu:8080/chips/add/"+userID+"/"+newChipAmt;
        System.out.println("Adding or removing: " + newChipAmt.toString());


        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.PUT, url, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                                getUserChips();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        error.printStackTrace();
                        Toast.makeText(getApplicationContext(), "Error sending request", Toast.LENGTH_LONG).show();
                    }
                }
        );

        requestQueue.add(jsonObjectRequest);

    }

    private void startGame() {

        p1.setVisibility(View.VISIBLE);
        p2.setVisibility(View.VISIBLE);
        p3.setVisibility(View.VISIBLE);
        p4.setVisibility(View.VISIBLE);
        p5.setVisibility(View.VISIBLE);
        p6.setVisibility(View.VISIBLE);

        if (numPlayers < 6) {
            p6.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 5) {
            p5.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 4) {
            p4.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 3) {
            p3.setVisibility(View.INVISIBLE);
        }
        if (numPlayers < 2) {
            p2.setVisibility(View.INVISIBLE);
        }




        Intent intent = new Intent("SendWebSocketMessage");
        intent.putExtra("key", "chat1");
        intent.putExtra("message", "#COINFLIP: BET 0");
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);





    }

    private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String key = intent.getStringExtra("key");
            if ("chat1".equals(key)) {
                String message = intent.getStringExtra("message");

                if (message.contains("#COINFLIP")) {
                    String[] commands = message.split("\n");

                    getUserChips();

                    for (String cmd : commands) {
                        System.out.println(cmd);

                        if (cmd.contains("COIN")){
                            String coin = cmd.substring(cmd.indexOf(":")+1,cmd.length());
                            coinText.setText(coin);

                        }
                        if (cmd.contains("CALLS")){
                            String[] users = cmd.substring(cmd.indexOf(":")+1,cmd.length()).split(",");
                            for (int i = 0; i < users.length; i++) {
                                String[] info = users[i].split(" ");
                                System.out.println(Arrays.toString(info));

                                userArray[i].setUsername(info[1]);
                                userArray[i].setPick(info[2]);

                            }

                        }
                        if (cmd.contains("BETS")){
                            String[] users = cmd.substring(cmd.indexOf(":")+1,cmd.length()).split(",");
                            for (int i = 0; i < users.length; i++) {
                                String[] info = users[i].split(" ");
                                System.out.println(Arrays.toString(info));

                                userArray[i].setBet(Integer.parseInt(info[2]));

                            }

                        }
                        if (cmd.contains("GAME")){
                            if (cmd.contains("OVER")) {
                                updateChips();
                            }

                        }

                    }
                    updateScreen();

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
