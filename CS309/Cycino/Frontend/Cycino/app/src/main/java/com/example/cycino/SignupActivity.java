package com.example.cycino;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * SignupActivity handles the user signup process, allowing new users to register an account
 * by providing a username and password. It includes validation for matching passwords
 * and communicates with the server to create the account. Users can also navigate to the
 * login screen if they already have an account.
 */
public class SignupActivity extends AppCompatActivity {

    /**
     * EditText for entering the desired username.
     */
    private EditText usernameEditText;

    /**
     * EditText for entering the password.
     */
    private EditText passwordEditText;

    /**
     * EditText for confirming the entered password.
     */
    private EditText confirmEditText;

    /**
     * Button to navigate to the LoginActivity.
     */
    private Button loginButton;

    /**
     * Button to submit the signup form and create a new account.
     */
    private Button signupButton;

    /**
     * Initializes the signup activity and sets up the UI elements and button click listeners.
     *
     * @param savedInstanceState The previously saved state of the activity, if any.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signup);

        // Initialize UI elements from layout xml.
        usernameEditText = findViewById(R.id.signup_username_edt);
        passwordEditText = findViewById(R.id.signup_password_edt);
        confirmEditText = findViewById(R.id.signup_confirm_edt);
        loginButton = findViewById(R.id.signup_login_btn);
        signupButton = findViewById(R.id.signup_signup_btn);

        // Sets the click listener for login button
        loginButton.setOnClickListener(new View.OnClickListener() {
            /**
             * Redirects the user to the LoginActivity when the login button is clicked.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                /* when login button is pressed, use intent to switch to Login Activity */
                Intent intent = new Intent(SignupActivity.this, LoginActivity.class);
                startActivity(intent);  // go to LoginActivity
            }
        });

        // Set click listener for the signup button
        signupButton.setOnClickListener(new View.OnClickListener() {
            /**
             * Validates the user input and attempts to register a new account when the signup button is clicked.
             * Ensures that the password fields match and are not empty before continuing.
             *
             * Three strings: Username, Password, and Confirm that are all inputted by user.
             *
             * Password and confirm are checked to be equal. If they are, then the user is signed up and signUpUser is called.
             *
             * If they do not match, then the user is queried again and receives a Toast message.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                /* grab strings from user inputs */
                String username = usernameEditText.getText().toString().trim();
                String password = passwordEditText.getText().toString().trim();
                String confirm = confirmEditText.getText().toString().trim();

                if (password.equals(confirm) && !password.isEmpty() && !username.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "Signing up...", Toast.LENGTH_SHORT).show();
                    signUpUser(username, password);  // Call the sign-up method
                } else {
                    Toast.makeText(getApplicationContext(), "Passwords don't match or are invalid.", Toast.LENGTH_LONG).show();
                }
            }
        });
    }

    /**
     * Sends a POST request to the server to register a new user.
     * This method constructs a JSON object containing the  username and password that was inputted,
     * which sends the request to the server's signup endpoint, and handles the server's response.
     * If the signup is successful, the user is directed to the home page.
     * If there are errors during the request or response parsing, the user is notified appropriately.
     *
     * @param username The username provided by the user to register their account.
     * @param password The password provided by the user for their new account.
     */
    private void signUpUser(final String username, final String password) {
        // Server URL
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/signup/register"; // signup/register to make new users.

        // Create JSON object for user data with the inputted username and password.
        JSONObject userData = new JSONObject();
        try {
            userData.put("username", username);
            userData.put("password", password);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating JSON data", Toast.LENGTH_LONG).show();
            return;
        }

        // Create a JSON object POST request to send user data to server.
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.POST, url, userData, new Response.Listener<JSONObject>() {
                    /**
                     * Handles the server's response to the signup request.
                     * If the server responds with a successful status, the user is redirected to the home page.
                     * Otherwise, a failure message is displayed to the user.
                     *
                     * @param response The JSON response from the server.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            String status = response.getString("status") ;
                            if (status.equals("200 ok")) {
                                Intent intent = new Intent(SignupActivity.this, LoginActivity.class);
                                intent.putExtra("USERNAME", username);
                                startActivity(intent);
                                Toast.makeText(getApplicationContext(), "Signup successful!", Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(getApplicationContext(), "Signup failed. Try again.", Toast.LENGTH_LONG).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
                    /**
                     * Handles errors encountered during the request to the server.
                     * Displays an appropriate error message to the user and logs the issue for debugging.
                     *
                     * @param error The error encountered during the request.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // Handle the error response
                        Toast.makeText(getApplicationContext(), "Server error: " + error.getMessage(), Toast.LENGTH_LONG).show();
                        error.printStackTrace();
                    }
                });
        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }
}