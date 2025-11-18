package com.example.cycino;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class RulesActivity extends AppCompatActivity {

    private Button btnBlackjack, btnPoker, btnBaccarat, btnCoinFlip, btnAppInfo, backBtn;
    private LinearLayout scrollViewLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_rulesinformation);

        // Initialize UI elements
        btnBlackjack = findViewById(R.id.btnBlackjack);
        btnPoker = findViewById(R.id.btnPoker);
        btnBaccarat = findViewById(R.id.btnBaccarat);
        btnCoinFlip = findViewById(R.id.btnCoinFlip);
        btnAppInfo = findViewById(R.id.btnAppInfo);
        scrollViewLayout = findViewById(R.id.scrollViewLayout);
        backBtn = findViewById(R.id.btnBack) ;

        Intent intent = getIntent();
        int userID = intent.getIntExtra("UUID",-1);
        String username = intent.getStringExtra("USERNAME");



        // Set listeners for buttons
        btnBlackjack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();

                // Add a header for rules
                addHeaderTextView(scrollViewLayout, "Blackjack Rules:");

                // Add rules as list items
                addTextViewToScrollView(scrollViewLayout, "😎 Try to get as close to 21 as possible without exceeding it.");
                addTextViewToScrollView(scrollViewLayout, "😎 Number cards are worth their face value.");
                addTextViewToScrollView(scrollViewLayout, "😎 Face cards are worth 10 points each.");

                // Add a detailed section for aces
                addHeaderTextView(scrollViewLayout, "Understanding Aces:");
                addTextViewToScrollView(scrollViewLayout, "🅰️ Aces can be worth 1 or 11 points, depending on the situation.");
                addTextViewToScrollView(scrollViewLayout, "🅰️ If counting an ace as 11 keeps your hand value under or equal to 21, it is counted as 11.");
                addTextViewToScrollView(scrollViewLayout, "🅰️ If counting an ace as 11 would cause your hand value to exceed 21, it is counted as 1 instead.");
                addTextViewToScrollView(scrollViewLayout, "🅰️ Example:");
                addTextViewToScrollView(scrollViewLayout, "> Hand: Ace, 7 -> Total: 18 (Ace counts as 11)");
                addTextViewToScrollView(scrollViewLayout, "> Hand: Ace, 7, 5 -> Total: 13 (Ace counts as 1)");

                // Add a section on when to hit or stand
                addHeaderTextView(scrollViewLayout, "Know When to Hit or Stand:");
                addTextViewToScrollView(scrollViewLayout, "🎯 Hit if your hand is 10 or lower.");
                addTextViewToScrollView(scrollViewLayout, "🧍‍♂️ Stand if you have 17 or higher and the dealer's upcard is 7 or lower.");

                // Add a section on splitting pairs
                addHeaderTextView(scrollViewLayout, "Split Pairs Strategically:");
                addTextViewToScrollView(scrollViewLayout, "🪓 Always split aces and eights.");
                addTextViewToScrollView(scrollViewLayout, "🪓 Never split tens or fours.");

                addHeaderTextView(scrollViewLayout, "Betting Strategies:");

                // Add retooled betting tips
                addTextViewToScrollView(scrollViewLayout, "💰 Consider the dealer's up card when deciding your move.");
                addTextViewToScrollView(scrollViewLayout, "💰 Focus on managing your bankroll wisely to play consistently over time. Although the currency is artificial, its best to treat it realistically for practice.");
                addTextViewToScrollView(scrollViewLayout, "💰 Gradually increase your bets only if you're comfortable with your overall balance.");
                addTextViewToScrollView(scrollViewLayout, "💰 Doubling down when your hand equals 10 or 11 is more favorable and can increase profit.");
                addTextViewToScrollView(scrollViewLayout, "💰 Playing at tables with lower dealer stand values and higher payouts decreases house edge.");
            }
        });

        btnPoker.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();

                addHeaderTextView(scrollViewLayout, "Poker Rules:");

                // Add general Texas Hold'em rules
                addTextViewToScrollView(scrollViewLayout, "🧠 Texas Hold'em Poker is played with a standard deck of 52 cards.");
                addTextViewToScrollView(scrollViewLayout, "🧠 Each player is dealt two private cards (hole cards).");
                addTextViewToScrollView(scrollViewLayout, "🧠 Five community cards are dealt face-up in the center of the table.");
                addTextViewToScrollView(scrollViewLayout, "🧠 Players use any combination of their hole cards and the community cards to form the best possible hand.");
                addTextViewToScrollView(scrollViewLayout, "🧠 The game consists of four betting rounds: pre-flop, flop, turn, and river.");
                addTextViewToScrollView(scrollViewLayout, "🧠 The objective is to win the pot by having the best hand or forcing all other players to fold.");

                // Add a section on hand rankings
                addHeaderTextView(scrollViewLayout, "Poker Hand Rankings:");
                addTextViewToScrollView(scrollViewLayout, "1️⃣ Royal Flush: A, K, Q, J, 10 of the same suit.");
                addTextViewToScrollView(scrollViewLayout, "2️⃣ Straight Flush: Five cards in a sequence of the same suit.");
                addTextViewToScrollView(scrollViewLayout, "3️⃣ Four of a Kind: Four cards of the same rank.");
                addTextViewToScrollView(scrollViewLayout, "4️⃣ Full House: Three of a kind with a pair.");
                addTextViewToScrollView(scrollViewLayout, "5️⃣ Flush: Any five cards of the same suit, not in sequence.");
                addTextViewToScrollView(scrollViewLayout, "6️⃣ Straight: Five cards in a sequence, but not of the same suit.");
                addTextViewToScrollView(scrollViewLayout, "7️⃣ Three of a Kind: Three cards of the same rank.");
                addTextViewToScrollView(scrollViewLayout, "8️⃣ Two Pair: Two different pairs.");
                addTextViewToScrollView(scrollViewLayout, "9️⃣ One Pair: Two cards of the same rank.");
                addTextViewToScrollView(scrollViewLayout, "🔟 High Card: The highest card in your hand when no other combination is made.");

                // Add a section on Texas Hold'em strategies
                addHeaderTextView(scrollViewLayout, "Texas Hold'em Strategies:");
                addTextViewToScrollView(scrollViewLayout, "♥️ Play tight in early positions: Focus on strong starting hands like Aces, Kings, Queens, or Ace-King.");
                addTextViewToScrollView(scrollViewLayout, "♠️ Loosen up in late positions: You can play a wider range of hands if fewer players act after you.");
                addTextViewToScrollView(scrollViewLayout, "♦️ Pay attention to the board texture: Evaluate the strength of potential hands based on community cards.");
                addTextViewToScrollView(scrollViewLayout, "♣️ Semi-bluff effectively: Bet aggressively with drawing hands (e.g., flush or straight draws) to put pressure on opponents.");
                addTextViewToScrollView(scrollViewLayout, "♥️ Protect your hand: Bet strongly if you have a vulnerable but likely winning hand.");
                addTextViewToScrollView(scrollViewLayout, "♠️ Fold when necessary: Avoid calling large bets with weak hands or chasing low-probability draws.");

                // Add a section on Texas Hold'em tips
                addHeaderTextView(scrollViewLayout, "Texas Hold'em Tips:");
                addTextViewToScrollView(scrollViewLayout, "💡 Learn the odds: Understand probabilities for hitting draws or improving your hand.");
                addTextViewToScrollView(scrollViewLayout, "💡 Observe opponents: Watch for betting patterns, tendencies, and potential tells.");
                addTextViewToScrollView(scrollViewLayout, "💡 Be aware of your stack size: Adjust your strategy based on how many chips you have relative to the blinds.");
                addTextViewToScrollView(scrollViewLayout, "💡 Manage your bankroll: Never risk too much of your total chips on a single hand.");
                addTextViewToScrollView(scrollViewLayout, "💡 Stay disciplined: Fold hands that don’t fit your strategy, even if it’s tempting to play.");

                // Add a section on betting in Texas Hold'em
                addHeaderTextView(scrollViewLayout, "Betting in Texas Hold'em:");
                addTextViewToScrollView(scrollViewLayout, "💰 Small Blind and Big Blind: The two players to the left of the dealer post mandatory bets before the cards are dealt.");
                addTextViewToScrollView(scrollViewLayout, "💰 Betting Rounds:");
                addIndentedTextView(scrollViewLayout, "  1️⃣ Pre-Flop: Players bet after receiving their hole cards.");
                addIndentedTextView(scrollViewLayout, "  2️⃣ Flop: Players bet after the first three community cards are dealt.");
                addIndentedTextView(scrollViewLayout, "  3️⃣ Turn: Players bet after the fourth community card is dealt.");
                addIndentedTextView(scrollViewLayout, "  ️ ️4️⃣ River: Players bet after the fifth and final community card is dealt.");
                addTextViewToScrollView(scrollViewLayout, "💰 Bet sizing: Consider the size of the pot and potential outcomes when making bets.");
                addTextViewToScrollView(scrollViewLayout, "💰 Avoid overcommitting: Fold weak hands instead of calling large bets.");

                // Add closing tips
                addHeaderTextView(scrollViewLayout, "Final Tip:");
                addTextViewToScrollView(scrollViewLayout, "🧨 Texas Hold'em is a game of skill, patience, and observation. Focus on playing strategically and enjoy the game!");
            }
        });

        btnBaccarat.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();

                addHeaderTextView(scrollViewLayout, "Baccarat Rules:");

                // Add general Baccarat rules
                addTextViewToScrollView(scrollViewLayout, " 📙 Baccarat is played with up to 8 decks of cards shuffled together.");
                addTextViewToScrollView(scrollViewLayout, " 📙 Players bet on the outcome of the game: Player win, Banker win, or a Tie.");
                addTextViewToScrollView(scrollViewLayout, " 📙 The objective is to bet on the hand that comes closest to a total of 9.");
                addTextViewToScrollView(scrollViewLayout, " 📙 Cards 2-9 are worth their face value, Aces are worth 1, and 10s and face cards are worth 0.");
                addTextViewToScrollView(scrollViewLayout, " 📙 If the total exceeds 9, only the last digit is considered (e.g., 15 becomes 5).");

                // Add a section on the game flow
                addHeaderTextView(scrollViewLayout, "Game Flow:");
                addTextViewToScrollView(scrollViewLayout, "🎲 Both the Player and Banker hands are dealt two cards each.");
                addTextViewToScrollView(scrollViewLayout, "🎲 A third card may be drawn for either hand based on specific rules:");
                addIndentedTextView(scrollViewLayout, "🎲 Player draws a third card if their hand total is 0-5, unless the Banker already has 8 or 9.");
                addIndentedTextView(scrollViewLayout, "🎲 Banker draws a third card based on their hand total and the Player’s third card value.");
                addTextViewToScrollView(scrollViewLayout, "🎲 The hand closest to 9 wins. If the totals are equal, it’s a Tie.");

                // Add a section on betting options
                addHeaderTextView(scrollViewLayout, "Betting Options:");
                addTextViewToScrollView(scrollViewLayout, "💸 Bet on Player: Pays 1:1 if the Player hand wins.");
                addTextViewToScrollView(scrollViewLayout, "💸 Bet on Banker: Pays 1:1 minus a 5% commission if the Banker hand wins.");
                addTextViewToScrollView(scrollViewLayout, "💸 Bet on Tie: Pays 8:1 or 9:1 (varies by casino) if both hands have the same total.");

                // Add a section on Baccarat tips
                addHeaderTextView(scrollViewLayout, "Baccarat Tips:");
                addTextViewToScrollView(scrollViewLayout, "😁 Always bet on Banker: Statistically, Banker bets win slightly more often.");
                addTextViewToScrollView(scrollViewLayout, "😁 Avoid the Tie bet: It has the highest house edge, making it a risky choice.");
                addTextViewToScrollView(scrollViewLayout, "😁 Try managing your bankroll: Although the currency is artificial, practicing as if it was real can increase feel for the game.");

                // Add a section on strategies
                addHeaderTextView(scrollViewLayout, "Betting Strategies:");
                addTextViewToScrollView(scrollViewLayout, "💰 Martingale System: Double your bet after a loss to recover losses, but be cautious of table limits.");
                addTextViewToScrollView(scrollViewLayout, "💰 Follow Streaks: Some players prefer to bet on streaks, like multiple Banker or Player wins in a row.");
                addTextViewToScrollView(scrollViewLayout, "💰 Avoid Complex Systems: Baccarat is largely a game of luck, so avoid overly complicated strategies.");
            }
        });

        btnCoinFlip.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();

                addHeaderTextView(scrollViewLayout, "Coin Flip Rules:");

                // Add general Coin Flip rules
                addTextViewToScrollView(scrollViewLayout, "🪙 The game is played with an entire lobby of players betting on the outcome of a coin flip.");
                addTextViewToScrollView(scrollViewLayout, "🪙 Each round, all players guess either \"Heads\" or \"Tails\".");
                addTextViewToScrollView(scrollViewLayout, "🪙 Players who guess correctly advance to the next round. | Players who guess incorrectly are eliminated from the game.");
                addTextViewToScrollView(scrollViewLayout, "🪙 If all players are eliminated in a single round, the game continues, and everyone stays in.");
                addTextViewToScrollView(scrollViewLayout, "🪙 The game prolongs until only one player remains, who is declared the winner and wins all of the bets from the losers.");

                // Add a section on betting mechanics
                addHeaderTextView(scrollViewLayout, "Betting Mechanics:");
                addTextViewToScrollView(scrollViewLayout, "🍀 Players do not compete against the house; the game is entirely player-versus-player.");
                addTextViewToScrollView(scrollViewLayout, "🍀 All players place the same bet amount each game.");
                addTextViewToScrollView(scrollViewLayout, "🍀 Bets accumulate in a communal pot, and the final winner claims the entire pot.");
                addTextViewToScrollView(scrollViewLayout, "🍀 There is no house cut or commission in this game.");

                // Add a section on game flow
                addHeaderTextView(scrollViewLayout, "Game Flow:");
                addTextViewToScrollView(scrollViewLayout, "🐦 The coin is flipped, and the outcome is randomly determined to be either \"Heads\" or \"Tails\".");
                addTextViewToScrollView(scrollViewLayout, "🐦 Players who guessed the correct side advance to the next round.");
                addTextViewToScrollView(scrollViewLayout, "🐦 If all players are eliminated in a single round, the coin is flipped again, and everyone remains in the game.");

                // Add a section on tips
                addHeaderTextView(scrollViewLayout, "Tips for Playing Coin Flip:");
                addTextViewToScrollView(scrollViewLayout, "🌪️ Remember that each coin flip is independent; prior results do not influence future flips.");
                addTextViewToScrollView(scrollViewLayout, "🌪️ Use randomness to your advantage: Avoid predictable patterns when guessing.");
                addTextViewToScrollView(scrollViewLayout, "🌪️ Focus on consistency: While luck is a major factor, staying calm and composed can improve your performance.");

                // Add a section on strategies
                addHeaderTextView(scrollViewLayout, "Strategies for Coin Flip:");
                addTextViewToScrollView(scrollViewLayout, "💰 Observe other players' tendencies: Some players may have patterns in their guesses.");
                addTextViewToScrollView(scrollViewLayout, "💰 Being in the minority for a flip is more favorable, as there is always a 50% chance to guess correctly.");
                addTextViewToScrollView(scrollViewLayout, "💰 Embrace the luck factor: The game is designed to be fun and unpredictable.");
            }
        });

        btnAppInfo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();

                addHeaderTextView(scrollViewLayout, "App Information:");

                // Add details about the app
                addTextViewToScrollView(scrollViewLayout, "🐦 Welcome to the Cycino Casino Practice App!");
                addTextViewToScrollView(scrollViewLayout, "🐦 This app provides users with a platform to practice popular casino games with artificial currency with friends.");
                addTextViewToScrollView(scrollViewLayout, "🐦 Whether you're a beginner or a seasoned player, this app is your guide to mastering casino classics--with the likes of Poker, Blackjack, Baccarat, and Coin Flips!");

                // Add a section for key features
                addHeaderTextView(scrollViewLayout, "Key Features:");
                addTextViewToScrollView(scrollViewLayout, "🎰 Comprehensive simulated games for Blackjack, Poker, Baccarat, Coin Flip, and more.");
                addTextViewToScrollView(scrollViewLayout, "🗣️ Easy-to-navigate social system that allows users to friend and play with desired users.");
                addTextViewToScrollView(scrollViewLayout, "😁 Users can create and personify their own user pages as well.");
                addTextViewToScrollView(scrollViewLayout, "💲 Artificial currency that tracks user success when playing, along with a leaderboard system tracking user statistics.");
                addTextViewToScrollView(scrollViewLayout, "💬 Two chatting systems: Gamechat with current lobby and direct messaging with one user.");

                // Add a section for usage tips
                addHeaderTextView(scrollViewLayout, "Usage Tips:");
                addTextViewToScrollView(scrollViewLayout, "🏠 Use the homepage to navigate throughout the app when deciding next actions.");
                addTextViewToScrollView(scrollViewLayout, "👤 Try friending users and blocking ones who you do not want to play with.");
                addTextViewToScrollView(scrollViewLayout, "🤔 Conduct different strategies and don't be afraid to try something new. Remember the currency is artificial.");
                addTextViewToScrollView(scrollViewLayout, "😴 Take breaks between games to stay focused and make better decisions.");
                addTextViewToScrollView(scrollViewLayout, "☹️ REMEMBER THAT IN REAL CASINOS, AND THIS ONE ALIKE, THE HOUSE ALWAYS WINS. ");
                addTextViewToScrollView(scrollViewLayout, "☎️ Call 1-800-522-4700 if you ever experience problems with gambling. ");

                // Add a section for developer notes
                addHeaderTextView(scrollViewLayout, "Developer Notes:");
                addTextViewToScrollView(scrollViewLayout, "🏫 This app is designed for educational purposes and does not involve real-money gambling.");
                addTextViewToScrollView(scrollViewLayout, "📈 Feedback and suggestions are welcome to improve your experience.");
                addTextViewToScrollView(scrollViewLayout, "❤️‍🩹 Remember: Gambling responsibly is key to an enjoyable experience.");
                // Add a closing note
                addHeaderTextView(scrollViewLayout, "Enjoy the App!");
                addTextViewToScrollView(scrollViewLayout, "🤗 We hope this app enhances your casino gaming experience and prepares you for the Belaggio. Good luck and have fun!");

            }


        });

        backBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearScrollView();
                Intent i = new Intent(RulesActivity.this,HomePageActivity.class);
                i.putExtra("USERNAME",username);
                i.putExtra("UUID",userID);
                startActivity(i);
            }


        });


    }

    private void clearScrollView() {
        scrollViewLayout.removeAllViews();
    }

    private void addTextViewToScrollView(LinearLayout parent, String text) {
        TextView textView = new TextView(this);
        textView.setText(text);
        textView.setTextSize(16);
        textView.setLineSpacing(1.2f, 1.2f);
        textView.setPadding(8, 8, 8, 8);
        parent.addView(textView);
    }

    private void addHeaderTextView(LinearLayout parent, String text) {
        TextView header = new TextView(this);
        header.setText(text);
        header.setTextSize(20);
        header.setTypeface(null, android.graphics.Typeface.BOLD);
        header.setPadding(8, 16, 8, 8); // Add more padding for separation
        parent.addView(header);
        addSectionSpacing(scrollViewLayout);
    }

    private void addIndentedTextView(LinearLayout parent, String text) {
        TextView textView = new TextView(this);
        textView.setText(text);
        textView.setTextSize(18);
        textView.setPadding(32, 8, 8, 8); // Indent the text with more left padding
        parent.addView(textView);
    }

    private void addSectionSpacing(LinearLayout parent) {
        TextView spacer = new TextView(this);
        spacer.setHeight(16); // Add vertical space
        parent.addView(spacer);
    }

}
