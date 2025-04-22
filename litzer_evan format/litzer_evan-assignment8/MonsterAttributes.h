#pragma once

#include <string>
#include <vector>
#include <iostream>
#include "Dice.h"
#include "Monster.h"
#include <curses.h>


class MonsterAttributes {
public:
    std::string name;
    std::string description;
    char symbol;
    std::vector<std::string> colors;
    Dice speed;
    std::vector<std::string> abilities;
    Dice hp;
    Dice damage;
    int rarity;

    bool isComplete = false; 

    void print() 
    {
        std::cout << name << std::endl;
        std::cout << description << std::endl;
        std::cout << symbol << std::endl;

        for (int i = 0; i < colors.size(); i++) 
        {
            std::cout << colors[i];
            if (i < colors.size() - 1) std::cout << " ";
        }
        std::cout << std::endl;

        std::cout << speed.base << "+" << speed.dice << "d" << speed.sides << std::endl;

        for (int i = 0; i < abilities.size(); i++) 
        {
            std::cout << abilities[i];
            if (i < abilities.size() - 1) std::cout << " ";
        }
        std::cout << std::endl;

        std::cout << hp.base << "+" << hp.dice << "d" << hp.sides << std::endl;
        std::cout << damage.base << "+" << damage.dice << "d" << damage.sides << std::endl;

        std::cout << rarity << std::endl << std::endl;
    }

    Monster createInstance(int x, int y) const 
    {
        int rolledSpeed = speed.base + (rand() % speed.sides + 1) * speed.dice;
        int rolledHP = hp.base + (rand() % hp.sides + 1) * hp.dice ;
        int type = loadMonsterType();
        bool tunnel = (type & 0x4) ;

        int ncursesColor = COLOR_WHITE  ;
        if (!colors.empty())
        {
            std::string c = colors[0];
            if (c == "RED") {
                ncursesColor = COLOR_RED ;
            }
            else if (c == "GREEN") {
                 ncursesColor = COLOR_GREEN;
            }
            else if (c == "YELLOW") { 
                ncursesColor = COLOR_YELLOW;
            }
            else if (c == "BLUE") { 
                ncursesColor = COLOR_BLUE;
            }
            else if (c == "CYAN") {
                ncursesColor = COLOR_CYAN;
            }
            else if (c == "MAGENTA") { 
                ncursesColor = COLOR_MAGENTA;
            }
            else if (c == "WHITE") {
                ncursesColor = COLOR_WHITE;
            }
            else if (c == "BLACK") { 
                ncursesColor = COLOR_WHITE;  
            }
        }
        return Monster(x, y, symbol, type, rolledSpeed, tunnel, rolledHP, damage, ncursesColor);
    }
    
    int loadMonsterType() const ;
};



inline int MonsterAttributes::loadMonsterType() const
{
    int mask = 0 ;
    for (int i = 0 ; i < abilities.size(); i++)
    {
        std::string ab = abilities[i];

        if (ab == "SMART")
        {
            mask = mask | 1;
        }
        if (ab == "TELE") 
        {
            mask = mask | 2 ;
        }
        if (ab == "TUNNEL")
        {
            mask = mask | 4;
        }
        if (ab == "ERRATIC")
        {
            mask = mask | 8 ;
        }
    }

    return mask ;
}
