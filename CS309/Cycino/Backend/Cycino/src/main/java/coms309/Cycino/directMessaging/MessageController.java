package coms309.Cycino.directMessaging;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
public class MessageController {

    @Autowired
    private MessageRepository msgRepo;

    @GetMapping("/directMessaging/history/{sender}/{receiver}")
    private List<Message> getChatHistory(@PathVariable Long sender, @PathVariable Long receiver) {
        List<Message> messages = msgRepo.findAll();
        List<Message> chatHistory = new ArrayList<>();
        for (Message message : messages) {
            if ((message.getUid().equals(sender) && message.getRecipient() == (receiver)) || (message.getUid().equals(receiver) && message.getRecipient() == sender)) {
                chatHistory.add(message);
            }
        }
        return chatHistory;
    }
}
