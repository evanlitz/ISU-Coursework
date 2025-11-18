package coms309.Cycino;

import coms309.Cycino.directMessaging.DirectMessagingSocket;
import coms309.Cycino.follow.FollowService;
import org.springframework.beans.factory.annotation.Configurable;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.web.socket.server.standard.ServerEndpointExporter;

@Configurable
@Configuration
@ConditionalOnMissingBean(ServerEndpointExporter.class)
@Profile("!test")
public class WebSocketConfig {
    @Bean
    public ServerEndpointExporter serverEndpointExporter() {
        return new ServerEndpointExporter();
    }
}
