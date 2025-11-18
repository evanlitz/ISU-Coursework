package com.example.androidexample;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class FirstPage extends AppCompatActivity {

    private TextView messageText;
    private Button pageNext;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.first_page);
        // link to Main activity XML

        /* initialize UI elements */
        messageText = findViewById(R.id.msg_txt);      // link to message textview in the Main activity XML
        messageText.setText("This is the first page");
        messageText.setTextColor(0xFFFF00FF);
        messageText.setTextSize(40);

        pageNext = findViewById(R.id.page3_prev);
        pageNext.setBackgroundColor(0xFF00FF00);
        pageNext.setTextColor(0xFF000000);


        pageNext.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                Intent intent = new Intent(FirstPage.this, MainActivity.class);
                startActivity(intent);

            }
        });

    }
}


