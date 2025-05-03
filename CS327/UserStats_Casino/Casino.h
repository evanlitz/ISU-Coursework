#pragma once

#include "PC.h"       
#include <ncurses.h>  
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <random>     
#include <algorithm>
// make > compile_log.txt 2>&1



class Casino {
public:
    static void enterCasino(PC& player) {
        while (true)
        {
            clear();
            mvprintw(0, 0, "Welcome to the Dungeon Casino!");
            mvprintw(2, 0, "1. Play Slot Machine");
            mvprintw(3, 0, "2. Play Chest Roulette");
            mvprintw(4, 0, "3. Play Russian Roulette");
            mvprintw(5, 0, "4. Play Dungeon Scratch-Off");
            mvprintw(6, 0, "5. Play Spin the Wheel of Misfortune");
            mvprintw(7, 0, "ESC. Exit Casino");

            refresh();
            int ch = getch();
            if (ch == '1') {
                playSlotMachine(player);
            } 
            else if (ch == '2')
            {
                playTrapRoulette(player);
            }
            else if (ch == '3')
            {
                playRussianRoulette(player);
            }
            else if (ch == '4')
            {
                playScratchOff(player) ;
            }
            else if (ch == '5')
            {
                playWheelOfMisfortune(player);
            }
            else if (ch == 27) {
                break;
            }
        }
    }

    static void playTrapRoulette(PC& player) {
        int highlight = 0;
        while (true) {
            clear();
            mvprintw(0, 0, "Trap Roulette");
            mvprintw(2, 0, "Three chests lie before you...");
            mvprintw(3, 0, "Use the left and right arrow keys to pick a chest. Press ENTER to open it.");
    
            for (int i = 0; i < 3; i++) {
                int x = 10 + i * 15;
                int y = 6;
    
                mvprintw(y,     x, "+-------+");
                mvprintw(y + 1, x, "|       |");
                mvprintw(y + 2, x, "|   %d   |", i + 1);
                mvprintw(y + 3, x, "|       |");
                mvprintw(y + 4, x, "+-------+");
    
                if (i == highlight) {
                    mvprintw(y + 5, x + 1, "  ^ You");
                }
            }
    
            refresh();
            int ch = getch();
            if (ch == KEY_LEFT && highlight > 0) highlight--;
            else if (ch == KEY_RIGHT && highlight < 2) highlight++;
            else if (ch == '\n' || ch == '\r') break;
        }
    
        int selected = highlight;
    
        std::vector<std::string> outcomes = {"Treasure", "Nothing", "Trap"};
        std::shuffle(outcomes.begin(), outcomes.end(), std::default_random_engine(std::random_device{}()));
    
        clear();
        mvprintw(0, 0, "You chose chest %d...", selected + 1);
        usleep(800000);
        mvprintw(2, 0, "Opening...");
        refresh();
        usleep(1000000);
    
        std::string result = outcomes[selected];
    
        if (result == "Treasure") {
            int reward = rand() % 4;
            switch (reward) {
                case 0:
                    mvprintw(4, 0, "You feel tougher! +5 Defense!");
                    player.defense += 5;
                    break;
                case 1:
                    mvprintw(4, 0, "You feel healthier! +10 HP!");
                    player.hp = std::min(player.hp + 10, player.maxHP);
                    break;
                case 2:
                    mvprintw(4, 0, "You feel quicker! +15 Dodge!");
                    player.dodge += 15;
                    break;
                case 3:
                    mvprintw(4, 0, "You feel immortal! +20 Max HP!");
                    player.maxHP += 20;
                    break;
            }
        } else if (result == "Nothing") {
            mvprintw(4, 0, "Nothing inside... maybe next time.");
        } else if (result == "Trap") {
            int penalty = rand() % 4;
            switch (penalty) {
                case 0:
                    mvprintw(4, 0, "Armor break! -5 Defense!");
                    player.defense = std::max(0, player.defense - 5);
                    break;
                case 1:
                    mvprintw(4, 0, "Poisoned! -10 HP!");
                    player.hp -= 10;
                    if (player.hp <= 0) player.hp = 1;
                    break;
                case 2:
                    mvprintw(4, 0, "Clumsy now! -15 Dodge!");
                    player.dodge = std::max(0, player.dodge - 15);
                    break;
                case 3:
                    mvprintw(4, 0, "Drained! -20 Max HP!");
                    player.maxHP = std::max(10, player.maxHP - 20);
                    if (player.hp > player.maxHP) player.hp = player.maxHP;
                    break;
            }
        }
    
        mvprintw(6, 0, "Current HP: %d / %d", player.hp, player.maxHP);
        mvprintw(7, 0, "Defense: %d   Dodge: %d", player.defense, player.dodge);
        mvprintw(9, 0, "Press any key to return...");
        getch();
    }
    
