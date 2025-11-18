package coms309.Cycino.users;

import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import coms309.Cycino.follow.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class UserController {

    @Autowired
    private UserService userService;

    @RequestMapping(method = RequestMethod.GET, path = "/users")
    public List<User> getUsers(){
        return userService.getUsers();
    }

    @PutMapping("/users/update/{id}")
    public Map<String, Object> create(@RequestBody User user, @PathVariable long id){
        Map<String, Object> result = new HashMap<>();
        if (userService.create(user, id)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request"); //User probably does not exist
        }
        return result;
    }

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable long id){
        return userService.getUser(id);
    }




}
