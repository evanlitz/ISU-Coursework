package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * The LobbyPageActivity is the main interface for managing a game lobby.
 * It allows users to see who’s currently in the lobby, add new players,
 * remove existing ones, or adjust settings as needed. There’s also an option to start the game
 * once everything is set up or delete the lobby entirely if plans change.
 *
 * The class handles most of the interactions between the user and the server for lobby management.
 * This includes adding/deleting players, starting a game, going to settings, etc.
 *
 * Players are displayed in a list, showing their usernames and roles in the game. The buttons are laid out for easy access,
 * covering everything a host might need to do in preparation for the game.
 *
 */
public class LobbyPageActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {

    /**
     * Button to start the game from the lobby.
     */
    private Button buttonStartGame;

    /**
     * Button to delete the lobby.
     */
    private Button buttonDeleteLobby;

    /**
     * Button to navigate back to the home screen.
     */
    private Button buttonBackToHome;

    /**
     * Button to open the settings page for the lobby.
     */
    private Button buttonChangeSettings;

    /**
     * ScrollView to display the list of users in the lobby.
     */
    private ScrollView scrollViewUserList;

    /**
     * LinearLayout container for dynamically displaying the list of users.
     */
    private LinearLayout userListContainer;

    RequestQueue queue;

    private Spinner selectedGame;
    private String currSelectedGame;

    private String username;

    private TextView lobbyNum;
    /**
     * ID of the current lobby.
     */
    private int lobbyID; // Temporary value for testing purposes.

    /**
     * ID of the current user.
     */
    private int currentUser;

    String url = "http://coms-3090-052.class.las.iastate.edu:8080/lobby/";

