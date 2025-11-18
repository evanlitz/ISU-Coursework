package coms309.Cycino.login;

import coms309.Cycino.users.User;
import coms309.Cycino.users.UsersRepository;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;

@Service
public class LoginService {

    @Autowired
    private LoginRepository loginRepository;
    @Autowired
    private UsersRepository repo;
    @Autowired
    private UserService service;

    public Map<String, Object> checkInfo(String username, String password){
        Map<String, Object> response = new HashMap<>();
        if(containsUser(username).get("status").equals("200 ok")){
            LoginInfo l = getUser(username);
             if(l.getPassword().equals(password)){
                 response.put("status", "200 ok");
                 response.put("Id", l.getId());
                 return response;
             };
             response.put("status", "404 not found");
            response.put("error", "Wrong Password");
            return response;
        }
        response.put("status", "404 not found");
        response.put("error", "Wrong username");
        return response;

    }

    public LoginInfo getUser(String username){

        List<LoginInfo> users = new ArrayList<>(loginRepository.findAll());
        for(LoginInfo u : users){
            if(u.getUsername().equalsIgnoreCase(username)){
                return u;
            }
        }
        return null;
    }

    public LoginInfo getUser(long id){
        return loginRepository.findById(id).orElse(null);
    }

    public Map<String, Object> containsUser(String username){

        Map<String, Object> response = new HashMap<>();
        List<LoginInfo> users = new ArrayList<>(loginRepository.findAll());
        for(LoginInfo u : users){
            if(u.getUsername().equalsIgnoreCase(username)){
                response.put("status", "200 ok");
                response.put("user", u.getUser());
                return response;
            }
        }
        response.put("status", "404 not found");
        return response;
    }

    public void addUser(LoginInfo user){
        User user2 = service.create(user);
        user.setUser(user2);
        user2.setUserName(user.getUsername());
        repo.save(user2);
        loginRepository.save(user);
    }

    public Map<String, Object> setUser(String username, User user){
        Map<String, Object> response = new HashMap<>();

        LoginInfo login = getUser(username);
        if(login == null){
            response.put("status", "404 not found");
            response.put("error", "No user with that username");
            return response;
        }
        login.setUser(user);
        response.put("status", "200 ok");
        return response;
    }

    public Map<String, Object> deleteUser(String username){
        Map<String, Object> response = new HashMap<>();
        LoginInfo login = getUser(username);
        User u = login.getUser();
        if(u != null){
            repo.delete(u);
            loginRepository.deleteById(login.getId());
            response.put("status", "200 ok");
            return response;
        }
        response.put("status", "404 not found");
        response.put("error", "No user with that id");
        return response;

    }

    public Map<String, Object> update(LoginInfo login, String username){
        Map<String, Object> response = new HashMap<>();
        if(getUser(username) == null){
            response.put("status", "404");
            response.put("error", "no user with that id");
            return response;
        }
        LoginInfo temp = getUser(username);
        response.put("status", "200 ok");
        if(login.getUsername() == null && login.getPassword() == null){
            response.put("update", "No update to user");
            return response;
        }
        if(login.getUsername() != null){
            temp.setUsername(login.getUsername());
            temp.getUser().setUserName(login.getUsername());
            response.put("username", login.getUsername());
        }
        if(login.getPassword() != null){
            temp.setPassword(login.getPassword());
            response.put("password", login.getPassword());
        }
        repo.save(temp.getUser());
        loginRepository.save(temp);
        return response;
    }

}
