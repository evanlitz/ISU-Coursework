package com.example.cycino;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;

public class BaccaratActivity extends AppCompatActivity {

    private int userChips ;
    private int userID  ;
    private String userUsername  ;
    private int lobbyID ;
    private Button sendBtn, chatToggleBtn, tieBtn, bankerBtn, playerBtn, betButton, backButton, resetButton;
    private EditText msgEtx, betEditText;
    private TextView msgTv, winnerTv, playerLabel, bankerLabel, playerScoreTv, bankerScoreTv, chipCountText;
    private ImageView playerCard1, playerCard2, playerCard3, bankerCard1, bankerCard2, bankerCard3 ;
    private ScrollView chatArea;
    private boolean chatOpen = true;
    private String serverURL;
    private int playerCardCount ;
    private int bankerCardCount ;
    private RequestQueue requestQueue;
    private String removeChipsUrl, addChipsUrl, getChipsUrl ;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_baccarat);

        // Initialize chat components
        sendBtn = findViewById(R.id.sendBtn);
        chatToggleBtn = findViewById(R.id.toggleChat);
        msgEtx = findViewById(R.id.msgEdt);
        msgTv = findViewById(R.id.tx1);
        chatArea = findViewById(R.id.chatView);
        tieBtn = findViewById(R.id.tieButton);
        playerBtn = findViewById(R.id.playerButton);
        bankerBtn = findViewById(R.id.bankerButton);
        playerCard1 = findViewById(R.id.playerCard1);
        playerCard2 = findViewById(R.id.playerCard2);
        playerCard3 = findViewById(R.id.playerCard3);
        bankerCard1 = findViewById(R.id.bankerCard1);
        bankerCard2 = findViewById(R.id.bankerCard2);
        bankerCard3 = findViewById(R.id.bankerCard3);
        betEditText = findViewById(R.id.betEditText);
        betButton = findViewById(R.id.betButton);
        winnerTv = findViewById(R.id.winnerTextView);
        playerLabel = findViewById(R.id.playerLabel);
        bankerLabel = findViewById(R.id.bankerLabel);
        playerScoreTv = findViewById(R.id.playerScore);
        bankerScoreTv = findViewById(R.id.bankerScore);
        chipCountText = findViewById(R.id.chipCountText);
        requestQueue = Volley.newRequestQueue(this);
        backButton = findViewById(R.id.backButton);
        resetButton = findViewById(R.id.resetButton);



        playerBtn.setVisibility(View.GONE);
        bankerBtn.setVisibility(View.GONE);
        tieBtn.setVisibility(View.GONE);

        Intent inIntent = getIntent();
        userUsername = inIntent.getStringExtra("USERNAME");
        userID = inIntent.getIntExtra("UUID",-1);
        lobbyID = inIntent.getIntExtra("LOBBYID",-2);

        addChipsUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/add/" + userID + "/" ;
        removeChipsUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/remove/" + userID + "/" ;
        getChipsUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/get/" + userID ;
        serverURL = "ws://coms-3090-052.class.las.iastate.edu:8080/chat/" + lobbyID + "/" + userUsername;





        String serverUrl = serverURL ;
        Intent serviceIntent = new Intent(this, WebSocketService.class);
        serviceIntent.setAction("CONNECT");
        serviceIntent.putExtra("key", "chat1");
        serviceIntent.putExtra("url", serverUrl);
        startService(serviceIntent);

        setChips(getChipsUrl) ;

        betButton.setOnClickListener(v -> {
            String betAmountString = betEditText.getText().toString().trim();

            // Check if the input is not empty and is a valid integer
            if (!betAmountString.isEmpty()) {
                try {
                    int betAmount = Integer.parseInt(betAmountString); // Parse input as integer

                    if (betAmount > 0 && betAmount <= userChips) {

                        handleBet(betAmount) ;

                    } else {
                        // Notify the user that the bet must be greater than 0
                        Toast.makeText(this, "Bet must be a valid number", Toast.LENGTH_SHORT).show();
                    }
                } catch (NumberFormatException e) {
                    // Notify the user that the input is not a valid integer
                    Toast.makeText(this, "Please enter a valid integer", Toast.LENGTH_SHORT).show();
                }
            } else {
                // Notify the user to enter a bet
                Toast.makeText(this, "Please enter a bet", Toast.LENGTH_SHORT).show();
            }
        });

        // Set up send button listener
        sendBtn.setOnClickListener(v -> {
            String msgStr = msgEtx.getText().toString();
            if (!msgStr.isEmpty()) {
                Intent intent = new Intent("SendWebSocketMessage");
                intent.putExtra("key", "chat1");
                intent.putExtra("message", msgStr);
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
                msgEtx.setText("");
            }
        });

        // Toggle chat visibility
        chatToggleBtn.setOnClickListener(v -> {
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

        backButton.setOnClickListener(v -> {
            Intent i = new Intent(BaccaratActivity.this,HomePageActivity.class);
            i.putExtra("USERNAME", userUsername);
            i.putExtra("UUID", userID);
            startActivity(i);
        });

        tieBtn.setOnClickListener(v -> handleDecision("TIE"));
        playerBtn.setOnClickListener(v -> handleDecision("PLAYER"));
        bankerBtn.setOnClickListener(v -> handleDecision("BANKER"));

        resetButton.setOnClickListener(v -> {
            resetGame() ;
        });

    }

    // BroadcastReceiver for receiving WebSocket messages
    private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String key = intent.getStringExtra("key");

            if ("chat1".equals(key)) {
                String message = intent.getStringExtra("message");

                if (message != null) {
                    // Check if the message starts with #BACCARAT
                    if (message.startsWith("#BACCARAT")) {
                        handleBaccaratMessage(message); // Handle game-specific logic
                    } else if (!message.contains("DONOTSEND")) {
                        // Display other messages in chat
                        runOnUiThread(() -> {
                            String s = msgTv.getText().toString();
                            msgTv.setText(s + message + "\n");
                            chatArea.fullScroll(View.FOCUS_DOWN);
                        });
                    }
                }
            }
        }
    };

    private void handleBaccaratMessage(String gameInfo) {
        // Trim the entire message to remove leading and trailing newlines
        gameInfo = gameInfo.trim();

        // Split the message by newlines
        String[] lines = gameInfo.split("\\r?\\n");

        // Debugging: Print each line to verify its content
        for (String line : lines) {
            line = line.trim(); // Ensure each line is trimmed
            Log.d("BaccaratActivity", "Line: [" + line + "]");
        }

        // Initialize variables
        String gameState = null;
        String calls = null;
        String bets = null ;
        String playerScore = null ;
        String bankerScore = null ;
        String gameResult = null ;
        String playerCards = null ;
        String bankerCards = null ;

        // Parse each line
        for (String line : lines) {
            if (line.contains("GAMESTATE:")) {
                gameState = line.substring(line.indexOf("GAMESTATE:") + "GAMESTATE:".length()).trim();
            } else if (line.contains("CALLS:")) {
                calls = line.substring(line.indexOf("CALLS:") + "CALLS:".length()).trim();
            } else if (line.contains("BETS:")) {
                bets = line.substring(line.indexOf("BETS:") + "BETS:".length()).trim();
            } else if (line.contains("PLAYER_HAND")) {
                playerScore = line.substring(line.indexOf("PLAYER_HAND") + "PLAYER_HAND".length()).trim();
            } else if (line.contains("BANKER_HAND")) {
                bankerScore = line.substring(line.indexOf("BANKER_HAND") + "BANKER_HAND".length()).trim();
            } else if (line.contains("GAMERESULT:")) {
                gameResult = line.substring(line.indexOf("GAMERESULT:") + "GAMERESULT:".length()).trim();
            } else if (line.contains("PLAYER")) {
                playerCards = line.substring(line.indexOf("PLAYER_CARDS") + "PLAYER_CARDS".length()).trim();
            } else if (line.contains("BANKER")) {
                bankerCards = line.substring(line.indexOf("BANKER_CARDS") + "BANKER_CARDS".length()).trim();
            }
        }

        // Handle null gameState
        if (gameState == null) {
            Log.e("BaccaratActivity", "Invalid message: GAMESTATE not found");
            Toast.makeText(this, "Error: Invalid game state", Toast.LENGTH_SHORT).show();
            return;
        }

        // Process gameState (example)
        if (gameState.equals("OVER")) {
            Log.d("BaccaratActivity", "Game is over. Starting reveal...");
            startCardReveal(playerCards, bankerCards, gameResult, playerScore, bankerScore, calls, bets);
        } else if (gameState.equals("ONGOING")) {
            Log.d("BaccaratActivity", "Game is ongoing. Waiting for backend simulation...");
        } else {
            Log.e("BaccaratActivity", "Unexpected gameState: " + gameState);
            Toast.makeText(this, "Error: Unexpected game state", Toast.LENGTH_SHORT).show();
        }
    }

    private void startCardReveal(String playerCards, String bankerCards, String gameResult, String playerScore, String bankerScore, String calls, String bets) {
        // Split the card strings
        String[] playerCardArray = playerCards.split(" ");
        String[] bankerCardArray = bankerCards.split(" ");

        // Initialize player and banker card counts
        playerCardCount = Integer.parseInt(playerCardArray[0]);
        bankerCardCount = Integer.parseInt(bankerCardArray[0]);

        Log.d("BaccaratActivity", ""+ playerCardCount);

        // Combine cards in the order they are revealed (player first)
        String[] cardSequence = new String[playerCardCount + bankerCardCount];
        boolean isPlayerTurn = true;
        int playerIndex = 1, bankerIndex = 1, sequenceIndex = 0;

        while (sequenceIndex < cardSequence.length) {
            if (isPlayerTurn && playerIndex <= playerCardCount) {
                cardSequence[sequenceIndex++] = "PLAYER " + playerCardArray[playerIndex++];
            } else if (!isPlayerTurn && bankerIndex <= bankerCardCount) {
                cardSequence[sequenceIndex++] = "BANKER " + bankerCardArray[bankerIndex++];
            }
            isPlayerTurn = !isPlayerTurn; // Alternate turns
        }

        // Start the sequential reveal
        revealCardsSequentially(cardSequence, gameResult, bankerScore, playerScore, calls, bets);
    }

    private void revealCardsSequentially(String[] cardSequence, String winner, String bankerScore, String playerScore, String calls, String bets) {
        // ImageViews for player and banker cards
        ImageView[] playerCardViews = {playerCard1, playerCard2, playerCard3};
        ImageView[] bankerCardViews = {bankerCard1, bankerCard2, bankerCard3};

        // Use a Handler for timed reveals
        Handler handler = new Handler();
        int totalDelay = 0; // Initialize total delay

        for (int i = 0; i < cardSequence.length; i++) {
            final int delay = i * 1000; // 1-second delay between each card
            totalDelay = delay; // Track the total delay
            final int index = i;

            handler.postDelayed(() -> {
                String[] parts = cardSequence[index].split(" ");
                String who = parts[0];
                String cardName = parts[1];
                int resourceId = getResources().getIdentifier(cardName.toLowerCase(), "drawable", getPackageName());

                if (who.equals("PLAYER") && index / 2 < playerCardViews.length) {
                    if (resourceId != 0) {
                        playerCardViews[index / 2].setImageResource(resourceId);
                        playerCardViews[index / 2].setVisibility(View.VISIBLE);
                    } else {
                        Toast.makeText(this, "Player card not found: " + cardName, Toast.LENGTH_SHORT).show();
                    }
                } else if (who.equals("BANKER") && index / 2 < bankerCardViews.length) {
                    if (resourceId != 0) {
                        bankerCardViews[index / 2].setImageResource(resourceId);
                        bankerCardViews[index / 2].setVisibility(View.VISIBLE);
                    } else {
                        Toast.makeText(this, "Banker card not found: " + cardName, Toast.LENGTH_SHORT).show();
                    }
                }
            }, delay);
        }

        // Schedule the updateWinner call after the last card reveal
        handler.postDelayed(() -> {
            // Call updateWinner, parseCalls, and parseBets after 2 seconds
            updateWinner(winner, bankerScore, playerScore);

            // Parse the user's result and bet only after all cards are revealed
            String userResult = parseCalls(calls);
            int userBet = parseBets(bets);

            // Call handleResult after parsing the data
            handleResult(userResult, userBet);

            // Second delay for reset button visibility
            handler.postDelayed(() -> resetButton.setVisibility(View.VISIBLE), 2000);
        }, totalDelay + 2000); // Initial 2-second delay after cards are dealt
    }

    private void handleBet(int betAmount) {

        if (requestQueue == null) {
            Toast.makeText(this, "Request queue is not initialized.", Toast.LENGTH_SHORT).show();
            return;
        }

        String betStr = "#BACCARAT: BET " + betAmount;
        Intent checkConnectionIntent = new Intent("CheckWebSocketStatus");
        LocalBroadcastManager.getInstance(this).sendBroadcast(checkConnectionIntent);

        Intent intent = new Intent("SendWebSocketMessage");
        intent.putExtra("key", "chat1");
        intent.putExtra("message", betStr);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

        betEditText.setVisibility(View.GONE);
        betButton.setVisibility(View.GONE);

        playerBtn.setVisibility(View.VISIBLE);
        bankerBtn.setVisibility(View.VISIBLE);
        tieBtn.setVisibility(View.VISIBLE);

        Toast.makeText(this, "Bet placed: " + betAmount, Toast.LENGTH_SHORT).show();
        handleRemoveChips(betAmount, removeChipsUrl) ;
    }

    void updateWinner(String winner, String bankerScore, String playerScore) {
        winnerTv.setText("Winner: " + winner);
        winnerTv.setVisibility(View.VISIBLE); // Make it visible
        playerScoreTv.setText("Player Score: " + playerScore) ;
        bankerScoreTv.setText("Banker Score: " + bankerScore) ;
        playerScoreTv.setVisibility(View.VISIBLE) ;
        bankerScoreTv.setVisibility(View.VISIBLE) ;
    }


    private void handleDecision(String decision)
    {

        hideDecisionButtons() ;
        playerLabel.setVisibility(View.VISIBLE);
        bankerLabel.setVisibility(View.VISIBLE);
        String decStr =  "#BACCARAT: PICK " + decision ;
        Intent intent = new Intent("SendWebSocketMessage");
        intent.putExtra("key", "chat1");
        intent.putExtra("message", decStr);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
    }

    private void hideDecisionButtons()
    {
        tieBtn.setVisibility(View.GONE);
        playerBtn.setVisibility(View.GONE);
        bankerBtn.setVisibility(View.GONE);
    }


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

    private void setChips(String getChipsUrl)
    {
        JsonObjectRequest getRequest = new JsonObjectRequest(
                Request.Method.GET,
                getChipsUrl,
                null,
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            userChips = response.getInt("chips");
                            runOnUiThread(() -> chipCountText.setText("" + userChips));
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(getRequest);
    }

    private void handleAddChips(int addAmount, String addChipsUrl)
    {
        JsonObjectRequest putRequest = new JsonObjectRequest(
                Request.Method.PUT,
                addChipsUrl + addAmount,
                null, // No body for this request
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            userChips = response.getInt("chips");
                            chipCountText.setText("" + userChips);
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle errors
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(putRequest);
    }



    private void handleRemoveChips(int removeAmount, String removeChipsUrl)
    {
        JsonObjectRequest putRequest = new JsonObjectRequest(
                Request.Method.PUT,
                removeChipsUrl + removeAmount,
                null, // No body for this request
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            userChips = response.getInt("chips");
                            chipCountText.setText("" + userChips);
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle errors
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(putRequest);
    }

    private String parseCalls(String calls) {
        String[] callParts = calls.split(" ");

        // Iterate through the parts to find the username
        for (int i = 0; i < callParts.length; i += 2) {
            String currentUser = callParts[i];
            String result = callParts[i + 1];

            // Check if the current username matches
            if (currentUser.equals(userUsername)) {
                return result; // Return the result (e.g., "WON", "LOST", "TIE")
            }
        }
        // Return "Not Found" if the username is not in CALLS
        return "Not Found";
    }

    private int parseBets(String bets) {
        // Split the BETS string into parts
        String[] betParts = bets.split(" ");

        // Iterate through the parts to find the username and their bet
        for (int i = 0; i < betParts.length; i += 2) {
            String currentUser = betParts[i];
            String betAmount = betParts[i + 1];

            // Check if the current username matches
            if (currentUser.equals(userUsername)) {
                try {
                    return Integer.parseInt(betAmount); // Parse and return the bet amount as an integer
                } catch (NumberFormatException e) {
                    Log.e("BaccaratActivity", "Error parsing bet amount: " + betAmount);
                    return -1; // Return -1 to indicate an error
                }
            }
        }
        return -1;
    }



    private void handleResult(String userResult, int userBet)
    {
        if(userResult.equals("WIN"))
        {
            handleAddChips(userBet, addChipsUrl) ;
            chipCountText.setText("" + userChips);
            Toast.makeText(this, "Congrats! You just won" + userBet + "cyChips!", Toast.LENGTH_LONG).show();
        }
        else if(userResult.equals("LOST"))
        {
            Toast.makeText(this, "Better luck next time!", Toast.LENGTH_LONG).show();
        }
        else {
            Toast.makeText(this, "Error with calls." , Toast.LENGTH_SHORT).show();
        }
    }

    private void resetGame() {
        // Set all card ImageViews to invisible
        playerCard1.setVisibility(View.INVISIBLE);
        playerCard2.setVisibility(View.INVISIBLE);
        playerCard3.setVisibility(View.INVISIBLE);
        bankerCard1.setVisibility(View.INVISIBLE);
        bankerCard2.setVisibility(View.INVISIBLE);
        bankerCard3.setVisibility(View.INVISIBLE);

        // Set the winner TextView to invisible
        winnerTv.setVisibility(View.INVISIBLE);

        // Set the player and banker score TextViews to invisible
        playerScoreTv.setVisibility(View.INVISIBLE);
        bankerScoreTv.setVisibility(View.INVISIBLE);
        resetButton.setVisibility(View.INVISIBLE);

        // Make the bet EditText and bet Button visible
        betEditText.setVisibility(View.VISIBLE);
        betButton.setVisibility(View.VISIBLE);

        // Optionally clear any existing text in the bet EditText
        betEditText.setText("");

        // Show a toast message to indicate the game has been reset
        Toast.makeText(this, "Game has been reset. Place your bet!", Toast.LENGTH_SHORT).show();
    }


}