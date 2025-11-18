package com.example.profilepage;

import android.os.Bundle;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;

import org.w3c.dom.Text;

public class LeaderboardActivity extends AppCompatActivity{

    Gravity gravity = new Gravity();

    final private String[] names = {"name1","name2","name3","name5","name4"};
    final private Integer[] scores = {500000,100000,200,5000,200};
    final private Integer[] numWins = {1000,10,85,20,300};


    private LinearLayout lbNames;
    private LinearLayout lbScores;
    private LinearLayout lbWins;
    private TextView titleText;

    final int items = 5;
    final int numLines = 2;
    final TextView[] myNameViews = new TextView[items];
    final TextView[] myScoreViews = new TextView[items];
    final TextView[] myWinViews = new TextView[items];


    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_leaderboard);

        lbNames = findViewById(R.id.lb_names);
        lbScores = findViewById(R.id.lb_scores);
        lbWins = findViewById(R.id.lb_wins);
        titleText = findViewById(R.id.text_leaderboard_title);

        titleText.setPadding(0,150,0,0);
        titleText.setTextSize(40);

        final TextView nameTitle = new TextView(this);
        final TextView winsTitle = new TextView(this);
        final TextView scoreTitle = new TextView(this);

        nameTitle.setText("Name");
        winsTitle.setText("Wins");
        scoreTitle.setText("Chips");

        nameTitle.setTextSize(28);
        nameTitle.setPadding(10,0,0,0);
        winsTitle.setTextSize(28);
        winsTitle.setGravity(gravity.RIGHT);
        scoreTitle.setTextSize(28);
        scoreTitle.setGravity(gravity.RIGHT);
        scoreTitle.setPadding(0,0,10,0);


        lbNames.addView(nameTitle);
        lbWins.addView(winsTitle);
        lbScores.addView(scoreTitle);


        for (int i = 0; i < items; i++) {

            final int numLines = 3;
            final TextView[] lines = new TextView[numLines];

            for (int j = 0; j < numLines; j++) {

                final TextView line = new TextView(this);

                line.setBackgroundColor(0xFF000000);
                line.setTextSize(2);
                lines[j] = line;

            }

            final TextView nameView = new TextView(this);
            final TextView scoreView = new TextView(this);
            final TextView winView = new TextView(this);


            // set some properties of rowTextView or something
            nameView.setText(names[i]);
            nameView.setTextSize(20);
            nameView.setGravity(gravity.LEFT);
            nameView.setPadding(10,0,0,0);

            winView.setText(numWins[i]+"");
            winView.setTextSize(20);
            winView.setGravity(gravity.RIGHT);
            winView.setPadding(10,0,0,0);

            scoreView.setText(scores[i]+"");
            scoreView.setTextSize(20);
            scoreView.setGravity(gravity.RIGHT);
            scoreView.setPadding(0,0,10,0);


            // add the textview to the linearlayout
            lbNames.addView(nameView);
            lbNames.addView(lines[0]);
            lbWins.addView(winView);
            lbWins.addView(lines[1]);
            lbScores.addView(scoreView);
            lbScores.addView(lines[2]);

            // save a reference to the textview for later
            myNameViews[i] = nameView;
            myScoreViews[i] = scoreView;


        }
    }
}
