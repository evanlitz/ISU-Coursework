package coms309.Cycino.directMessaging;

import java.io.IOException;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.Set;

import coms309.Cycino.follow.FollowService;
import coms309.Cycino.groupChat.GroupChat;
import coms309.Cycino.groupChat.GroupChatService;
import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import jakarta.websocket.OnClose;
import jakarta.websocket.OnError;
import jakarta.websocket.OnMessage;
import jakarta.websocket.OnOpen;
import jakarta.websocket.Session;
import jakarta.websocket.server.PathParam;
import jakarta.websocket.server.ServerEndpoint;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Configurable;
import org.springframework.stereotype.Controller;

@Configurable
@Controller      // this is needed for this to be an endpoint to springboot
@ServerEndpoint(value = "/directMessaging/{userID}")  // this is Websocket url
public class DirectMessagingSocket {

    // cannot autowire static directly (instead we do it by the below method)  
    private static MessageRepository msgRepo;
    private static FollowService followService;
    private static UserService userService;
    private static GroupChatService groupChatService;

    /*
     * Grabs the MessageRepository singleton from the Spring Application
     * Context.  This works because of the @Controller annotation on this
     * class and because the variable is declared as static.
     * There are other ways to set this. However, this approach is
     * easiest.
     */
    @Autowired
    public void setMessageRepository(MessageRepository repo) {
        msgRepo = repo;  // we are setting the static variable
    }
    @Autowired
    public void setFollowService(FollowService followService) {this.followService = followService;}
    @Autowired
    public void setGroupChatService(GroupChatService groupChatService) {this.groupChatService = groupChatService;}
    @Autowired
    public void setUserService(UserService userService) {this.userService = userService;}

    // Store all socket session and their corresponding username.
    private static Map<Session, Long> sessionUserMap = new Hashtable<>();
    private static Map<Long, Session> userSessionMap = new Hashtable<>();

    private final Logger logger = LoggerFactory.getLogger(DirectMessagingSocket.class);

    @OnOpen
    public void onOpen(Session session, @PathParam("userID") Long user)
            throws IOException {

        // WORKING ON USING USER ID INSTEAD OF USERNAME; PERHAPS I SHOULD ONLY CARE ABOUT USERID,
        // SINCE IT IS THE ONLY THING GUARANTEED TO BE UNIQUE?
        //
        logger.info("Entered into Open");
        // store connecting user information
        sessionUserMap.put(session, user);
        userSessionMap.put(user, session);

        /*
        //Send chat history to the newly connected user
        sendMessageToParticularUser(user, getChatHistory());


        // broadcast that new user joined
        String message = "User:" + user + " has Joined the Chat";
        broadcast(message);
        */
    }


    @OnMessage
    public void onMessage(Session session, String message) throws IOException {

        // Handle new messages
        logger.info("Entered into Message: Got Message:" + message);

        // Get user from the session
        Long user = sessionUserMap.get(session);

        // Direct message to a user using the format "@username <message>"
        if (message.startsWith("@")) {
            directMessage(message, user);
        } else if (message.startsWith("#")) {
            groupMessage(message, user);
        } else { // broadcast
            sendMessageToParticularUser(user, "Your message is lacking a recipient, please try again.");
            //broadcast(user + ": " + message);
        }
    }


    @OnClose
    public void onClose(Session session) throws IOException {
        logger.info("Entered into Close");

        // remove the user connection information
        Long user = sessionUserMap.get(session);
        sessionUserMap.remove(session);
        userSessionMap.remove(user);

        // broadcase that the user disconnected
        String message = user + " disconnected";
        broadcast(message);
    }


    @OnError
    public void onError(Session session, Throwable throwable) {
        // Do error handling here
        logger.info("Entered into Error");
        throwable.printStackTrace();
    }


    private void sendMessageToParticularUser(Long user, String message) {
        Session session = userSessionMap.get(user);
        if (session != null) {
            try {
                session.getBasicRemote().sendText(message);
            }
            catch (IOException e) {
                logger.info("Exception: " + e.getMessage().toString());
                e.printStackTrace();
            }
        } else {
          logger.info("Session for recipient is null");
        }
    }


    private void broadcast(String message) {
        sessionUserMap.forEach((session, username) -> {
            try {
                session.getBasicRemote().sendText(message);
            }
            catch (IOException e) {
                logger.info("Exception: " + e.getMessage().toString());
                e.printStackTrace();
            }

        });

    }


    // Gets the Chat history from the repository
    private String getChatHistory() {
        List<Message> messages = msgRepo.findAll();

        // convert the list to a string
        StringBuilder sb = new StringBuilder();
        if(messages != null && messages.size() != 0) {
            for (Message message : messages) {
                sb.append(message.getUid().toString() + ": " + message.getContent() + "\n");
            }
        }
        return sb.toString();
    }

    public boolean isRecipientFollowingSender(Long sender, Long recipient) {
        List<Long> followersOfSender = followService.getFollowers(sender);
        if (followersOfSender.contains(recipient)) {
            return true;
        } else {
            return false;
        }
    }

    public void directMessage(String message, Long user ){
        // Figure out the recipient of the message
        Long recipient = Long.parseLong(message.split(" ")[0].substring(1));
        if (isRecipientFollowingSender(user, recipient)) {
            // Isolate the content of the message
            String messageContent = message.split(" ", 2)[1];
            // send the message to the sender and receiver
            sendMessageToParticularUser(recipient, "[DM] " + user + ": " + message);
            sendMessageToParticularUser(user, "[DM] " + user + ": " + message);

            // Saving message to message repository
            msgRepo.save(new Message(user, recipient, messageContent));
        } else {
            // Don't send the message if the recipient is not following the user
            sendMessageToParticularUser(user, "The recipient of your message is not following you, please try again.");
        }
    }

    public void groupMessage(String message, Long uid) {
        // Get the sending user
        User user = userService.getUser(uid);
        // Figure out the receiving group of message
        Long groupID = Long.parseLong(message.split(" ")[0].substring(1));
        // Isolate the content of the message
        String messageContent = message.split(" ", 2)[1];
        // Get the members of the group
        Set<User> groupMembers = groupChatService.getUsersInGroupChat(groupID);

        // See if sender is a member in said group
        if (groupChatService.isUserInGroupChat(uid, groupID)) {
            // Get the group object so we can retrieve its name
            GroupChat groupChat = groupChatService.getGroupChat(groupID);
            for (User member : groupMembers) {
                sendMessageToParticularUser(member.getId(), "Group:" + groupChat.getGroupName() + " | " + user.getFirstName() + " " + user.getLastName() + ": " + messageContent);
            }
        } else {
            sendMessageToParticularUser(uid, "You are not part of the group you are trying to send to. Please try again.");
        }
    }
} // end of Class
