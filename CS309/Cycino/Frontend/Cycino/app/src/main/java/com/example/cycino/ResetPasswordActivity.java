package com.example.cycino;

import android.os.Bundle;
import android.util.Log;
import android.widget.EditText;
import android.content.Intent;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * ResetPasswordActivity handles resetting a user's password.
 * This activity is typically accessed after clicking forgot password in logInActivity, but also through settings.
 * The user enters and confirms their new password, and upon validation, the updated password is sent to the server.
 * The activity includes:
 * - Inputs for the new password and its confirmation.
 * - A button to submit the new password for update.
 * - Navigation to return to the login screen after successful completion.
 */
public class ResetPasswordActivity extends AppCompatActivity {
    /**
     * Input field for the new password.
     */
    private EditText input_password;

    /**
     * Input field to confirm the new password.
     */
    private EditText confirm_password;

    /**
     * Button to submit the new password and send the update request to the server.
     */
    private Button change_password_button;

    /**
     * Button to navigate back to the login screen without changing the password.
     */
    private Button back_to_login;


    /**
     * Initializes the activity, sets up the layout, and configures button click listeners.
     * The username is retrieved from the intent extras to associate  password change
     * with the correct account.
     *
     * @param savedInstanceState The saved state of the application.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_resetpassword);
        // Initialize UI components
        input_password = findViewById(R.id.input_password);
        confirm_password = findViewById(R.id.confirm_password);
        change_password_button = findViewById(R.id.reset_password_btn);
        back_to_login = findViewById(R.id.back_to_login_btn) ;
        // Retrieve username from intent.
        Intent intent = getIntent();
        String username = intent.getStringExtra("USERNAME");

        change_password_button.setOnClickListener(new View.OnClickListener() {
            /**
             * Validates the password input and confirmation. If the passwords match,
             * calls updateUserPassword to send the update request.
             * Displays a toast message if the passwords do not match.
             *
             * @param v The view that was clicked.
             */
            @Override
            public void onClick(View v) {
                String input = input_password.getText().toString();
                String confirm = confirm_password.getText().toString();

                if (input.equals(confirm)) {
                    updateUserPassword(username, input);
                } else {
                    Toast.makeText(getApplicationContext(), "Passwords don't match", Toast.LENGTH_LONG).show();
                }
            }
        });
    }

    /**
     * Sends a PUT request to the server to update the user's password.
     * The request includes the username and the new password in the JSON body.
     * If the update is successful, the user is redirected to the LoginActivity.
     * If there’s an error, a toast message is displayed with the failure reason.
     *
     * @param username    The username of the account for which account the password is being updated.
     * @param newPassword The new password entered by the user.
     */
    private void updateUserPassword(String username, String newPassword) {
        // Construct the server URL for the password update endpoint
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/update/" + username;
        // Create the Volley request queue
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        // Create the JSON object for the request body
        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("username", username);
            jsonBody.put("password", newPassword);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating request body", Toast.LENGTH_SHORT).show();
            return;
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url, jsonBody,
                new Response.Listener<JSONObject>() {
                    /**
                     * Handles the successful response from the server.
                     * Displays a success message and redirects the user to the LoginActivity.
                     *
                     * @param response The JSON response from the server.
                     */
                    @Override
                    public void onResponse(JSONObject response) {
                        Toast.makeText(getApplicationContext(), "Password has been changed", Toast.LENGTH_LONG).show();
                        Intent intent = new Intent(ResetPasswordActivity.this, LoginActivity.class);
                        startActivity(intent);
                    }
                },
                new Response.ErrorListener() {
                    /**
                     * Handles errors encoutnered during the password update request.
                     * Then it logs the error details and displays a toast message notifying the user of the failure.
                     *
                     * @param error The error returned from the server or network.
                     */
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Toast.makeText(getApplicationContext(), "Failed to update password", Toast.LENGTH_SHORT).show();
                        Log.e("ResetPassword", "Error: " + error.getMessage());
                    }
                });

        requestQueue.add(jsonObjectRequest);
    }
}