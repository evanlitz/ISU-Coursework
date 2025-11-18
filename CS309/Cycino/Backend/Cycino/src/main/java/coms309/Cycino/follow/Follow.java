package coms309.Cycino.follow;

import coms309.Cycino.users.User;
import jakarta.persistence.*;

@Entity
@Table(name = "follow")
public class Follow {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    //@Column(name = "follower")
    private long followingID;

    private boolean muteNotifications = false;

    private boolean blockUser = false;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "fk_user_ID")
    private User user;

    // Constructors
    public Follow() {}
    public Follow(long followingID) {
        this.followingID = followingID;
    }

    // Getters & Setters
    public int getId() {return id;}
    public void setId(int id) {this.id = id;}

    public long getForeignKey(){return user.getId();}

    public long getFollowingID() {return followingID;}
    public void setFollowingID(long followingID) {this.followingID = followingID;}

    public boolean isMuteNotifications() {return muteNotifications;}
    public void setMuteNotifications(boolean muteNotifications) {this.muteNotifications = muteNotifications;}

    public boolean isBlockUser() {return blockUser;}
    public void setBlockUser(boolean blockUser) {this.blockUser = blockUser;}

    @Override
    public String toString() {
        return "Follow{" +
                "id=" + id +
                ", followingID=" + followingID +
                ", muteNotifications=" + muteNotifications +
                ", user=" + user +
                '}';
    }
}
