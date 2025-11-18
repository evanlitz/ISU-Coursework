package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.material.button.MaterialButton;

import org.json.JSONException;

public class UserpageActivity extends AppCompatActivity {

    // Declare UI elements
    private MaterialButton backButton, chatButton, friendUserButton;
    private ImageView profilePicture;
    private TextView usernameTV, userBioTV, userRoleTV, fullNameTV, phoneNumberTV;
    private String userUsername ;
    private int userID ;
    private RequestQueue requestQueue;
    public String serverUrl ;
    private String userFirstName, userLastName, userRole, userPhoneNumber, userBio ;
    private int chips ;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_userpage); // Link to your XML layout

        requestQueue = Volley.newRequestQueue(this);

        // Initialize UI elements
        backButton = findViewById(R.id.backButton);
        profilePicture = findViewById(R.id.profilePicture);
        usernameTV = findViewById(R.id.username);
        userBioTV = findViewById(R.id.userBio);
        userRoleTV = findViewById(R.id.userRole);
        fullNameTV = findViewById(R.id.fullName);
        phoneNumberTV = findViewById(R.id.phoneNumber);





        Intent inIntent = getIntent();
        userUsername = inIntent.getStringExtra("USERNAME");
        userID = inIntent.getIntExtra("UUID",-1);

        getUserInfo();

        int[] profilePictures = {
                R.drawable.cycinopp1,
                R.drawable.cycinopp2,
                R.drawable.cycinopp3,
                R.drawable.cycinopp4,
                R.drawable.cycinopp5,
                R.drawable.cycinopp6,
                R.drawable.cycinopp7
        };

        int index = userID % profilePictures.length; // Ensure the index is within bounds
        profilePicture.setImageResource(profilePictures[index]);


        backButton.setOnClickListener(v -> {
            Intent backIntent = new Intent(UserpageActivity.this, FriendPageActivity.class); // Replace FriendChatActivity with the correct previous activity class
            backIntent.putExtra("USERNAME", userUsername);
            backIntent.putExtra("lUUID", userID);
            startActivity(backIntent);
            finish();


        }); // Close the activity and go back

        chatButton.setOnClickListener(view -> {
            // Placeholder for starting chat activity
            Toast.makeText(this, "Chat feature coming soon!", Toast.LENGTH_SHORT).show();
        });

        friendUserButton.setOnClickListener(view -> {
            // Placeholder for "Friend User" action
            Toast.makeText(this, "User added as a friend!", Toast.LENGTH_SHORT).show();
        });

        // Placeholder for profile picture click event
        profilePicture.setOnClickListener(view -> {
            // Show preset image selection dialog or perform other action
            Toast.makeText(this, "Change Profile Picture coming soon!", Toast.LENGTH_SHORT).show();
        });
    }

    private void setUserInfo()
    {
        usernameTV.setText(userUsername);
        fullNameTV.setText(userFirstName + " " + userLastName) ;
        userBioTV.setText(userBio) ;
        userRoleTV.setText(userRole) ;
        phoneNumberTV.setText(userPhoneNumber) ;
    }

    private void getUserInfo() {
        serverUrl = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + userID;
        JsonObjectRequest getRequest = new JsonObjectRequest(
                Request.Method.GET,
                serverUrl,
                null,
                response -> {
                    try {
                        // Extract fields directly from the response JSON
                        userUsername = response.getString("username");
                        userFirstName = response.getString("firstName");
                        userLastName = response.getString("lastName");
                        userPhoneNumber = response.getString("phoneNumber");
                        chips = response.getInt("chips");
                        userRole = response.getString("role");
                        userBio = response.getString("userBiography");

                        // Call setUserInfo to update the UI
                        setUserInfo();

                    } catch (JSONException e) {
                        // Handle JSON parsing errors
                        Toast.makeText(this, "Response parsing error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle request errors
                    Toast.makeText(this, "Request failed. Please check your connection.", Toast.LENGTH_SHORT).show();
                }
        );

        // Add the request to the queue
        requestQueue.add(getRequest);
    }



}
