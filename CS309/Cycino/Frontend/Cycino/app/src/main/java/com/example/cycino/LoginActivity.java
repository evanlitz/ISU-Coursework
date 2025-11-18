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

import java.util.HashMap;
import java.util.Map;

/**
 * LoginActivity handles the user log-in functionality in the app.
 * It allows users to enter their username and password, log in, sign up for a new account,
 * or recover their account via the "Forgot Password" button.
 * Logging in is done through sending a get request for the entered in username, checking the username's associated password,
 * and allowing the user into the app if the password matches. If it does not or the username does not exist, the user will be
 * queried again.
 *
 */
public class LoginActivity extends AppCompatActivity {

    public String username;
    public String password;
    /**
     * EditText for entering the username.
     */
    private EditText usernameEditText;

    /**
     * EditText for entering the password.
     */
    private EditText passwordEditText;

    /**
     * Button to submit login credentials.
     */
    private Button loginButton;

    /**
     * Button to navigate to the signup screen
     */
    private Button signupButton;

    /**
     * Button to navigate to the forgot password screen.
     */
    private Button forgotPasswordButton;

    /**
     * Called when the activity is first created.
     *
     * @param savedInstanceState The saved state of the application.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // Initialize UI components
        usernameEditText = findViewById(R.id.login_username_edt);
        passwordEditText = findViewById(R.id.login_password_edt);
        loginButton = findViewById(R.id.login_login_btn);
        signupButton = findViewById(R.id.login_signup_btn);
        forgotPasswordButton = findViewById(R.id.forgot_password_btn);

        // Set listeners for buttons
        loginButton.setOnClickListener(new View.OnClickListener() {
            /**
             * Handles the event for when the login button is clicked.
             * Validates correct input and initiates a login request. Incorrect input denies it.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                // User inputted username and password through editTexts.
                String username = usernameEditText.getText().toString().trim();
                String password = passwordEditText.getText().toString().trim();

                // Call logInUser with entered in username and password if they are not empty.
                if (!username.isEmpty() && !password.isEmpty()) {
                    logInUser(username, password);
                } else {
                    Toast.makeText(getApplicationContext(), "Please enter both username and password.", Toast.LENGTH_LONG).show();
                }
            }
        });

        signupButton.setOnClickListener(new View.OnClickListener() {
            /**
             * Handles the signup button when clicked, routing them to the signup screen.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(LoginActivity.this, SignupActivity.class);
                startActivity(intent);
            }
        });

        forgotPasswordButton.setOnClickListener(new View.OnClickListener() {
            /**
             * Handles the event when the forgot password button is clicked.
             * Redirects the user to the UsernameQueryActivity for password recovery.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(LoginActivity.this, UsernameQueryActivity.class);
                startActivity(intent);
            }
        });
    }

    /**
     * Sends a login request to the server with the provided username and password.
     *
     * Uses the sever url containing the username and password as part of endpoint and sends a GET request to the server.
     * The request expects a JSON response with the login status. If the server indicates a successful login, the user is redirected
     * to the home page. Otherwise, an error message is displayed through Toast.
     *
     * - Validates the input credentials before sending request.
     * - Creates JSON object to encapsulate username and password data.
     * - Handles server response:
     *      - If login is successful (200 ok), the user ID and username are passed to next activity.
     *      - If login fails, error message is shown.
     * - Also handles network errors.
     * @param username The username entered by the user in the editText.
     * @param password The password entered by the user in the editText.
     */
    private void logInUser(final String username, final String password) {
        // Server URL for login
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/submit/" + username + "/" + password;

        // Create JSON object for user data
        JSONObject userData = new JSONObject();
        try {
            userData.put("username", username);
            userData.put("password", password);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating JSON data", Toast.LENGTH_LONG).show();
            return;
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
                Request.Method.GET, url, userData, new Response.Listener<JSONObject>() {
            /**
             * Handles the server response for the login request.
             * This method processes JSON response received from server after login attempt.
             * It extracts status of request and user information from the JSON object.
             * If response indicates successful login, user is redirected to HomePage with their username and user ID passed as extras.
             * If login attempt fails, error message is displayed that informs user.
             *  Any JSON errors are caught and logged.
             *
             * @param response The JSON object returned by the server.
             */
            @Override
            public void onResponse(JSONObject response) {
                Log.d("LoginActivity", "Server Response: " + response.toString());
                try {
                    String status = response.getString("status");
                    Integer userID = response.getInt("Id");
                    if (status.equals("200 ok")) {
                        Intent intent = new Intent(LoginActivity.this, HomePageActivity.class);
                        intent.putExtra("USERNAME", username);
                        intent.putExtra("UUID", userID);
                        startActivity(intent);
                        Toast.makeText(getApplicationContext(), "Login successful!", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(getApplicationContext(), "Login failed. Try again.", Toast.LENGTH_LONG).show();
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                }
            }
        }, new Response.ErrorListener() {
            /**
             * Handles errors encountered during the login request.
             *
             * @param error The Volley error object.
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
             * Provides headers for the HTTP request.
             *
             * @return A map of HTTP headers.
             */
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json; charset=utf-8");
                return headers;
            }
        };

        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }
}