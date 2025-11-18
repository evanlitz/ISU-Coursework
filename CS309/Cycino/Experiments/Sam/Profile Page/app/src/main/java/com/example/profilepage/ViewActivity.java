package com.example.profilepage;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;

import android.view.View;
import android.widget.Button;
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


public class ViewActivity extends AppCompatActivity {

    private Button viewButton;
    private Button lbButton;
    RequestQueue requestQueue;
    LinearLayout viewLayout;

    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view);

        viewButton = findViewById(R.id.returnButton);
        lbButton = findViewById(R.id.lbButton);
        viewLayout = findViewById(R.id.layout_view);


        requestQueue = Volley.newRequestQueue(ViewActivity.this);
        viewButton.setText("Edit Profile");
        lbButton.setText("View Leaderboard");



        getOneUser(5);
        //getAllUsers();



        viewButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(ViewActivity.this, EditActivity.class);
                startActivity(intent);
            }
        });
        lbButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(ViewActivity.this, LeaderboardActivity.class);
                startActivity(intent);
            }
        });
    }

    private void showOneUser(JSONObject user) {
        TextView nameOut = new TextView(this);
        TextView phoneNumOut = new TextView(this);

        nameOut.setTextSize(30);
        phoneNumOut.setTextSize(20);


        try {

            String out = user.getString("firstName") + " " + user.getString("lastName");

            nameOut.setText(out);
            phoneNumOut.setText(user.getString("phoneNumber"));
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }



        viewLayout.addView(nameOut);
        viewLayout.addView(phoneNumOut);


    }

    private void showAllUsers(JSONArray users) throws JSONException {

        for (int i = 0; i < users.length(); i++) {
            TextView nameOut = new TextView(this);
            TextView phoneNumOut = new TextView(this);
            TextView SPACE = new TextView(this);
            nameOut.setTextSize(18);
            phoneNumOut.setTextSize(16);

            SPACE.setText("X");
            SPACE.setTextColor(0xFFFFFFFF);

            JSONObject user = users.getJSONObject(i);

            try {

                String out = user.getString("firstName") + " " + user.getString("lastName");

                nameOut.setText(out);
                phoneNumOut.setText(user.getString("phoneNumber"));
            } catch (JSONException e) {
                throw new RuntimeException(e);
            }

            viewLayout.addView(nameOut);
            viewLayout.addView(phoneNumOut);
            viewLayout.addView(SPACE);

        }

    }




        private void getOneUser(Integer id) {
            //String url = "https://10c011fe-3b08-4ae2-96a7-71049edb34ae.mock.pstmn.io/getData";
         String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/"+id;

            JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url, null,
                    new Response.Listener<JSONObject>() {
                        @Override
                        public void onResponse(JSONObject response) {
                            Toast.makeText(getApplicationContext(),"It worked", Toast.LENGTH_LONG).show();

                                Toast.makeText(getApplicationContext(),"It worked", Toast.LENGTH_LONG).show();
                                showOneUser(response);
                        }
                    }, new Response.ErrorListener() {
                @Override
                public void onErrorResponse(VolleyError error) {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(),"It failed", Toast.LENGTH_LONG).show();
                }
            });

            // Add the request to the RequestQueue
            requestQueue.add(jsonObjectRequest);
        }

        private void getAllUsers() {
            String url = "http://coms-3090-052.class.las.iastate.edu:8080/users";

            JsonArrayRequest jsonArrayRequest = new JsonArrayRequest(Request.Method.GET, url, null,
                    new Response.Listener<JSONArray>() {
                        @Override
                        public void onResponse(JSONArray response) {

                            try {
                                showAllUsers(response);
                            } catch (JSONException e) {
                                throw new RuntimeException(e);
                            }

                        }
                    }, new Response.ErrorListener() {
                @Override
                public void onErrorResponse(VolleyError error) {
                    error.printStackTrace();
                    Toast.makeText(getApplicationContext(),"It failed", Toast.LENGTH_LONG).show();
                }
            });
            requestQueue.add(jsonArrayRequest);

        }
}
