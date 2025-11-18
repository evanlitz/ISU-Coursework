package coms309.Cycino.GameSettings.BlackJack;
import coms309.Cycino.GameSettings.BlackJack.BlackJackSettingsRepository;

import coms309.Cycino.users.User;
import jakarta.persistence.*;

@Entity
public class BlackJackSettings {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;

    private int dealerStandOn;
    private int maxBet;
    private int minBet;
    private int amountOfDecks;

    // Constructors
    public BlackJackSettings() {}
    public BlackJackSettings(int dealerStandOn, int maxBet, int minBet, int amountOfDecks) {
        this.dealerStandOn = dealerStandOn;
        this.maxBet = maxBet;
        this.minBet = minBet;
        this.amountOfDecks = amountOfDecks;
    }
    // Getters & Setters
    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public User getUser() {
        return user;
    }

    public Long getUserId() {
        return this.user.getId();
    }

    public int getDealerStandOn() {
        return dealerStandOn;
    }

    public void setDealerStandOn(int dealerStandOn) {
        this.dealerStandOn = dealerStandOn;
    }

    public int getMaxBet() {
        return maxBet;
    }

    public void setMaxBet(int maxBet) {
        this.maxBet = maxBet;
    }

    public int getMinBet() {
        return minBet;
    }

    public void setMinBet(int minBet) {
        this.minBet = minBet;
    }

    public int getAmountOfDecks() {
        return amountOfDecks;
    }

    public void setAmountOfDecks(int amountOfDecks) {
        this.amountOfDecks = amountOfDecks;
    }
}
