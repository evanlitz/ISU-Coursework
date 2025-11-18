package coms309.Cycino.stats;

import coms309.Cycino.Enums;
import coms309.Cycino.users.User;
import jakarta.persistence.*;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Entity
public class UserStats {

    @Id
    private String userStatsId;

    private long user_Id;
    private String game;
    private int wins;
    private int losses;
    private double percentage;
    private double net;
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "Id")
    private User users;

    public UserStats(){}

    public UserStats(long userId, Enums.GameEnums game){
        this.user_Id = userId;
        this.userStatsId = userId + game.toString();
        this.game = game.toString();
    }

    public void setWinsLosses(int wins, int losses){
        this.wins = wins;
        this.losses = losses;
    }

    public void updateWins(int w, int l, int chips){
        wins += w;
        losses += l;
        net += chips;
        update();
    }

    private void update(){
        this.percentage = ((double)wins)/(losses+wins);
    }

    public int getWins(){
        return wins;
    }
    public int getLosses(){
        return losses;
    }

    public double getNet() {
        return net;
    }

    public double getPercentage() {
        return percentage;
    }

    public String getUserStatsId() {
        return userStatsId;
    }

    public long getUserId(){
        return user_Id;
    }

    public String getGame() {
        return game;
    }

}
