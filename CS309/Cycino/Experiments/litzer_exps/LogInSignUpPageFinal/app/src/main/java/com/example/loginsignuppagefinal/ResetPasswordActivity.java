package com.example.loginsignuppagefinal;

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

public class ResetPasswordActivity extends AppCompatActivity {
    private EditText input_password;
    private EditText confirm_password;
    private Button change_password_button;
    private Button back_to_login ;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_resetpassword);
        input_password = findViewById(R.id.input_password);
        confirm_password = findViewById(R.id.confirm_password);
        change_password_button = findViewById(R.id.reset_password_btn);
        back_to_login = findViewById(R.id.back_to_login_btn) ;
        Intent intent = getIntent();
        String username = intent.getStringExtra("USERNAME");

        change_password_button.setOnClickListener(new View.OnClickListener() {
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

    private void updateUserPassword(String username, String newPassword) {
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/login/update/" + username;

        RequestQueue requestQueue = Volley.newRequestQueue(this);
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
                    @Override
                    public void onResponse(JSONObject response) {
                        Toast.makeText(getApplicationContext(), "Password has been changed", Toast.LENGTH_LONG).show();
                        Intent intent = new Intent(ResetPasswordActivity.this, LoginActivity.class);
                        startActivity(intent);
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Toast.makeText(getApplicationContext(), "Failed to update password", Toast.LENGTH_SHORT).show();
                        Log.e("ResetPassword", "Error: " + error.getMessage());
                    }
                });

        requestQueue.add(jsonObjectRequest);
    }
}