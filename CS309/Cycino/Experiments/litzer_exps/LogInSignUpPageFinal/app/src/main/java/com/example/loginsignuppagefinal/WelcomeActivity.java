package com.example.loginsignuppagefinal;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.Button ;

import androidx.appcompat.app.AppCompatActivity;

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

public class WelcomeActivity extends AppCompatActivity {

    private TextView welcomeMessage ;
    private Button deleteAccount ;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        RequestQueue queue = Volley.newRequestQueue(this);
        setContentView(R.layout.activity_welcome);
        deleteAccount = findViewById(R.id.delete_account) ;
        welcomeMessage = findViewById(R.id.welcome_message) ;
        Intent intent = getIntent();
        String username = intent.getStringExtra("USERNAME");

        if (username != null && !username.isEmpty())
        {
            welcomeMessage.setText("Welcome, " + username + "!") ;
        }
        else {
            welcomeMessage.setText("Welcome, User!") ;
        }

//        deleteAccount.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                deleteUser("username") ;
//            }
//        });



    }

    private void logInUser(final String username, final String password) {
        // Server URL for login
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/submit/" + username + "/" + password ;
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

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, userData, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LoginActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            Integer id = Integer.valueOf(response.getString("Id")) ;
                            deleteUser(id) ; //**********************
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
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
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json; charset=utf-8");
                return headers;
            }
        };

        // Add the request to the RequestQueue

    }

    private void removeUser(final String username, final String password) {
        // Server URL for login
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/submit/" + username + "/" + password ;
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

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, userData, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LoginActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            Integer id = Integer.valueOf(response.getString("Id")) ;
                            deleteUser(id) ; //**********************
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
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
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json; charset=utf-8");
                return headers;
            }
        };

        // Add the request to the RequestQueue

    }




    private void deleteUser(int userId) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/delete/" + userId ;

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("LoginActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                        } catch (JSONException e) {
                            e.printStackTrace();
                            Toast.makeText(getApplicationContext(), "Error parsing server response", Toast.LENGTH_LONG).show();
                        }
                    }
                }, new Response.ErrorListener() {
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
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Content-Type", "application/json; charset=utf-8");
                return headers;
            }
        };
    }


}
