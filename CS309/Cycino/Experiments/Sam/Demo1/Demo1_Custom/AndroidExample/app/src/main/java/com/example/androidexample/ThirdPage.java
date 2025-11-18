package com.example.androidexample;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import java.util.Random;

public class ThirdPage extends AppCompatActivity{

    private TextView numberText;
    private Button pagePrev;
    private Button enterNumber;

    Random rand = new Random();
    Integer num = 0;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.third_page);
        // link to Main activity XML

        /* initialize UI elements */
        numberText = findViewById(R.id.msg_txt);      // link to message textview in the Main activity XML
        numberText.setText("0");


        pagePrev = findViewById(R.id.page3_prev);
        enterNumber = findViewById(R.id.enterNumber);



        pagePrev.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                Intent intent = new Intent(ThirdPage.this, MainActivity.class);
                startActivity(intent);

            }
        });

        enterNumber.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                num = rand.nextInt(100);
                numberText.setText(num.toString());


            }
        });

    }
}
