package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import android.view.View;
import android.widget.Button;
import android.widget.EditText;
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

public class HomePageActivity extends AppCompatActivity {

    private Button startLobby,joinLobby, leaderboard,friends,settings,logout, rulesBtn, bankBtn;
    private TextView userNameText, chipText;
    private EditText joinID;
    RequestQueue requestQueue;

    private String username;
    private Integer UUID;

    /**
     * @param savedInstanceState
     */
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_homepage);

        Intent intent = getIntent();
        username = intent.getStringExtra("USERNAME");
        UUID = intent.getIntExtra("UUID",-1);

        requestQueue = Volley.newRequestQueue(HomePageActivity.this);

        startLobby = findViewById(R.id.lobbyButton);
        joinLobby = findViewById(R.id.joinLobbyButton);
        joinID = findViewById(R.id.joinLobbyID);
        leaderboard = findViewById(R.id.leaderboardButton);
        friends = findViewById(R.id.friendsButton);
        settings = findViewById(R.id.settingsButton);
        rulesBtn = findViewById(R.id.rulesButton);
        bankBtn = findViewById(R.id.bankButton);

        userNameText = findViewById(R.id.hpUsername);
        chipText = findViewById(R.id.hpChips);

        //username = "Sam";
        //UUID = 4;
        //userNameText.setText("LOG IN BYPASSED");
        userNameText.setText(username);
        getOneUser(UUID);

        startLobby.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,LobbyPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);

            }
        });

        joinLobby.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                int lobbyID = Integer.parseInt(joinID.getText().toString());
                Intent i = new Intent(HomePageActivity.this,LobbyPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                i.putExtra("LOBBYID",lobbyID);
                startActivity(i);
            }
        });
        leaderboard.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,LeaderboardActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);

            }
        });
        friends.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,FriendPageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);

            }
        });
        settings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,MainSettingsActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);

            }
        });
        rulesBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,RulesActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);
            }
        });

        bankBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(HomePageActivity.this,BankActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",UUID);
                startActivity(i);
            }
        });


    }
    private void getOneUser(Integer id) {
        //String url = "https://10c011fe-3b08-4ae2-96a7-71049edb34ae.mock.pstmn.io/getData";
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/"+id;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Toast.makeText(getApplicationContext(),"view worked", Toast.LENGTH_LONG).show();

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
        chipText.setText("Chips: " + chips.toString());
    }
}
