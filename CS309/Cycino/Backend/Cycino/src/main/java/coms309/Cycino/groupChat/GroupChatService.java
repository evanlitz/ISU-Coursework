package coms309.Cycino.groupChat;


import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.Optional;
import java.util.Set;


@Service
public class GroupChatService {

    @Autowired
    GroupChatRepository groupChatRepository;
    @Autowired
    UserService userService;

    public Set<GroupChat> getUsersGroupChats(Long uid) {
        User user = userService.getUser(uid);
        return user.getGroupChats();
    }

    public Set<User> getUsersInGroupChat(Long groupchatID) {
        Optional<GroupChat> groupChat = groupChatRepository.findById(groupchatID);
        if (groupChat.isPresent()) {
            return groupChat.get().getUsers();
        } else {
            return null;
        }
    }

    public GroupChat getGroupChat(Long groupchatID) {
        Optional<GroupChat> groupChat = groupChatRepository.findById(groupchatID);
        if (groupChat.isPresent()) {
            return groupChat.get();
        } else {
            return null;
        }
    }

    public boolean isUserInGroupChat(Long userID, Long groupchatID) {
        Optional<GroupChat> groupChat = groupChatRepository.findById(groupchatID);
        if (groupChat.isPresent()) {
            for (User member : groupChat.get().getUsers()) {
                if (member.getId() == userID) {
                    return true;
                }
            }
        }
        return false;
    }
}