    static void playScratchOff(PC& player) {
        clear();
        mvprintw(0, 0, "Dungeon Scratch-Off");
        mvprintw(2, 0, "Pick 5 tiles to scratch...");
    
        const int gridSize = 25;
        const int gridCols = 5;
        const int gridRows = 5;
    
        std::vector<std::string> symbols = {"+", "%", "$", "&", "!"};
        std::vector<std::string> grid(gridSize);
        for (int i = 0; i < gridSize; i++) {
            grid[i] = symbols[rand() % symbols.size()];
        }
    
        bool revealed[gridSize] = {false};
        int picks = 0;
        int matches[5] = {0};
    
        while (picks < 5) {
            clear();
            mvprintw(0, 0, "Dungeon Scratch-Off");
            mvprintw(2, 0, "Pick 5 tiles to scratch (1-25):");
    
            for (int i = 0; i < gridSize; i++) {
                int row = 4 + i / gridCols;
                int col = 2 + (i % gridCols) * 6;
                if (revealed[i]) {
                    mvprintw(row, col, "[ %s ]", grid[i].c_str());
                } else {
                    mvprintw(row, col, "[%2d]", i + 1);
                }
            }
    
            bool validInput = false;
            while (!validInput) {
                echo();
                char input[4];
                mvprintw(10 + gridRows, 0, "Enter tile number (1-25): ");
                clrtoeol();
                getnstr(input, 3);
                noecho();
    
                int index = atoi(input) - 1;
                if (index >= 0 && index < gridSize && !revealed[index]) {
                    revealed[index] = true;
                    for (int s = 0; s < symbols.size(); s++) {
                        if (grid[index] == symbols[s]) {
                            matches[s]++;
                            break;
                        }
                    }
                    picks++;
                    validInput = true;
                } else {
                    mvprintw(11 + gridRows, 0, "Invalid tile. Try again.");
                    clrtoeol();
                    refresh();
                    usleep(1000000);
                }
            }
        }
    
        int highest = *std::max_element(matches, matches + 5);
    
        clear();
        mvprintw(0, 0, "Your picks:");
        for (int i = 0; i < gridSize; i++) {
            int row = 2 + i / gridCols;
            int col = 2 + (i % gridCols) * 6;
            if (revealed[i]) {
                mvprintw(row, col, "[ %s ]", grid[i].c_str());
            } else {
                mvprintw(row, col, "[ # ]");
            }
        }
    
        mvprintw(8 + gridRows, 0, "Press any key to reveal the rest...");
        getch();
        clear();
    
        mvprintw(0, 0, "Results:");
        for (int i = 0; i < gridSize; i++) {
            int row = 2 + i / gridCols;
            int col = 2 + (i % gridCols) * 6;
            mvprintw(row, col, "[ %s ]", grid[i].c_str());
        }
    
        mvprintw(8 + gridRows, 0, "You revealed %d matching symbols.", highest);
    
        if (highest == 5) {
            mvprintw(10 + gridRows, 0, "JACKPOT!!!!!! All user stats have been tripled!");
            player.maxHP *= 3;
            player.hp *= 3;
            player.damage.base *= 3;
            player.damage.dice *= 3;
            player.damage.sides *= 3;
            player.dodge *= 3;
            player.defense *= 3;
            player.hit *= 3;
        } else if (highest == 4) {
            int effect = rand() % 3;
            switch (effect) {
                case 0:
                    player.damage.base *= 2;
                    player.damage.dice += 1;
                    player.damage.sides *= 2;
                    mvprintw(10 + gridRows, 0, "Reward: Damage has been increased!");
                    break;
                case 1:
                    player.hit += 10;
                    player.dodge += 15;
                    mvprintw(10 + gridRows, 0, "Reward: +10 critical hit and +15 dodge chance!");
                    break;
                case 2:
                    player.hp += 100;
                    player.maxHP += 100;
                    mvprintw(10 + gridRows, 0, "Reward: HP and Max HP have been increased by 100!");
                    break;
            }
        } else if (highest == 3) {
            player.maxHP += 25;
            mvprintw(10 + gridRows, 0, "Reward: +25 Max HP!");
        } else if (highest == 2) {
            player.hp -= 10;
            mvprintw(10 + gridRows, 0, "Penalty: You lose 10 HP");
        } else {
            player.hp -= 20;
            mvprintw(10 + gridRows, 0, "Penalty: You lose 20 HP.");
        }
    
        if (player.hp <= 0 || player.maxHP <= 0) {
            clear();
            mvprintw(0, 0, "You collapse from your own greed...");
            mvprintw(2, 0, "The ghost attendant takes your body towards soul collection.");
            mvprintw(4, 0, "You have died scratching for treasure.");
            refresh();
            usleep(4000000);
            endwin();
            printf("\nGAME OVER: You died in the casino scratch-off.\n");
            exit(1);
        }
    
        mvprintw(12 + gridRows, 0, "Current HP: %d / %d", player.hp, player.maxHP);
        mvprintw(13 + gridRows, 0, "Damage: %d + %dd%d", player.damage.base, player.damage.dice, player.damage.sides);
        mvprintw(15 + gridRows, 0, "Press any key to return...");
        getch();
    }
    
    
    

