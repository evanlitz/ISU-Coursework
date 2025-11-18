package coms309.Cycino.signup;

import coms309.Cycino.login.LoginInfo;
import coms309.Cycino.login.LoginService;
import coms309.Cycino.users.User;
import coms309.Cycino.users.UsersRepository;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class SignupService {

    @Autowired
    private LoginService loginService;

    public Map<String, Object> signup(LoginInfo user){
        Map<String, Object> response = new HashMap<>();
        if(loginService.containsUser(user.getUsername()).get("status").equals("200 ok")){
            response.put("status", "500");
            response.put("error", "User already exists");
            return response;
        }
        loginService.addUser(user);
        response.put("status", "200 ok");
        response.put("Id", user.getId());
        return response;
    }
}
