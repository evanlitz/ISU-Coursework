package coms309.Cycino.GameSettings.BlackJack;

import coms309.Cycino.Games.Blackjack.BlackJack;
import coms309.Cycino.users.User;
import coms309.Cycino.users.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class BlackJackSettingsService {
    @Autowired
    private BlackJackSettingsRepository blackJackSettingsRepository;
    @Autowired
    private UserService userService;

    public BlackJackSettings getBlackJackSettings(Long id) {
        List<BlackJackSettings> blackJackSettingsAll = blackJackSettingsRepository.findAll();
        System.out.println("id: ");
        System.out.println(id);
        System.out.println(blackJackSettingsAll);
        for(BlackJackSettings settings : blackJackSettingsAll) {
            if(settings.getUserId().equals(id)) {
                return settings;
            }
        }
        return null;
    }

    @Transactional
    public Boolean updateBlackJackSettings(BlackJackSettings settings, Long id) {
        boolean ok = false;
        User user = userService.getUser(id);
        BlackJackSettings userSettings = user.getBlackJackSettings();
        if(userSettings.getUserId().equals(id)) {
            userSettings.setDealerStandOn(settings.getDealerStandOn());
            userSettings.setAmountOfDecks(settings.getAmountOfDecks());
            userSettings.setMaxBet(settings.getMaxBet());
            userSettings.setMinBet(settings.getMinBet());
            ok = true;
        }
        return ok;
    }
}
