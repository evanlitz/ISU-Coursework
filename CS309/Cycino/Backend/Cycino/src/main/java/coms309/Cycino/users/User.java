package coms309.Cycino.users;

import com.fasterxml.jackson.annotation.JsonIgnore;
import coms309.Cycino.Enums;
import coms309.Cycino.GameSettings.BlackJack.BlackJackSettings;
import coms309.Cycino.Games.GameLogic.PlayerHands;
import coms309.Cycino.follow.Follow;
import coms309.Cycino.groupChat.GroupChat;
import coms309.Cycino.lobby.Lobby;
import coms309.Cycino.login.LoginInfo;
import coms309.Cycino.stats.GameHistory;
import coms309.Cycino.stats.UserStats;
import jakarta.persistence.*;

import coms309.Cycino.GameSettings.BlackJack.BlackJackSettingsRepository;
import java.io.Serializable;
import java.util.*;

@Entity
@Table(name = "users") // escaping using double quotes for H2 SQL compatibility
public class User implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    @Column(name = "id")
    private Long id;
    private String username;
    private String firstName;
    private String lastName;
    private String phoneNumber;
    private double chips;
    @Enumerated(EnumType.STRING)
    private Enums.Roles role = Enums.Roles.BEGINNER;
    private String userBiography;

    @OneToOne(mappedBy = "user")
    @JsonIgnore
    private BlackJackSettings blackJackSettings;


    @OneToMany(cascade = CascadeType.ALL)
    @JoinColumn(name = "fk_user_ID", referencedColumnName = "id")
    private List<Follow> followList;

    @OneToMany(cascade = CascadeType.ALL)
    @JoinColumn(name = "user_id", referencedColumnName = "id")
    private List<UserStats> userStatslist;

    @OneToOne(cascade = CascadeType.ALL)
    @JsonIgnore
    private LoginInfo loginInfo;

    @ManyToOne
    private Lobby lobby;

    @OneToMany
    private Set<PlayerHands> hands = new HashSet<>();

    @ManyToMany
    @JoinTable(
            name = "user_game_history",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "game_history_id")
    )
    private Set<GameHistory> gameHistories;

    @ManyToMany(cascade = CascadeType.ALL)
    @JoinTable(
            name = "user_groupchat",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "groupChat_id")
    )
    private Set<GroupChat> groupChats = new HashSet<>();

    public User(){
        chips = 1000;
    }

    public User(Long id, String firstName, String lastName, String phoneNumber, Enums.Roles role, String userBiography, List<Follow> followList, LoginInfo loginInfo, BlackJackSettings blackJackSettings) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.phoneNumber = phoneNumber;
        this.role = role;
        this.userBiography = userBiography;
        this.followList = followList;
        this.loginInfo = loginInfo;
        this.blackJackSettings = blackJackSettings;
        this.username = loginInfo.getUsername();
        chips = 1000;
    }

    public void addGroupChat(GroupChat groupChat){
        groupChats.add(groupChat);
        groupChat.getUsers().add(this);
    }

    public void setUserName(String username){
        this.username = username;
    }

    public void removeGroupChat(GroupChat groupChat){
        this.groupChats.remove(groupChat);
        groupChat.getUsers().remove(this);
    }

    public Set<GroupChat> getGroupChats() {
        return groupChats;
    }

    public void setGroupChats(Set<GroupChat> groupChats) {
        this.groupChats = groupChats;
    }

    public BlackJackSettings getBlackJackSettings() {
        return this.blackJackSettings;
    }

    public String getUsername(){
        username = loginInfo.getUsername();
        return username;
    }

    public void setBlackJackSettings(BlackJackSettings blackJackSettings) {
        this.blackJackSettings = blackJackSettings;
    }
    public List<Follow> getFollowList() {
        return followList;
    }
    public void setFollowList(List<Follow> followList) {
        this.followList = followList;
    }
    public void newFollow(Follow follow){
        this.followList.add(follow);
    }
    public void removeFollow(Follow follow){
        this.followList.remove(follow);
    }

    public long getId(){
        //this.username = loginInfo.getUsername();
        return id;
    }

    public String getFirstName(){
        return firstName;
    }

    public LoginInfo getLoginInfo() {
        return loginInfo;
    }

    public String getLastName() {
        return lastName;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public Enums.Roles getRole(){
        return role;
    }

    public void setRole(Enums.Roles role){
        this.role = role;
    }


    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setLoginInfo(LoginInfo loginInfo) {
        this.loginInfo = loginInfo;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public String getUserBiography() {return userBiography;}
    public void setUserBiography(String userBiography) {this.userBiography = userBiography;}

    public String[] getContact(){
        return new String[]{firstName, lastName, phoneNumber};
    }
    public void updateRole(String role){
        this.role = Enums.Roles.valueOf(role.toUpperCase());
    }

    @Override
    public String toString() {
        return "User{" +
                "firstName='" + firstName + '\'' +
                ", lastName='" + lastName + '\'' +
                ", phoneNumber='" + phoneNumber + '\'' +
                ", role=" + role +
                ", userBiography='" + userBiography + '\'' +
                ", loginInfo=" + loginInfo +
                ", id=" + id +
                '}';
    }
    public void setId(long id){
        this.id=id;
    }


    public Set<GameHistory> getGameHistories(){
        return gameHistories;
    }

    public double getChips(){
        return chips;
    }

    public void addGameHistory(GameHistory gameHistory){
        gameHistories.add(gameHistory);
    }

    public void addChips(double chips){
        this.chips += chips;
    }
}
