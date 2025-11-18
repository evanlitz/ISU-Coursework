package coms309.Cycino.groupChat;

import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import coms309.Cycino.users.UsersRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
public class GroupChatController {
    @Autowired
    UsersRepository usersRepository;
    @Autowired
    GroupChatRepository groupChatRepository;
    @Autowired
    UserService userService;
    @Autowired
    GroupChatService groupChatService;

    @GetMapping("/directMessaging/{uid}/groupChats")
    public Set<GroupChat> groupChat(@PathVariable Long uid) {
        return groupChatService.getUsersGroupChats(uid);
    }

    @GetMapping("directMessaging/groupChats/{groupchatID}")
    public Set<User> usersInGroupChat(@PathVariable Long groupchatID) {
        return groupChatService.getUsersInGroupChat(groupchatID);
    }

    @Transactional
    @PutMapping("/directMessaging/groupChats/{groupchatID}/addUser/{userID}")
    public Map<String, Object> addUser(@PathVariable Long groupchatID, @PathVariable Long userID) {
        Map<String, Object> response = new HashMap<>();
        User addUser = userService.getUser(userID);
        // Just find correct groupChat, then add correct user to said groupChat
        List<GroupChat> groupChats = groupChatRepository.findAll();
        for (GroupChat groupChat : groupChats) {
            if (groupChat.getId().equals(groupchatID)) {
                groupChat.addUser(addUser);
                response.put("status", "200 OK");
                return response;
            }
        }
        response.put("status", "400 Bad Request");
        return response;
    }

    @Transactional
    @PutMapping("/directMessaging/groupChats/{groupchatID}/removeUser/{userID}")
    public Map<String, Object> removeUser(@PathVariable Long groupchatID, @PathVariable Long userID) {
        Map<String, Object> response = new HashMap<>();
        User addUser = userService.getUser(userID);
        // Just find correct groupChat, then add correct user to said groupChat
        List<GroupChat> groupChats = groupChatRepository.findAll();
        for (GroupChat groupChat : groupChats) {
            if (groupChat.getId().equals(groupchatID)) {
                groupChat.removeUser(addUser);
                response.put("status", "200 OK");
                return response;
            }
        }
        response.put("status", "400 Bad Request");
        return response;
    }

    @PostMapping("/directMessaging/{uid}/groupChats/create")
    public Map<String, Object> createGroupChat(@PathVariable Long uid, @RequestBody String name) {
        Map<String, Object> response = new HashMap<>();
        try {
            User user = userService.getUser(uid);
            GroupChat groupChat = new GroupChat();
            groupChat.setGroupName(name);
            user.addGroupChat(groupChat);
            groupChatRepository.save(groupChat);
            response.put("status", "200 OK");
        } catch(Exception e) {
            response.put("error", e.getMessage());
        }
        return response;
    }

    @DeleteMapping("directMessaging/groupChats/delete/{groupchatID}")
    public Map<String, Object> deleteGroupChat(@PathVariable Long groupchatID) {
        Map<String, Object> response = new HashMap<>();
        Optional<GroupChat> groupChat = groupChatRepository.findById(groupchatID);
        if (groupChat.isPresent()) {
            Set<User> usersCopy = new HashSet<>(groupChat.get().getUsers());
            for (User user : usersCopy) {
                user.removeGroupChat(groupChat.get());
            }
            groupChatRepository.delete(groupChat.get());
            response.put("status", "200 OK");
        } else {
            response.put("status", "400 Bad Request");
        }
        return response;
    }
}
