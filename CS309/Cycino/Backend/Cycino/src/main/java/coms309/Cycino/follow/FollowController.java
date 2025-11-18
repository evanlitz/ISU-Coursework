package coms309.Cycino.follow;

import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class FollowController {
    @Autowired
    private FollowService followService;
    @Autowired
    private UserService userService;

    @PostMapping("/users/{uid}/follow")
    public Map<String, Object> addToFollowList(@RequestBody Follow follow, @PathVariable long uid){
        Map<String, Object> result = new HashMap<>();
        if (followService.addToFollowList(follow, uid)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request");
        }
        return result;
    }

    @GetMapping("/users/{uid}/following")
    public List<Follow> getFollowingList(@PathVariable long uid) {
        return followService.getFollowingList(uid);
    }

    @GetMapping("users/{uid}/followers")
    public List<Long> getFollowersList(@PathVariable long uid) {
        return followService.getFollowers(uid);
    }

    @PutMapping("/users/{uid}/follow/update")
    public Map<String, Object> updateFollowing(@RequestBody Follow follow, @PathVariable long uid){
        Map<String, Object> result = new HashMap<>();
        if (followService.updateFollowing(follow, uid)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request");
        }
        return result;
    }

    @PutMapping("/users/{uid}/block")
    public Map<String, Object> blockUser(@RequestBody Follow follow, @PathVariable long uid){
        Map<String, Object> result = new HashMap<>();
        if (followService.blockUser(follow, uid)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request");
        }
        return result;
    }

    @PutMapping("/users/{uid}/unblock")
    public Map<String, Object> unblockUser(@RequestBody Follow follow, @PathVariable long uid){
        Map<String, Object> result = new HashMap<>();
        if (followService.unblockUser(follow, uid)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request");
        }
        return result;
    }

    @DeleteMapping("/users/{uid}/unfollow/{unfollowID}")
    public Map<String, Object> removeFromFollowList(@PathVariable long uid, @PathVariable long unfollowID){
        Map<String, Object> result = new HashMap<>();
        if (followService.removeFromFollowList(uid, unfollowID)){
            result.put("status", "200 OK");
        } else {
            result.put("status", "400 Bad Request");
        }
        return result;
    }
}
