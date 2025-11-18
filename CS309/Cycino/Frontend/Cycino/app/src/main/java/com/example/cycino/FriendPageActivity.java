package com.example.cycino;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

/**
 * The FriendPageActivity allows you to see all of your followers and interact with them
 * Supports adding, removing and muting followers
 * Has buttons to go to chat and view profile
 * @author Sam Craft
 * @author Evan Litzer
 */

public class FriendPageActivity extends AppCompatActivity {

    /**
     * Array of followerName TextViews
     */
    private TextView[] followerName;
    /**
     * TextView of current user Username
     */
    private TextView userName;
    /**
     * Back Button
     */
    private Button backButton;
    /**
     * Array of Buttons to go to chat
     */
    private Button[] chatButton;
    /**
     * Array of Buttons to go to Profile
     */
    private Button[] profileButton;
    /**
     * Array of LinearLayouts that hold each profile
     */
    private LinearLayout[] profileContainer;
    private RequestQueue requestQueue;

    private EditText addFriendEditText ;
    private Button addFriendBtn, removeFriendBtn ;

    /**
     * JSONArray of all of user's followers
     */
    JSONArray friends;
    /**
     * Array of user's follower's IDs
     */
    Integer[] friendsID;

    Integer userID;
    String username;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_friendpage);
        requestQueue = Volley.newRequestQueue(getApplicationContext());
        addFriendBtn = findViewById(R.id.addFriendButton);
        removeFriendBtn = findViewById(R.id.unfriendButton);
        addFriendEditText = findViewById(R.id.addFriendEditText);



        backButton = findViewById(R.id.backButton);
        followerName = new TextView[]{
                findViewById(R.id.friend1Name),
                findViewById(R.id.friend2Name),
                findViewById(R.id.friend3Name),
                findViewById(R.id.friend4Name),
                findViewById(R.id.friend5Name),
                findViewById(R.id.friend6Name),
                findViewById(R.id.friend7Name),
        };

        chatButton = new Button[]{
                findViewById(R.id.friend1Chat),
                findViewById(R.id.friend2Chat),
                findViewById(R.id.friend3Chat),
                findViewById(R.id.friend4Chat),
                findViewById(R.id.friend5Chat),
                findViewById(R.id.friend6Chat),
                findViewById(R.id.friend7Chat),
        };

        profileButton = new Button[]{
                findViewById(R.id.friend1Profile),
                findViewById(R.id.friend2Profile),
                findViewById(R.id.friend3Profile),
                findViewById(R.id.friend4Profile),
                findViewById(R.id.friend5Profile),
                findViewById(R.id.friend6Profile),
                findViewById(R.id.friend7Profile),
        };

        profileContainer = new LinearLayout[] {
                findViewById(R.id.friend1LL),
                findViewById(R.id.friend2LL),
                findViewById(R.id.friend3LL),
                findViewById(R.id.friend4LL),
                findViewById(R.id.friend5LL),
                findViewById(R.id.friend6LL),
                findViewById(R.id.friend7LL),
        };

        userName = findViewById(R.id.userName);

        friendsID = new Integer[7];

        Intent intent = getIntent();
        userID = intent.getIntExtra("UUID",-1);
        username = intent.getStringExtra("USERNAME");

        userName.setText(username + "'s Following List:");

        getFollowerList(userID);

        addFriendBtn.setOnClickListener(v -> {
            String friendInput = addFriendEditText.getText().toString().trim();
            getUserByUsername(friendInput) ;
            addFriendEditText.setText("") ;
        });
        removeFriendBtn.setOnClickListener(v -> {
            String friendInput = addFriendEditText.getText().toString().trim();
            getUserByUsernameRemove(friendInput) ;
            addFriendEditText.setText("") ;
        });


        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent i = new Intent(FriendPageActivity.this,HomePageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",userID);
                startActivity(i);
            }
        });

        profileButton[0].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[0]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[1].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[1]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[2].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[2]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[3].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[3]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[4].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[4]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[5].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[5]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });
        profileButton[6].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, ViewFriendActivity.class);
                intent.putExtra("UUID",friendsID[6]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });

        chatButton[0].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[0]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);
            }
        });

        chatButton[1].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[1]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });

        chatButton[2].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[2]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });

        chatButton[3].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[3]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });

        chatButton[4].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[4]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);

            }
        });

        chatButton[5].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[5]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);
            }
        });
        chatButton[6].setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FriendPageActivity.this, FriendChatActivity.class);
                intent.putExtra("UUID",friendsID[6]);
                intent.putExtra("lUUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent);
            }
        });
    }

    /**
     * Gets the list of followers for a specific user ID
     * @param userID
     */
    public void getFollowerList(final int userID) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + userID + "/following";

        JsonArrayRequest jsonArrayRequest = new JsonArrayRequest(
                Request.Method.GET, url, null,
                response -> {
                    try {
                        // Clear the current UI first
                        clearFollowerListUI();

                        friends = response;
                        showUserEntries(response.length());
                        for (int i = 0; i < response.length(); i++) {
                            JSONObject follower = response.getJSONObject(i);
                            Integer followingId = follower.getInt("followingID");
                            friendsID[i] = followingId;
                            getUserName(followingId, i); // Fetch and set the username
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        Toast.makeText(getApplicationContext(), "Error parsing JSON data", Toast.LENGTH_LONG).show();
                    }
                },
                error -> {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Error fetching data", Toast.LENGTH_LONG).show();
                }
        );

        requestQueue.add(jsonArrayRequest);
    }

    /**
     *
     * Follows another user by entering both the current user's ID, and the ID of the user that is attempting to be followed.
     * @param userID
     * @param followingID
     *
     *
     */
    private void followUser(final int userID, final int followingID) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + userID + "/follow";

        // Create the JSON object for the request body
        JSONObject followBody = new JSONObject();
        try {
            followBody.put("followingID", followingID);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.POST, url, followBody,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 OK")) {
                                Toast.makeText(getApplicationContext(), "Successfully followed user " + followingID, Toast.LENGTH_SHORT).show();
                                // Refresh the follower list to reflect the update
                                getFollowerList(userID);
                            } else {
                                Toast.makeText(getApplicationContext(), "Failed to follow user " + followingID, Toast.LENGTH_SHORT).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing response", Toast.LENGTH_LONG).show();
                        }
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



    /**
     * Gets the usernames of all of the user's followers.
     * @param id
     * @param loopI
     *
     */
    private void getUserName(Integer id, Integer loopI) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + id;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.GET, url, null,
                response -> {
                    try {
                        // Set the username in the TextView instead of first and last name
                        String username = response.getString("username");
                        followerName[loopI].setText(username);
                        profileContainer[loopI].setVisibility(View.VISIBLE); // Ensure container is visible
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                },
                error -> {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Error fetching user data", Toast.LENGTH_LONG).show();
                }
        );

        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }

    /**
     * Enables the correct amount of user templates for the page
     * @param numEntries
     *
     */
    private void showUserEntries(int numEntries) {
        for (int i = 0; i < numEntries; i++) {
            profileContainer[i].setVisibility(View.VISIBLE);

        }
    }

    private void getUserByUsername(String username) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/contains/" + username;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.GET, url, null,
                response -> {
                    try {
                        // Extract the "user" object from the response
                        JSONObject userObject = response.getJSONObject("user");

                        // Extract user details from the "user" object
                        int followingID = userObject.getInt("id");
                        String firstName = userObject.getString("firstName");
                        String lastName = userObject.getString("lastName");

                        // Display a toast message with the user details
                        Toast.makeText(getApplicationContext(), "User: " + firstName + " " + lastName, Toast.LENGTH_SHORT).show();

                        // Call followUser with the extracted followingID
                        followUser(userID, followingID);

                    } catch (JSONException e) {
                        Toast.makeText(getApplicationContext(), "Error parsing response in getUserByUsername.", Toast.LENGTH_LONG).show();
                    }
                },
                error -> {
                    // Handle error
                    Toast.makeText(getApplicationContext(), "Username not found or request failed.", Toast.LENGTH_SHORT).show();
                }
        );

        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }

    private void getUserByUsernameRemove(String username) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/contains/" + username;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.GET, url, null,
                response -> {
                    try {
                        // Extract the "user" object from the response
                        JSONObject userObject = response.getJSONObject("user");

                        // Extract user details from the "user" object
                        int followingID = userObject.getInt("id");
                        String firstName = userObject.getString("firstName");
                        String lastName = userObject.getString("lastName");

                        // Display a toast message with the user details
                        Toast.makeText(getApplicationContext(), "User: " + firstName + " " + lastName, Toast.LENGTH_SHORT).show();

                        // Call followUser with the extracted followingID
                        unfollowUser(userID, followingID);

                    } catch (JSONException e) {
                        Toast.makeText(getApplicationContext(), "Error parsing response in getUserByUsername.", Toast.LENGTH_LONG).show();
                    }
                },
                error -> {
                    // Handle error
                    Toast.makeText(getApplicationContext(), "Username not found or request failed.", Toast.LENGTH_SHORT).show();
                }
        );

        // Add the request to the RequestQueue
        requestQueue.add(jsonObjectRequest);
    }

    private void unfollowUser(final int userID, final int unfollowingID) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/" + userID + "/unfollow/" + unfollowingID;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.DELETE, url, null,
                response -> {
                    try {
                        String status = response.getString("status");
                        if (status.equals("200 OK")) {
                            Toast.makeText(getApplicationContext(), "Successfully unfollowed user " + unfollowingID, Toast.LENGTH_SHORT).show();
                            // Clear UI and fetch the updated follower list
                            clearFollowerListUI();
                            getFollowerList(userID);
                        } else {
                            Toast.makeText(getApplicationContext(), "Failed to unfollow user " + unfollowingID, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        Toast.makeText(getApplicationContext(), "Error parsing response", Toast.LENGTH_LONG).show();
                    }
                },
                error -> {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Error sending request", Toast.LENGTH_LONG).show();
                }
        );

        requestQueue.add(jsonObjectRequest);
    }

    private void clearFollowerListUI() {
        for (int i = 0; i < profileContainer.length; i++) {
            profileContainer[i].setVisibility(View.GONE); // Hide all containers
            followerName[i].setText(""); // Clear the text of follower names
            friendsID[i] = null; // Reset the friendsID array
        }
    }


}