    static void playRussianRoulette(PC& player) {
        clear();
        mvprintw(0, 0, "       .-.");
        mvprintw(1, 0, "      (o o)   The ghost dealer stares at you...");
        mvprintw(2, 0, "      | O \\   ");
        mvprintw(3, 0, "     \\|_/_|    A revolver lies between you.");
        mvprintw(4, 0, "     //   \\\\  ");
        mvprintw(5, 0, "    (|     |) ");
        mvprintw(6, 0, "   /_\\___/_\\  ");
        mvprintw(7, 0, "    |__|__|   ====[@]   <- revolver");
        refresh();
        usleep(3000000);
        clear();    
        mvprintw(0, 0, "~~~~ Russian Roulette ~~~~");
        mvprintw(2, 0, "The ghost dealer loads one bullet into a 6-chamber revolver...");
        mvprintw(3, 0, "He spins the cylinder, aims at you, and smiles.");
        refresh();
        usleep(2000000);
    
        for (int i = 0; i < 10; i++) {
            clear();
            mvprintw(0, 0, "Spinning the cylinder...");
            mvprintw(2, 0, "[%c]", "-\\|/"[i % 4]);
            refresh();
            usleep(150000);
        }
    
        int chamber = rand() % 6;
        clear();
        mvprintw(0, 0, "The ghost raises the revolver to your head...");
        refresh();
        usleep(1500000);
    
        if (chamber == 0) {
            mvprintw(2, 0, "BANG! You have been shot.");
            mvprintw(4, 0, "You died at the table just like the ghost before you.");
            refresh();
            usleep(4000000);
            endwin();
            printf("\nGame Over: You died playing Russian Roulette.\n");
            exit(1);
        } else {
            mvprintw(2, 0, "*click*... You're still alive.");
            mvprintw(4, 0, "The ghost cackles, 'Lucky mortal...'");
            refresh();
            usleep(2000000);
    
            int reward = rand() % 4;
            switch (reward) {
                case 0:
                    mvprintw(6, 0, "You feel unstoppable! +100 Max HP!");
                    player.maxHP += 100;
                    break;
                case 1:
                    mvprintw(6, 0, "You feel untouchable! +35 Dodge!");
                    player.dodge += 35;
                    break;
                case 2:
                    mvprintw(6, 0, "You feel impenetrable! +35 Defense!");
                    player.defense += 35;
                    break;
                case 3:
                    mvprintw(6, 0, "Your muscles suddenly bulge up! Damage significantly increases!");
                    player.damage.base += 5;
                    player.damage.dice += 2;
                    player.damage.sides += 3;
                    break;
            }
        }
    
        mvprintw(8, 0, "Current HP: %d / %d", player.hp, player.maxHP);
        mvprintw(9, 0, "Defense: %d   Dodge: %d", player.defense, player.dodge);
        mvprintw(10, 0, "Damage: %d + %dd%d", player.damage.base, player.damage.dice, player.damage.sides);
        mvprintw(12, 0, "Press any key to return...");
        getch();
    }
    
