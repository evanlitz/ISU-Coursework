package com.example.loginsignuppage;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    private TextView messageText;
    private TextView usernameText ;
    private Button loginButton;
    private Button signupButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        messageText = findViewById(R.id.main_msg_txt);
        usernameText = findViewById(R.id.main_username_txt);
        loginButton = findViewById(R.id.main_login_btn);
        signupButton = findViewById(R.id.main_signup_btn);

        Bundle extras = getIntent().getExtras();

        if(extras == null)
        {
            messageText.setText("Home Page");
            usernameText.setVisibility(View.INVISIBLE);
        } else {
            messageText.setText("Welcome");
            usernameText.setText(extras.getString("USERNAME"));
            loginButton.setVisibility(View.INVISIBLE);
            signupButton.setVisibility(View.INVISIBLE);
        }

    loginButton.setOnClickListener(new View.OnClickListener()
        {
        public void onClick(View v)
        {
            Intent intent = new Intent(MainActivity.this, LoginActivity.class);
            startActivity(intent);
        }
        });

    signupButton.setOnClickListener(new View.OnClickListener() {
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, SignupActivity.class);
            startActivity(intent);
        }

        });
    }
}