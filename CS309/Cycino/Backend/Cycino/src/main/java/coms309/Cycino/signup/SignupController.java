package coms309.Cycino.signup;

import coms309.Cycino.login.LoginInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class SignupController {


    @Autowired

    private SignupService signupService;

    @PostMapping("/signup/register")
    public Map<String, Object> signup(@RequestBody LoginInfo user){
        return signupService.signup(new LoginInfo(user.getUsername(), user.getPassword()));
    }
}
