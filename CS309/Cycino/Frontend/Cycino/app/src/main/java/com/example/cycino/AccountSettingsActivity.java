package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.cycino.R;

import org.json.JSONException;
import org.json.JSONObject;


public class AccountSettingsActivity extends AppCompatActivity {

    private Button backButton;
    private Button btnChangeUsername;
    private Button btnChangePassword;
    private Button btnChangeFirstName;
    private Button btnChangeLastName;
    private Button btnChangePhoneNumber;
    private Button deleteAccountButton;
    private EditText editUsername;
    private EditText editPassword;
    private EditText editFirstName;
    private EditText editLastName;
    private EditText editPhoneNumber;
    private String password ;
    private String username ;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_accountsettings);

        Intent intent = getIntent();
        int userID = intent.getIntExtra("UUID",-1);
        String userUsername = intent.getStringExtra("USERNAME");
        Toast.makeText(AccountSettingsActivity.this, "" + userID, Toast.LENGTH_SHORT).show();

        getPassword(userID) ;

        // Initialize UI elements
        backButton = findViewById(R.id.bbackButton);
        btnChangeUsername = findViewById(R.id.btnChangeUsername);
        btnChangePassword = findViewById(R.id.btnChangePassword);
        btnChangeFirstName = findViewById(R.id.btnChangeFirstName);
        btnChangeLastName = findViewById(R.id.btnChangeLastName);
        btnChangePhoneNumber = findViewById(R.id.btnChangePhoneNumber);
        deleteAccountButton = findViewById(R.id.deleteAccountButton);
        editUsername = findViewById(R.id.editUsername);
        editPassword = findViewById(R.id.editPassword);
        editFirstName = findViewById(R.id.editFirstName);
        editLastName = findViewById(R.id.editLastName);
        editPhoneNumber = findViewById(R.id.editPhoneNumber);

        // Set listeners for buttons
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(AccountSettingsActivity.this, MainSettingsActivity.class);
                intent.putExtra("UUID",userID);
                intent.putExtra("USERNAME",username);
                startActivity(intent); // Start MainActivity
            }
        });

        btnChangeUsername.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newUsername = editUsername.getText().toString();
                if (newUsername.matches("^[a-zA-Z0-9_]+$")) {
                    updateLogin(newUsername, password) ;
                } else {
                    Toast.makeText(AccountSettingsActivity.this, "Invalid username. Only letters, numbers, and underscores are allowed.", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnChangePassword.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newPassword = editPassword.getText().toString();
                if (!newPassword.contains(" ")) {
                    updateLogin(username, newPassword);
                } else {
                    Toast.makeText(AccountSettingsActivity.this, "Invalid password. No spaces are allowed.", Toast.LENGTH_SHORT).show();
                }
            }
        });

        // This currently changes all user information. need a proper endpoint or null checks.
        btnChangeFirstName.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newFirstName = editFirstName.getText().toString();
                if (newFirstName.matches("^[a-zA-Z]+$")) {
                    updateFirstName(userID, newFirstName);
                } else {
                    Toast.makeText(AccountSettingsActivity.this, "Invalid first name. Only letters are allowed.", Toast.LENGTH_SHORT).show();
                }
            }
        });


        // This currently changes all user information. need a proper endpoint.
        btnChangeLastName.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newLastName = editLastName.getText().toString();
                if (newLastName.matches("^[a-zA-Z]+$")) {
                    updateLastName(userID, newLastName) ;
                } else {
                    Toast.makeText(AccountSettingsActivity.this, "Invalid last name. Only letters are allowed.", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnChangePhoneNumber.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newPhoneNumber = editPhoneNumber.getText().toString();
                if (newPhoneNumber.matches("^[0-9]+$")) {
                    updatePhoneNumber(userID, newPhoneNumber) ;
                } else {
                    Toast.makeText(AccountSettingsActivity.this, "Invalid phone number. Only numbers are allowed.", Toast.LENGTH_SHORT).show();
                }
            }
        });

        deleteAccountButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                deleteAccount(username);
                Toast.makeText(AccountSettingsActivity.this, "Account deleted" + userID, Toast.LENGTH_SHORT).show();
                Intent intent = new Intent(AccountSettingsActivity.this, LoginActivity.class);
                startActivity(intent);
            }
        });
    }

    /**
     * @param username
     */
    private void deleteAccount(String username) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/delete/" + username;
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.DELETE, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("AccountSettings", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 ok")) {
                                Toast.makeText(AccountSettingsActivity.this, "Account has been deleted.", Toast.LENGTH_SHORT).show();
                                Intent intent = new Intent(AccountSettingsActivity.this, SignupActivity.class); // CHANGE TO SIGNUP PAGE!!!!!
                                startActivity(intent);
                            }
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
        };

        // Add the request to the RequestQueue
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);

    }

    /**
     * @param newUsername
     * @param newPassword
     */
    private void updateLogin(String newUsername, String newPassword) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/update/" + username ;
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        JSONObject userData = new JSONObject();
        try {
            userData.put("username", newUsername);
            userData.put("password", newPassword);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating JSON data", Toast.LENGTH_LONG).show();
            return;
        }
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, userData, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Toast.makeText(getApplicationContext(), "Login information has been updated", Toast.LENGTH_LONG).show();
                        username = newUsername ;
                        password = newPassword ;
                        editUsername.setText("");
                        editPassword.setText("");
                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Toast.makeText(getApplicationContext(), "Failed to update login information", Toast.LENGTH_SHORT).show();
                        Log.e("UsernamePassword", "Error: " + error.getMessage());
                    }
                });
        requestQueue.add(jsonObjectRequest);
    }

    /**
     * @param newFirstName
     */
    private void updateFirstName(final int userID, final String newFirstName)
    {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/update/" + userID;

        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("firstName", newFirstName);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating request body", Toast.LENGTH_SHORT).show();
            return;
        }
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, jsonBody, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("AccountSettingsActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 OK")) {
                                Toast.makeText(AccountSettingsActivity.this, "First name updated to: " + newFirstName, Toast.LENGTH_SHORT).show();
                            }
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
        };
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * @param newLastName
     */
    private void updateLastName(final int userID, final String newLastName)
    {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/update/" + userID ;

        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("lastName", newLastName);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating request body", Toast.LENGTH_SHORT).show();
            return;
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, jsonBody, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("AccountSettingsActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 OK")) {
                                Toast.makeText(AccountSettingsActivity.this, "Last name updated to: " + newLastName, Toast.LENGTH_SHORT).show();
                            }
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
        };
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    /**
     * @param newPhoneNumber 
     */
    private void updatePhoneNumber(final int userID, final String newPhoneNumber)
    {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/update/" + userID ;

        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("phoneNumber", newPhoneNumber);
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Error creating request body", Toast.LENGTH_SHORT).show();
            return;
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.PUT, url, jsonBody, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("AccountSettingsActivity", "Server Response: " + response.toString());
                        try {
                            String status = response.getString("status");
                            if (status.equals("200 OK")) {
                                Toast.makeText(AccountSettingsActivity.this, "Phone number updated to: " + newPhoneNumber, Toast.LENGTH_SHORT).show();
                            }
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
        };
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);
    }

    private void getPassword(int userID) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/" + userID;
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                                username = response.getString("username") ;
                                password = response.getString("password") ;
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
        };
        RequestQueue queue = Volley.newRequestQueue(this);
        queue.add(jsonObjectRequest);

    }







}




