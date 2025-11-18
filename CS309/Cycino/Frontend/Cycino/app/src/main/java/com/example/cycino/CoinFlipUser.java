package com.example.cycino;

public class CoinFlipUser {

    String username;
    String pick;
    Integer bet;

    CoinFlipUser() {
        username = null;
        pick = null;
        bet = 0;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPick() {
        return pick;
    }

    public void setPick(String pick) {
        this.pick = pick;
    }

    public Integer getBet() {
        return bet;
    }

    public void setBet(Integer bet) {
        this.bet = bet;
    }


}
