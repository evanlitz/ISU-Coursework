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

public class UsernameQueryActivity extends AppCompatActivity {
    private EditText usernameEditText;
    private Button resetPassword;
    private Button backToLogin;
    private boolean usernameExists;

    /**
     * @param savedInstanceState
     */
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_usernamequery);

        /* initialize UI elements */
        resetPassword = findViewById(R.id.reset_button);
        usernameEditText = findViewById(R.id.username_input);
        backToLogin = findViewById(R.id.go_back_to_login_btn);
        usernameExists = false;

        //testServerConnection();

        resetPassword.setOnClickListener(new View.OnClickListener() {

            public void onClick(View v) {
                String username = usernameEditText.getText().toString();

                // RUN METHOD THAT SEARCHES SERVER FOR USERNAME AND SETS A BOOLEAN TO TRUE OR FALSE.
                pushData(username) ;

                if(usernameExists) {
                    Intent intent = new Intent(UsernameQueryActivity.this, ResetPasswordActivity.class);
                    intent.putExtra("USERNAME", username);
                    startActivity(intent);
                }
            }
        });


        backToLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(UsernameQueryActivity.this, LoginActivity.class);
                startActivity(intent);
            }
        });


    }

    /**
     * @param Username
     */
    private void pushData(final String Username) {
        // Server URL for login (adjust to match your API)
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/contains/" + Username;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            String check = response.getString("status");
                            if (check.equals("200 ok")) {
                                usernameExists = true;
                            } else {
                                Toast.makeText(getApplicationContext(), "Username not found. Try again.", Toast.LENGTH_LONG).show();
                            }
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

        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }
}