    static void playWheelOfMisfortune(PC& player) {
        std::vector<std::string> outcomes = {
            "Full Heal",
            "+10 Dodge & Defense",
            "+1 Damage Base/Dice/Sides",
            "+30 Max HP",
            "NOTHING",
            "Extended Dungeon Warranty",
            "-20 Max HP",
            "-10 Dodge & Defense"
        };
    
        int selected = rand() % outcomes.size();
    
        int totalSpins = 40 + (rand() % 10);  
        for (int i = 0; i < totalSpins; i++) {
            clear();
            mvprintw(0, 0, "O [Wheel of Misfortune] O");
            mvprintw(2, 0, "Spinning...");
            for (int j = 0; j < outcomes.size(); j++) {
                int y = 4 + j;
                if (j == i % outcomes.size()) {
                    attron(A_BOLD | A_REVERSE);
                    mvprintw(y, 4, "> %s <", outcomes[j].c_str());
                    attroff(A_BOLD | A_REVERSE);
                } else {
                    mvprintw(y, 6, "  %s", outcomes[j].c_str());
                }
            }
            refresh();
        
            int delay = 80000 + (i * i * 90);  
            usleep(std::min(delay, 800000)); 
        }
    
        clear();
        mvprintw(0, 0, "Final Result: %s", outcomes[selected].c_str());
    
        switch (selected) {
            case 0:  
                player.hp = player.maxHP;
                mvprintw(2, 0, "You feel fully restored! Your HP has been filled!");
                break;
            case 1:  
                player.dodge += 10;
                player.defense += 10;
                mvprintw(2, 0, "Your body feels shielded! +10 dodge and defense!");
                break;
            case 2:  
                player.damage.base += 1;
                player.damage.dice += 1;
                player.damage.sides += 1;
                mvprintw(2, 0, "Your power surges! Your damage increases exponentially!");
                break;
            case 3:  
                player.maxHP += 30;
                mvprintw(2, 0, "You feel more resilient! +30 maxHP!");
                break;
            case 4:  
                mvprintw(2, 0, "Nothing happened...awkward");
                break;
            case 5: {
                const std::vector<std::string> sullySpeech = {
                    "Ahh... hello again, valued wheel spinner.",
                    "I'm Sully the Sloth, assistant vice liaison of the Casino Terms & Conditions Compliance Committee.",
                    "",
                    "By participating in this spin, you have voluntarily entered into a binding magical contract,",
                    "governed under subsection 42B of the Infernal Game Clause Codex,",
                    "ratified in the Year of the Weeping Basilisk.",
                    "",
                    "This agreement entitles you to absolutely no refunds,",
                    "no complaints, no exchanges, and most importantly, no sympathy.",
                    "",
                    "Now, onto the Wheel Usage Waiver Form Section V:",
                    "By spinning, you agree that the wheel may produce joy, dread, or mild itching,",
                    "and waive all rights to emotional stability for the next 24 dungeon hours.",
                    "",
                    "If you experience regret lasting longer than 4 hours, please consult a necromancer.",
                    "",
                    "Clause 19 states: Should Sully the Sloth begin speaking,",
                    "you are required by magical law to listen to the entire statement,",
                    "even if it causes boredom, existential reflection, or spontaneous hair growth.",
                    "",
                    "Now, regarding wheel liability insurance premiums — ",
                    "you're currently enrolled in the 'We're Not Responsible for Anything' tier.",
                    "Upgrades to the 'Still Not Our Fault' plan are available at checkout.",
                    "",
                    "In conclusion, always spin responsibly,",
                    "never question the ghost dealer, and remember:",
                    "if you think you're hearing voices… you probably are.",
                    "",
                    "Thank you for attending this mandatory lecture.",
                    "Sully out."
                    };
                
                    clear();
                    for (const auto& line : sullySpeech) {
                        mvprintw(0, 0, "Sully the Sloth says:");
                        mvprintw(2, 0, line.c_str());
                        refresh();
                        usleep(3000000);  
                        clear();
                    }
                
                    mvprintw(0, 0, "You may now return to your misery.");
                    mvprintw(2, 0, "Press any key to leave Sully alone...");
                    getch();
                    break;
                }
            case 6:  
                player.maxHP = std::max(10, player.maxHP - 20);
                if (player.hp > player.maxHP) player.hp = player.maxHP;
                mvprintw(2, 0, "Your vitality is drained! -20 maxHP!");
                break;
            case 7:  
                player.dodge = std::max(0, player.dodge - 10);
                player.defense = std::max(0, player.defense - 10);
                mvprintw(2, 0, "You feel sluggish and exposed! -10 dodge and defense!");
                break;
        }
    
        mvprintw(4, 0, "Current HP: %d / %d", player.hp, player.maxHP);
        mvprintw(5, 0, "Damage: %d + %dd%d", player.damage.base, player.damage.dice, player.damage.sides);
        mvprintw(6, 0, "Dodge: %d   Defense: %d", player.dodge, player.defense);
        mvprintw(8, 0, "Press any key to return...");
        getch();
    }
    

