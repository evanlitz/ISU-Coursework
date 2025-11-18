package coms309.Cycino.Games.baccarat;

import java.util.Random;

public class BaccaratCard {
    private String name;
    private String suit;
    private int value;

    public BaccaratCard(String name, String suit, int value) {
        this.name = name;
        this.suit = suit;
        if (value >= 10){
            this.value = 0;
        } else{
            this.value = value;
        }
    }

    public String getName() {
        return name;
    }

    public int getValue(){
        return value;
    }

    public String getSuit(){
        return suit;
    }

    public String toString() {
        return suit + "_" + name;
    }
}
