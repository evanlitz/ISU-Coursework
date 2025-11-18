package com.example.cycino;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
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
import org.json.JSONObject;

public class FriendChatActivity extends AppCompatActivity {

    private Button backButton;
    private Button friendNameButton;
    private Button sendButton;
    private EditText messageEditText;
    private ScrollView chatScrollView;
    private LinearLayout chatContainer;
    private int userID ;
    private String username ;
    private String serverURL;
    private int recipientID  ;
    private boolean isNotificationsOn ;
    private RequestQueue requestQueue ;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_friendchat); // Ensure this matches your XML filename
        requestQueue = Volley.newRequestQueue(getApplicationContext());

        Intent prevIntent = getIntent();
        userID = prevIntent.getIntExtra("lUUID", -1); // Default to -1 if not found
        recipientID = prevIntent.getIntExtra("UUID", -1); // Default to -1 if not found
        username = prevIntent.getStringExtra("USERNAME");

        getUserByUserID(recipientID) ;

        // Initialize UI elements
        backButton = findViewById(R.id.backButton);
        friendNameButton = findViewById(R.id.friendNameButton);
        sendButton = findViewById(R.id.sendButton);
        messageEditText = findViewById(R.id.messageEditText);
        chatScrollView = findViewById(R.id.chatScrollView);
        chatContainer = findViewById(R.id.chatContainer);
        requestQueue = Volley.newRequestQueue(getApplicationContext());

        String recipientSR = "@" + recipientID + " " ; // SET WHEN USER CLICKS ON CHAT WITH SPECIFIC FRIEND

        String serverUrl = "ws://coms-3090-052.class.las.iastate.edu:8080/directMessaging/" + userID;

        Intent intent = new Intent(this, WebSocketService.class);
        intent.setAction("CONNECT");
        intent.putExtra("key", "chat2");
        intent.putExtra("url", serverUrl);
        startService(intent);

        sendButton.setOnClickListener(v -> {
            String messageContent = messageEditText.getText().toString().trim();
            if (!messageContent.isEmpty()) {
                String message = recipientSR + messageContent;

                Intent sendIntent = new Intent("SendWebSocketMessage");
                sendIntent.putExtra("key", "chat2");
                sendIntent.putExtra("message", message);
                LocalBroadcastManager.getInstance(this).sendBroadcast(sendIntent);

                messageEditText.setText("");
            } else {
                Toast.makeText(FriendChatActivity.this, "Please enter a message.", Toast.LENGTH_SHORT).show();
            }
        });
        // Set up click listeners
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish(); // Closes the activity and returns to the previous screen
            }
        });

        friendNameButton.setOnClickListener(v -> {
            Intent fcIntent = new Intent(FriendChatActivity.this, HomePageActivity.class); //////////////////////

            fcIntent.putExtra("USER_ID", userID); // Current user's ID
            fcIntent.putExtra("USERNAME", username); // Current user's username
            fcIntent.putExtra("FRIEND_ID", recipientID); // Friend's user ID

            startActivity(fcIntent);
        });



        }

    private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String key = intent.getStringExtra("key");
            if ("chat2".equals(key)) {
                String message = intent.getStringExtra("message");

                // Check if the message is from the current user
                if (!message.startsWith("[DM] " + userID + ":")) {
                    // Show a toast for a new message from the recipient
                    Toast.makeText(FriendChatActivity.this, "You've got a new message from " + recipientID, Toast.LENGTH_SHORT).show();

                    runOnUiThread(() -> addMessageToChat(message, false));
                } else {
                    // This is a sent message echo from the server
                    runOnUiThread(() -> addMessageToChat(message, true));
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

    private void addMessageToChat(String message, boolean isSentByUser) {
        // Parse the message to remove unnecessary details
        String formattedMessage = message;

        // Check and format the message if it starts with "[DM]"
        if (message.startsWith("[DM]")) {
            try {
                // Extract the actual message content (assuming this format: [DM] <userID>: @<recipientID> <message>)
                int colonIndex = message.indexOf(":");
                if (colonIndex != -1) {
                    // Get the part after the colon
                    formattedMessage = message.substring(colonIndex + 1).trim();

                    // Remove the "@<recipientID>" part if present
                    int atIndex = formattedMessage.indexOf("@");
                    if (atIndex != -1) {
                        int spaceIndex = formattedMessage.indexOf(" ", atIndex); // Find the space after "@<recipientID>"
                        if (spaceIndex != -1) {
                            formattedMessage = formattedMessage.substring(spaceIndex + 1).trim(); // Extract the message after "@<recipientID>"
                        }
                    }
                }
            } catch (Exception e) {
                formattedMessage = message; // Fallback in case of parsing issues
            }
        }

        // Create a new TextView for the message
        TextView messageTextView = new TextView(this);
        messageTextView.setText(formattedMessage); // Set the formatted message

        // Adjust font size and style
        messageTextView.setTextSize(18); // Increase font size (e.g., 18sp)
        messageTextView.setTypeface(null, android.graphics.Typeface.BOLD); // Make text bold
        messageTextView.setPadding(16, 12, 16, 12); // Adjust padding for better spacing

        // Set different styles for messages sent by user vs. received
        if (isSentByUser) {
            messageTextView.setBackgroundResource(R.drawable.sent_message_background); // Use a custom drawable for sent messages
            messageTextView.setTextColor(Color.WHITE);
            // Align the message to the right
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, 12, 0, 12); // Add more spacing between messages
            params.gravity = Gravity.END;
            messageTextView.setLayoutParams(params);
        } else {
            messageTextView.setBackgroundResource(R.drawable.received_message_background); // Use a custom drawable for received messages
            messageTextView.setTextColor(Color.BLACK);
            // Align the message to the left
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(0, 12, 0, 12); // Add more spacing between messages
            params.gravity = Gravity.START;
            messageTextView.setLayoutParams(params);
        }

        // Add the TextView to the chat container
        chatContainer.addView(messageTextView);

        // Scroll to the bottom of the ScrollView to show the new message
        chatScrollView.post(() -> chatScrollView.fullScroll(View.FOCUS_DOWN));
    }

    private void getUserByUserID(int userID) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + userID;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.GET, url, null,
                response -> {
                    try {
                        // Extract the username directly from the response
                        String username = response.getString("username");

                        // Set the username to the friendNameButton
                        friendNameButton.setText("" + username);

                    } catch (JSONException e) {
                        Toast.makeText(getApplicationContext(), "Error parsing response.", Toast.LENGTH_LONG).show();
                    }
                },
                error -> {
                    // Handle error
                    Toast.makeText(getApplicationContext(), "Failed to fetch user data. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );

        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }



}

