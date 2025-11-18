package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
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

public class ViewFriendActivity extends AppCompatActivity {

    // Declare UI elements
    private MaterialButton backButton ;
    private ImageView profilePicture;
    private TextView usernameTV, userBioTV, userRoleTV, fullNameTV, phoneNumberTV;
    private String currentUsername ;
    private int currentUserID ;
    private int userID ;
    private RequestQueue requestQueue;
    public String serverUrl ;
    private String userFirstName, userLastName, userRole, userPhoneNumber, userBio, userUsername ;
    private int chips ;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_userpage); // Link to your XML layout

        Intent prevIntent = getIntent();
        currentUserID = prevIntent.getIntExtra("lUUID", -1); // Default to -1 if not found
        userID = prevIntent.getIntExtra("UUID", -1); // Default to -1 if not found
        currentUsername = prevIntent.getStringExtra("USERNAME");

        requestQueue = Volley.newRequestQueue(this);

        // Initialize UI elements
        backButton = findViewById(R.id.backButton);
        profilePicture = findViewById(R.id.profilePicture);
        usernameTV = findViewById(R.id.username);
        userBioTV = findViewById(R.id.userBio);
        userRoleTV = findViewById(R.id.userRole);
        fullNameTV = findViewById(R.id.fullName);
        phoneNumberTV = findViewById(R.id.phoneNumber);




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


        getUserInfo();

        backButton.setOnClickListener(v -> {
            Intent backIntent = new Intent(ViewFriendActivity.this, FriendPageActivity.class); // Replace FriendChatActivity with the correct previous activity class
            backIntent.putExtra("USERNAME", currentUsername);
            backIntent.putExtra("UUID", currentUserID);
            startActivity(backIntent);
            finish(); // Close the current activity
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

    private void setProfilePicture()
    {

    }



}
