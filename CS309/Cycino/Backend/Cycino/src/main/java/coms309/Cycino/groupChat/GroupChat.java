package coms309.Cycino.groupChat;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import coms309.Cycino.users.User;

import java.util.HashSet;
import java.util.Set;

@Entity
public class GroupChat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String groupName;

    @ManyToMany(fetch = FetchType.EAGER, mappedBy = "groupChats")
    @JsonIgnore
    private Set<User> users = new HashSet<>();

    public void setId(Long id) {this.id = id;}
    public Long getId() {return id;}

    public void addUser(User user) {
        this.users.add(user);
        user.getGroupChats().add(this);
    }

    public void removeUser(User user) {
        this.users.remove(user);
        user.getGroupChats().remove(this);
    }

    public Set<User> getUsers() {
        return users;
    }

    public void setUsers(Set<User> users) {
        this.users = users;
    }

    public void setGroupName(String groupName) {
        this.groupName = groupName;
    }
    public String getGroupName() {
        return groupName;
    }
}