    static void playSlotMachine(PC& player) {
        clear();
        const std::vector<std::string> symbols = {"@", "$", "#", "&", "!"};
    
        mvprintw(0, 0, "Spinning...");
        refresh();
        usleep(600000);
    
        int s1, s2, s3;
    
        for (int i = 0; i < 10; ++i) {
            int temp1 = rand() % symbols.size();
            mvprintw(2, 0, "[ %s ]", symbols[temp1].c_str());
            refresh();
            usleep(100000 + i * 15000);
        }
        s1 = rand() % symbols.size();
        mvprintw(2, 0, "[ %s ]", symbols[s1].c_str());
    
        for (int i = 0; i < 10; ++i) {
            int temp2 = rand() % symbols.size();
            mvprintw(2, 6, "[ %s ]", symbols[temp2].c_str());
            refresh();
            usleep(100000 + i * 15000);
        }
        s2 = rand() % symbols.size();
        mvprintw(2, 6, "[ %s ]", symbols[s2].c_str());
    
        for (int i = 0; i < 10; ++i) {
            int temp3 = rand() % symbols.size();
            mvprintw(2, 12, "[ %s ]", symbols[temp3].c_str());
            refresh();
            usleep(100000 + i * 15000);
        }
        s3 = rand() % symbols.size();
        mvprintw(2, 12, "[ %s ]", symbols[s3].c_str());
    
        refresh();
        usleep(800000);
    
        mvprintw(4, 0, "Final Result:");
        mvprintw(5, 0, "[ %s ]", symbols[s1].c_str());
        refresh();
        usleep(700000);
        mvprintw(5, 6, "[ %s ]", symbols[s2].c_str());
        refresh();
        usleep(700000);
        mvprintw(5, 12, "[ %s ]", symbols[s3].c_str());
    
        if (s1 == s2 && s2 == s3) {
            mvprintw(7, 0, "JACKPOT! +50 HP!");
            player.maxHP += 50 ;
            player.hp += 50 ;
        } else if (s1 == s2 || s2 == s3 || s1 == s3) {
            mvprintw(7, 0, "Nice! +25 HP!");
            player.maxHP += 25 ;
            player.hp += 25 ;
        } else {
            mvprintw(7, 0, "No match. -20 HP!");
            player.hp -= 20;
            player.maxHP -= 20 ;
        }
    
        if (player.hp <= 0 || player.maxHP <= 0) {
            clear();
            mvprintw(0, 0, "You collapse from your own greed...");
            mvprintw(2, 0, "The ghost attendant takes your body towards soul collection.");
            mvprintw(4, 0, "You have died spinning the wheel of temptation.");
            refresh();
            usleep(4000000);
            endwin();
            printf("\nGAME OVER: You died from greed in the casino.\n");
            exit(1);
        }
        

        mvprintw(9, 0, "Current HP: %d", player.hp);
        mvprintw(10, 0, "Current Max HP: %d", player.maxHP);
        mvprintw(12, 0, "Press any key to return...");
        getch();
    }
};
