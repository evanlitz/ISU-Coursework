package coms309.Cycino.login;

import coms309.Cycino.users.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
public class LoginController {

    @Autowired
    private LoginService loginService;

    @GetMapping("/login/submit/{username}/{password}")
    public Map<String, Object> checkInfo(@PathVariable String username, @PathVariable String password){
        return loginService.checkInfo(username, password);
    }

    @GetMapping("/login/{id}")
    public LoginInfo getUser(@PathVariable long id){
        return loginService.getUser(id);
    }

    @GetMapping("/login/contains/{username}")
    public Map<String, Object> containsUser(@PathVariable String username){
        return loginService.containsUser(username);
    }

    @PostMapping("/login/setUser/{username}")
    public Map<String, Object> setUser(@RequestBody User user, String username){
        return loginService.setUser(username, user);
    }

    @PutMapping("/login/update/{username}")
    public Map<String, Object> updateUser(@RequestBody LoginInfo login, @PathVariable String username){
        return loginService.update(login, username);
    }

    @DeleteMapping("/login/delete/{username}")
    public Map<String, Object> deleteUser(@PathVariable String username){
        return loginService.deleteUser(username);
    }

}