    /**
     * List of users currently in the lobby.
     */
    private ArrayList<JSONObject> userList = new ArrayList<>();



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lobbypage);

        queue = Volley.newRequestQueue(this);

        // Initialize UI elements
        buttonStartGame = findViewById(R.id.buttonStartGame);
        buttonDeleteLobby = findViewById(R.id.buttonDeleteLobby);
        buttonBackToHome = findViewById(R.id.buttonBackToHome);
        lobbyNum = findViewById(R.id.currLobbyID);
        buttonChangeSettings = findViewById(R.id.buttonChangeSettings);
        scrollViewUserList = findViewById(R.id.scrollViewUserList);
        userListContainer = findViewById(R.id.userListContainer);
        selectedGame = findViewById(R.id.gameSelection);


        selectedGame.setOnItemSelectedListener(this);

        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
                this,
                R.array.games_array,
                android.R.layout.simple_spinner_item
        );

        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        selectedGame.setAdapter(adapter);


        Intent i = getIntent();
        username = i.getStringExtra("USERNAME");
        currentUser = i.getIntExtra("UUID",-1);
        lobbyID = i.getIntExtra("LOBBYID",-1);

        // Load existing users in the lobby.


        if (lobbyID == -1) {
            createLobby();
        }

        else {
            addUserByID();
            lobbyNum.setText("Lobby: "+lobbyID);
        }




        /**
         * Sets up the "Add User" button.
         * When clicked, retrieves the username from the input field and attempts to add the user to the lobby.
         * Displays a message if the field is empty.
         */

        /**
         * Sets up the "Start Game" button.
         * When clicked, triggers a placeholder action to start the game.
         */
        buttonStartGame.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if(currSelectedGame.equals("Baccarat")) {
                    Intent i = new Intent(LobbyPageActivity.this, BaccaratActivity.class);
                    i.putExtra("USERNAME", username);
                    i.putExtra("UUID", currentUser);
                    i.putExtra("LOBBYID", lobbyID);
                    startActivity(i);
                }
                if(currSelectedGame.equals("Blackjack")) {

                        Intent i2 = new Intent(LobbyPageActivity.this,BlackjackActivity.class);
                        i2.putExtra("USERNAME",username);
                        i2.putExtra("UUID",currentUser);
                        i2.putExtra("LOBBYID",lobbyID);
                        startActivity(i2);
                }
                if(currSelectedGame.equals("Coinflip")) {
                        Intent i3 = new Intent(LobbyPageActivity.this,CoinFlipActivity.class);
                        i3.putExtra("USERNAME",username);
                        i3.putExtra("UUID",currentUser);
                        i3.putExtra("LOBBYID",lobbyID);
                        startActivity(i3);
                }
                if(currSelectedGame.equals("Poker")) {
                        Intent i4 = new Intent(LobbyPageActivity.this,PokerActivity.class);
                        i4.putExtra("USERNAME",username);
                        i4.putExtra("UUID",currentUser);
                        i4.putExtra("LOBBYID",lobbyID);
                        startActivity(i4);

                }

                Toast.makeText(LobbyPageActivity.this, "Starting game...", Toast.LENGTH_SHORT).show();
            }
        });

        /**
         * Sets up the "Delete Lobby" button.
         * When clicked, attempts to delete the current lobby using the lobby ID.
         */
        buttonDeleteLobby.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Placeholder for deleting lobby logic
                deleteLobby(lobbyID) ;
                Intent intent = new Intent(LobbyPageActivity.this, HomePageActivity.class);
                intent.putExtra("USERNAME",username);
                intent.putExtra("UUID",currentUser);
                startActivity(intent);
            }
        });

        /**
         * Sets up the "Back to Home" button.
         * When clicked, notifies the user and navigates back to the home screen.
         */
        buttonBackToHome.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Placeholder for navigating back to home
                Toast.makeText(LobbyPageActivity.this, "Going back to home", Toast.LENGTH_SHORT).show();
                Intent intent = new Intent(LobbyPageActivity.this, HomePageActivity.class);
                intent.putExtra("USERNAME",username);
                intent.putExtra("UUID",currentUser);
                removeUserByID();
                startActivity(intent);
            }
        });

        /**
         * Sets up the "Change Settings" button.
         * When clicked, notifies the user and navigates to the settings page.
         */
        buttonChangeSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Placeholder for changing settings
                Toast.makeText(LobbyPageActivity.this, "Opening settings", Toast.LENGTH_SHORT).show();
                Intent intent = new Intent(LobbyPageActivity.this, MainSettingsActivity.class); // CHANGE TO SIGNUP PAGE!!!!!
                startActivity(intent);
            }
        });
    }


    private void createLobby() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.POST, url+"create/"+currentUser, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        // Handle the successful response here
                        try {
                            String status = response.getString("status");
                            lobbyID = response.getInt("lobbyId");
                            lobbyNum.setText("Lobby: "+lobbyID);
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


        queue.add(jsonObjectRequest);
    }

    private void addUserByID() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"add/"+lobbyID+"/"+currentUser, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public synchronized void onResponse(JSONObject response) {
                        lobbyNum.setText("Lobby: "+lobbyID);
                        loadUsersInLobby(lobbyID);
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(), "view failed", Toast.LENGTH_LONG).show();
            }
        });
        queue.add(jsonObjectRequest);
    }

    private void removeUserByID() {
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url+"remove/"+lobbyID+"/"+currentUser, null,
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
        queue.add(jsonObjectRequest);
    }

    /**
     * Adds a user to the lobby's user list and dynamically updates the UI to display their information.
     * Creates a new TextView for the user, showing their username and role, and adds it to the user container.
     * This keeps the lobby interface up-to-date with the current players.
     *
     * @param user     The JSON object representing the user to be added.
     * @param username The username of the user being added.
     * @throws JSONException If there is an issue extracting the user's role from the JSON object.
     */
    private void addUserToList(JSONObject user, String username) throws JSONException {
        userList.add(user) ;
        android.widget.TextView userTextView = new android.widget.TextView(this);
        userTextView.setText("Username: " + username + "    Role: " + user.getString("role")) ;
        userTextView.setPadding(12, 12, 12, 12);
        userTextView.setTextSize(20);
        userListContainer.addView(userTextView);
    }

    /**
     * Attempts to add a user to the lobby by sending a PUT request to the server.
     * Checks if the user is already in the lobby before making the server call, avoiding duplicates.
     * If successful, the user is added to the local user list and displayed in the list.
     *
     * @param user          The JSON object representing the user to be added.
     * @param inputUsername The username of the user to be added to the lobby.
     * @throws JSONException If there is an issue extracting the user ID from the JSON object.
     */
    private void addUserToLobby(JSONObject user, String inputUsername) throws JSONException {
        int userID = user.getInt("id") ;
        for (JSONObject existingUser : userList) {
            if (existingUser.getInt("id") == userID) {
                Toast.makeText(this, "User is already in the lobby.", Toast.LENGTH_SHORT).show();
                return; // Exit to prevent adding duplicate
            }
        }
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/lobby/add/" + lobbyID + "/" + userID ;
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Processes the server's response to the PUT request.
                     * If successful, the user is added to the UI and the local user list.
                     * Otherwise, an error message is displayed to indicate the failure.
                     *
                     * @param response The JSON response from the server.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LobbyPage", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 ok")) {
                                addUserToList(user, inputUsername) ;
                                Toast.makeText(LobbyPageActivity.this, "User has been added to lobby.", Toast.LENGTH_SHORT).show();
                            }
                            else
                            {
                                Toast.makeText(LobbyPageActivity.this, "Failed to add user to lobby: Are they already in it?", Toast.LENGTH_LONG).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the PUT request.
                     * Logs the error details and displays a message notifying the user of the issue.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        if (error.networkResponse != null && error.networkResponse.data != null) {
                            String errorMsg = new String(error.networkResponse.data);
                            Log.e("VolleyError", errorMsg);
                        }
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                        error.printStackTrace();
                    }
                }) {
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * Sends a GET request to verfiy if a user with the specified username exists.
     * If the user is found, the method proceeds to add the user to current lobby.
     * Handles server responses, validates user existence, and provides feedback on errors and success.
     *
     * @param inputUsername The username of the user to be verified and added to the lobby.
     */
    private void getAddUser(String inputUsername)
    {
        // Construct the URL for the GET request
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/contains/" + inputUsername ;
        // Create a JSON object request to validate the user
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the GET request.
                     * If the user exists, retrieves the user object and calls addUserToLobby to add them to the lobby.
                     *
                     * @param response The JSON response from the server containing user details.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 ok")) {
                                JSONObject userObject = response.getJSONObject("user");
                                if (userObject != null) {
                                    addUserToLobby(userObject, inputUsername);
                                } else {
                                    // "user" key is missing in response
                                    Toast.makeText(getApplicationContext(), "User data is missing in the response.", Toast.LENGTH_SHORT).show();
                                }
                            }
                            else {
                                Toast.makeText(getApplicationContext(), "User not found", Toast.LENGTH_SHORT).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the GET request.
                     * Logs the error and displays a toast message notifying the user of the issue.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e("VolleyError", "Server error: " + error.getMessage());
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                    }

                }) {
            /**
             * Adds headers to the GET request, specifying the content type and accepted response type.
             *
             * @return A map containing the request headers.
             * @throws AuthFailureError If there is an authentication failure when setting headers.
             */
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json");
                headers.put("Accept", "application/json"); // If the server expects it
                return headers;
            }
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * Removes a user from the lobby's user list and updates the UI to reflect the change.
     * Iterates through the current user list to find the user with the specified ID.
     * If the user is found, it is removed from both the internal list and the displayed UI.
     * If the user is not found, a toast message notifies the caller.
     *
     * @param userId The unique identifier of the user to be removed from the lobby.
     * @throws JSONException If an error occurs while processing the JSON object structure.
     */
    private void deleteUserFromList(int userId) throws JSONException {
        // Iterate through the userList to find the user with the given ID
        for (int i = 0; i < userList.size(); i++) {
            JSONObject user = userList.get(i);

            if (user.getInt("id") == userId) {
                // Remove the user from userList
                userList.remove(i);

                // Remove the corresponding TextView from userListContainer
                userListContainer.removeViewAt(i);

                return;
            }
        }
        Toast.makeText(this, "User not found in the lobby list.", Toast.LENGTH_SHORT).show();
    }

    /**
     * Sends a GET request to verify the existence of a user by username and retrieve their user object.
     * If the user exists, the method proceeds to delete the user from the current lobby.
     * Handles server responses, user validation, and error notifications to ensure smooth operation.
     *
     * @param inputUsername The username of the user to be verified and removed from the lobby.
     */
    private void getDeleteUser(String inputUsername)
    {
        // Get the correct URL with the right endpoints for GET request
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/contains/" + inputUsername ;
        // Create a JSON object request to validate the user
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the GET request.
                     * Checks if the user exists and retrieves the user object. If the user exists, it calls
                     * deleteUserFromLobby to remove the user from the lobby.
                     *
                     * @param response The JSON response from the server containing the user details.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 ok")) {
                                JSONObject userObject = response.getJSONObject("user");
                                if (userObject != null) {
                                    deleteUserFromLobby(userObject);
                                } else {
                                    // "user" key is missing in response
                                    Toast.makeText(getApplicationContext(), "User data is missing in the response.", Toast.LENGTH_SHORT).show();
                                }
                            }
                            else {
                                Toast.makeText(getApplicationContext(), "User not found", Toast.LENGTH_SHORT).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the GET request.
                     * Logs the error and displays a toast message notifying the user of the issue.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e("VolleyError", "Server error: " + error.getMessage());
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                    }

                }) {
            /**
             * Adds headers to the GET request, specifying the content type and accepted response type.
             *
             * @return A map containing the request headers.
             * @throws AuthFailureError If there is an authentication failure when setting headers.
             */
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json");
                headers.put("Accept", "application/json"); // If the server expects it
                return headers;
            }
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * Sends a PUT request to remove a user from the specified lobby.
     * If the user is sucessfully removed, the UI and internal user list are updated to reflect the change.
     * Handles server responses and errors during the deletion process.
     *
     * @param user A JSON object representing the user to be removed, containg their ID and details.
     * @throws JSONException If an error occurs while extracting the user ID from the JSON object.
     */
    private void deleteUserFromLobby(JSONObject user) throws JSONException {
        // Get USER ID from the user.
        int userID = user.getInt("id") ;
        // Assemble the correct URL with right endpoints for PUT request.
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/lobby/remove/" + lobbyID + "/" + userID ;
        // Create JSON object request to remove the user from the lobby.
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the PUT request.
                     * Updates the UI and internal user list if the user is successfully removed.
                     *
                     * @param response The JSON response from the server indicating the operation's success or failure.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LobbyPage", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 ok")) {
                                deleteUserFromList(userID) ;
                                Toast.makeText(LobbyPageActivity.this, "User has been deleted from lobby.", Toast.LENGTH_SHORT).show();
                            }
                            else
                            {
                                Toast.makeText(LobbyPageActivity.this, "Failed to delete user from lobby", Toast.LENGTH_LONG).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the PUT request.
                     * Logs the error and displays a toast message notifying the user of the issue.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        if (error.networkResponse != null && error.networkResponse.data != null) {
                            String errorMsg = new String(error.networkResponse.data);
                            Log.e("VolleyError", errorMsg);
                        }
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                        error.printStackTrace();
                    }
                }) {
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }
    /**
     * Sends a DELETE request to the server to delete the specified lobby.
     * If the deletion is successful, the user is redirected to the welcome screen.
     * Any errors encountered during the request or response handling are logged and displayed to the user.
     *
     * @param lobbyID The unique identifier of the lobby to be deleted.
     */
    private void deleteLobby(int lobbyID)
    {
        // Create the correct URL with correct endpoints to delete the endpoint
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/lobby/delete/" + lobbyID + "/"+ currentUser;
        // Create a JSON object request to delete the lobby
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.DELETE, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the DELETE request.
                     * If the response indicates successful deletion, the user is notified via a toast message
                     * and redirected to the welcome screen.
                     *
                     * @param response The JSON response from the server.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LobbyPage", "Server Response: " + response.toString());

                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the DELETE request.
                     * Logs the error details and displays a toast message notifying the user of the issue.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        if (error.networkResponse != null && error.networkResponse.data != null) {
                            String errorMsg = new String(error.networkResponse.data);
                            Log.e("VolleyError", errorMsg);
                        }
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                        error.printStackTrace();
                    }
                }) {
            /**
             * Adds headers to the DELETE request, including the content type.
             *
             * @return A map containing the request headers.
             * @throws AuthFailureError If there is an issue with authentication when setting headers.
             */
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json");
                return headers;
            }
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * Retrieves the list of users currently in the specified lobby from the server.
     * For each user retrieved, this method dynamically updates the user interface
     * to display the username and associated role within the lobby. This ensures
     * that the lobby's user list is accurately reflected in real-time.
     *
     * @param lobbyID The unique identifier of the lobby whose user list is being loaded.
     */
    private void loadUsersInLobby(int lobbyID) {
       // Constuct the URL for the server request.
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/lobby/" + lobbyID;
        // Create a JSON object request ti retrieve the lobby's users
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the GET request.
                     * Extracts the list of players from the "players" array in the JSON response,
                     * and iterates through the list to add each player to the user list and UI.
                     *
                     * @param response The JSON response from the server containing player data.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            // Extract the "players" array from the response
                            JSONArray playersArray = response.getJSONArray("players");
                            for (int i = 0; i < playersArray.length(); i++) {
                                JSONObject playerObject = playersArray.getJSONObject(i);

                                // Extract relevant information for display
                                int userId = playerObject.getInt("id");
                                String username = playerObject.getString("username") ;
                                // Add player to list and UI
                                addUserToList(playerObject, username);
                            }
                            Toast.makeText(LobbyPageActivity.this, "Players loaded successfully.", Toast.LENGTH_SHORT).show();
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing player list", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors that occur during the request to the server.
                     * Logs the error message and displays a toast message to inform the user
                     * that the player list could not be loaded.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e("VolleyError", "Server error: " + error.getMessage());
                        Toast.makeText(getApplicationContext(), "Failed to load players in lobby", Toast.LENGTH_LONG).show();
                    }
                }) {
            /**
             * Adds headers to the GET request, specifying the content type and accepted response type.
             *
             * @return A map containing the request headers.
             * @throws AuthFailureError If there is an authentication failure when setting headers.
             */
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json");
                headers.put("Accept", "application/json"); // If needed by the server
                return headers;
            }
        };
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View v, int position, long id) {

        switch (position) {
            case 0:
                currSelectedGame = "Baccarat";
                break;
            case 1:
                currSelectedGame = "Blackjack";
                break;
            case 2:
                currSelectedGame = "Coinflip";
                break;

            case 3:
                currSelectedGame = "Poker";
                break;

        }

        buttonStartGame.setText("Start "+ currSelectedGame);
    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {
        // TODO Auto-generated method stub
    }
}
