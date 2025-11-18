package com.example.cycino;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;

public class GameChatActivity extends AppCompatActivity {

    private Button sendBtn, backMainBtn;
    private EditText msgEtx;
    private TextView msgTv;
    private TextView gameArea;
    private ScrollView chatArea;

    private boolean chatOpen = true;
    private String serverURL = "ws://coms-3090-052.class.las.iastate.edu:8080/chat/";
    private Integer lobbyID;
    private String username;

    /**
     * @param savedInstanceState
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gamechat);

        /* initialize UI elements */
        sendBtn = (Button) findViewById(R.id.bsendBtn);
        backMainBtn = (Button) findViewById(R.id.bbackMainBtn);
        msgEtx = (EditText) findViewById(R.id.bmsgEdt);
        msgTv = (TextView) findViewById(R.id.btx1);
        gameArea = findViewById(R.id.gameArea);
        chatArea = findViewById(R.id.chatView);

        gameArea.setBackgroundColor(0xFF00FF00);

        String serverUrl = serverURL + username;

        // start Websocket service with key "chat1"
        Intent serviceIntent = new Intent(this, WebSocketService.class);
        serviceIntent.setAction("CONNECT");
        serviceIntent.putExtra("key", "chat1");
        serviceIntent.putExtra("url", serverUrl);
        startService(serviceIntent);

        /* send button listener */
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
        backMainBtn.setOnClickListener(view -> {

            if (chatOpen) {
                sendBtn.setVisibility(View.GONE);
                msgEtx.setVisibility(View.GONE);
                chatArea.setVisibility(View.GONE);
                backMainBtn.setText("Open Chat");

                chatOpen = false;
            } else {

                sendBtn.setVisibility(View.VISIBLE);
                msgEtx.setVisibility(View.VISIBLE);
                chatArea.setVisibility(View.VISIBLE);
                backMainBtn.setText("Close Chat");

                chatOpen = true;

            }




            // got to chat activity

        });

    }

    // For receiving messages
    // only react to messages with tag "chat1"
    private BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String key = intent.getStringExtra("key");
            if ("chat1".equals(key)) {
                String message = intent.getStringExtra("message");
                runOnUiThread(() -> {
                    String s = msgTv.getText().toString();
                    msgTv.setText(s + message + "\n");
                    chatArea.fullScroll(View.FOCUS_DOWN);



                });
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