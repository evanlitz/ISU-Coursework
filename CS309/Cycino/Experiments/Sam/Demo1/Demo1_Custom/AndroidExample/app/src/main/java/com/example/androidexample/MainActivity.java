package com.example.androidexample;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    private TextView messageText;   // define message textview variable
    private Button pagePrev;
    private Button pageNext;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // link to Main activity XML

        /* initialize UI elements */
        messageText = findViewById(R.id.msg_txt);      // link to message textview in the Main activity XML
        messageText.setText("Hello World");

        pagePrev = findViewById(R.id.page2_prev);
        pageNext = findViewById(R.id.page3_prev);


        pageNext.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view) {

                Intent intent = new Intent(MainActivity.this, ThirdPage.class);
                startActivity(intent);

            }
        });

        pagePrev.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this, FirstPage.class);
                startActivity(intent);
            }
        });

    }
}