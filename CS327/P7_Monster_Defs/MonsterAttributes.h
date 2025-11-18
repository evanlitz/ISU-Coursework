#pragma once

#include <string>
#include <vector>
#include <iostream>
#include "Dice.h"

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
};