package coms309.Cycino.login;

import com.fasterxml.jackson.annotation.JsonIgnore;
import coms309.Cycino.users.User;
import jakarta.persistence.*;
import org.hibernate.annotations.Cascade;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.io.Serializable;

@Entity
public class LoginInfo implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String username;
    private String password;

    @JdbcTypeCode(SqlTypes.JSON)
    @OneToOne(cascade = CascadeType.REMOVE)
    @JsonIgnore
    private User user;

    public LoginInfo(){}

    public LoginInfo(String username, String password){
        //id = new Random().nextLong(0, 999999999);
        this.username = username;
        this.password = password;
    }

    public String getUsername(){
        return username;
    }

    public String getPassword(){
        return password;
    }

    public long getId() {
        return id;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setUser(User user){
        this.user = user;
    }

    public User getUser(){
        return user;
    }
}
