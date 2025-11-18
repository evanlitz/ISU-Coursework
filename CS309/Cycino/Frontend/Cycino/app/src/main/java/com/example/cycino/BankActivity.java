package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.material.button.MaterialButton;

import org.json.JSONException;
import org.json.JSONObject;

public class BankActivity extends AppCompatActivity {

    // Declare UI elements
    private ImageView chipIcon;
    private TextView chipBalance;
    private EditText chipInput;
    private MaterialButton addChipsButton;
    private MaterialButton removeChipsButton;
    private ImageView bottomImage;
    private MaterialButton backButton;
    private RequestQueue requestQueue;


    // set user info
    int userChips ;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bank); // Ensure this matches your XML filename

        Intent inIntent = getIntent();
        String username = inIntent.getStringExtra("USERNAME");
        int userID = inIntent.getIntExtra("UUID",-1);
        System.out.println("user Id: " + userID);



        // Initialize UI elements
        chipIcon = findViewById(R.id.chipIcon);
        chipBalance = findViewById(R.id.chipBalance);
        chipInput = findViewById(R.id.chipInput);
        addChipsButton = findViewById(R.id.addChipsButton);
        removeChipsButton = findViewById(R.id.removeChipsButton);
        bottomImage = findViewById(R.id.bottomImage);
        backButton = findViewById(R.id.backButton);
        requestQueue = Volley.newRequestQueue(this);


        // Example of setting up UI elements (you can remove these once you add logic)
        setChips(userID);

        addChipsButton.setOnClickListener(v -> {
            String inputText = chipInput.getText().toString().trim();
            if (inputText.isEmpty()) {
                Toast.makeText(this, "Please enter a valid chip amount", Toast.LENGTH_SHORT).show();
                return;
            }

            try {
                int addAmount = Integer.parseInt(inputText);
                if (addAmount <= 0) {
                    Toast.makeText(this, "Enter a positive number", Toast.LENGTH_SHORT).show();
                    return;
                }
                else if (addAmount > 10000) {
                    Toast.makeText(this, "Enter a number below 10000. ", Toast.LENGTH_SHORT).show();
                    return;
                }
                // Call handleAddChips with the valid addAmount
                handleAddChips(addAmount, userID);

            } catch (NumberFormatException e) {
                Toast.makeText(this, "Enter a number.", Toast.LENGTH_SHORT).show();
            }
        });

        removeChipsButton.setOnClickListener(v -> {
            String inputText = chipInput.getText().toString().trim();
            if (inputText.isEmpty()) {
                Toast.makeText(this, "Please enter a valid chip amount", Toast.LENGTH_SHORT).show();
                return;
            }

            try {
                int removeAmount = Integer.parseInt(inputText);
                if (removeAmount <= 0) {
                    Toast.makeText(this, "Enter a positive number", Toast.LENGTH_SHORT).show();
                    return;
                }
                else if(removeAmount > userChips) {
                    Toast.makeText(this, "Are you trying to be in debt? Enter a number less than your current amount.", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Call handleAddChips with the valid addAmount
                handleRemoveChips(removeAmount, userID);

            } catch (NumberFormatException e) {
                Toast.makeText(this, "Enter a number.", Toast.LENGTH_SHORT).show();
            }
        });

        backButton.setOnClickListener(v -> {
            Intent i = new Intent(BankActivity.this,HomePageActivity.class);
            i.putExtra("USERNAME", username);
            i.putExtra("UUID", userID);
            startActivity(i);
        });



        }




    private void setChips(int userID)
    {
        String getUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/get/" + userID ;
        JsonObjectRequest getRequest = new JsonObjectRequest(
                Request.Method.GET,
                getUrl,
                null,
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            userChips = response.getInt("chips");
                            chipBalance.setText(String.valueOf(userChips));
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle errors
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(getRequest);
    }

    private void handleAddChips(int addAmount, int userID)
    {
        String addUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/add/" + userID + "/" ;
        JsonObjectRequest putRequest = new JsonObjectRequest(
                Request.Method.PUT,
                addUrl + addAmount,
                null, // No body for this request
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            int updatedChips = response.getInt("chips");
                            Toast.makeText(this, "New balance: " + updatedChips, Toast.LENGTH_SHORT).show();
                            userChips = updatedChips ;
                            chipBalance.setText(String.valueOf(userChips));
                            chipInput.setText("") ;
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle errors
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(putRequest);
    }

    private void handleRemoveChips(int removeAmount, int userID)
    {
        String removeUrl = "http://coms-3090-052.class.las.iastate.edu:8080/chips/remove/" + userID + "/" ;
        JsonObjectRequest putRequest = new JsonObjectRequest(
                Request.Method.PUT,
                removeUrl + removeAmount,
                null, // No body for this request
                response -> {
                    try {
                        // Handle the JSON response
                        int status = response.getInt("status");
                        if (status == 200) {
                            int updatedChips = response.getInt("chips");
                            Toast.makeText(this, "New balance: " + updatedChips, Toast.LENGTH_SHORT).show();
                            userChips = updatedChips ;
                            chipBalance.setText(String.valueOf(userChips));
                            chipInput.setText("") ;
                        } else {
                            String error = response.getString("error");
                            Toast.makeText(this, "Error: " + error, Toast.LENGTH_SHORT).show();
                        }
                    } catch (JSONException e) {
                        Toast.makeText(this, "Response parsing error", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> {
                    // Handle errors
                    Toast.makeText(this, "Request failed. Please try again.", Toast.LENGTH_SHORT).show();
                }
        );
        requestQueue.add(putRequest);
    }




}