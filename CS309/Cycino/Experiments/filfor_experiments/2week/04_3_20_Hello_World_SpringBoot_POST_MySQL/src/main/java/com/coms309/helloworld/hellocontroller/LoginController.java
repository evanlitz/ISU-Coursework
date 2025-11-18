package com.coms309.helloworld.hellocontroller;

import com.coms309.helloworld.repository.LoginRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import com.coms309.helloworld.entity.Login;

import java.util.List;
import java.util.Optional;

@RequestMapping("/test")
@RestController
public class LoginController {
    @Autowired
    private LoginRepository loginRepository;

    @GetMapping("/hello")
    public String hello() {return "Hello World!";}

    @PostMapping("/login")
    public String receiveData(@RequestParam String username, @RequestParam String password) {
        System.out.println("Received data: " + username + " " + password);
        Login user = new Login(username, password);
        loginRepository.save(user);
        return "User received: " + user.toString();
    }

    @PostMapping("/login/json")
    public String receiveDataJson(@RequestBody Login login) {
        System.out.println("Received data: " + login.toString());
        System.out.println("login.getUsername() " + login.getUsername());
        System.out.println("login.getPassword() " + login.getPassword());
        //Login user = new Login(login.getUsername(), login.getPassword());
        //loginRepository.save(user);
        loginRepository.save(login);
        return "User received: " + login.toString();
    }

    @GetMapping("/users/{id}")
    public Optional<Login> getUserById(@PathVariable long id) {
        return loginRepository.findById(id);
    }

    @GetMapping("/users")
    public List<Login> getUsers() {
        return loginRepository.findAll();
    }
}
