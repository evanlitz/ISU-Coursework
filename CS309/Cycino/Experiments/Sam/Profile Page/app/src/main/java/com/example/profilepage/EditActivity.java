package com.example.profilepage;



import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class EditActivity extends AppCompatActivity {

    private TextView profileText;
    private EditText firstName;
    private EditText lastName;
    private EditText phoneNumber;
    private Button submit;
    RequestQueue requestQueue;

    final private Integer userID = 5;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_edit);

        profileText = findViewById(R.id.profileText);
        firstName = findViewById(R.id.firstName);
        lastName = findViewById(R.id.lastName);
        phoneNumber = findViewById(R.id.editTextPhone);
        submit = findViewById(R.id.submitButton);

        profileText.setPadding(0,130,0,0);
        profileText.setTextSize(30);
        profileText.setText("Profile Page");

        submit.setText("Save Profile");
        submit.setBackgroundColor(0xFFFFFF00);
        submit.setTextColor(0xFF000000);

        requestQueue = Volley.newRequestQueue(EditActivity.this);

        getOneUser(userID);


        submit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String fNameStr = firstName.getText().toString();
                String lNameStr = lastName.getText().toString();
                String phoneNum = phoneNumber.getText().toString();

                putUser(fNameStr,lNameStr,phoneNum,userID);
                Intent intent = new Intent(EditActivity.this, ViewActivity.class);
                startActivity(intent);


            }
        });

    }

    private void showOneUser(JSONObject user) {

        try {

            firstName.setText(user.getString("firstName"));
            lastName.setText(user.getString("lastName"));
            phoneNumber.setText(user.getString("phoneNumber"));
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }


    }

    private void putUser(final String fName, final String lName, final String phoneNum, final Integer id) {
        //String url = "https://10c011fe-3b08-4ae2-96a7-71049edb34ae.mock.pstmn.io/putData/"+id;
        String url = "http://coms-3090-052.class.las.iastate.edu:8080/users/update/"+id;

        System.out.println(url);

        JSONObject postData = new JSONObject();

        try {
            postData.put("firstName",fName);
            postData.put("lastName",lName);
            postData.put("phoneNumber",phoneNum);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT, url, postData,
                new Response.Listener<JSONObject>() {
            @Override
            public void onResponse(JSONObject response) {
                Toast.makeText(getApplicationContext(), "Response: "+(response.toString()), Toast.LENGTH_LONG).show();

            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
                Toast.makeText(getApplicationContext(),"FAIL"+ error, Toast.LENGTH_LONG).show();
            }
        });

        requestQueue.add(jsonObjectRequest);

        };
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

}