#pragma once

#include <string>
#include <vector>
#include <iostream>
#include "Dice.h"

class ItemAttributes 
{
public:  
    std::string name;
    std::string type;
    std::string description;
    std::string color;

    Dice weight, hit, damage, dodge, defense, speed, attr, value;
    int rarity = 0;
    bool artifact = false;
    bool isComplete = false;

    void print() const;
};

inline void ItemAttributes::print() const 
{
    std::cout << name << "\n"
              << description << "\n"
              << type << "\n"
              << color << "\n"
              << weight.base << "+" << weight.dice << "d" << weight.sides << "\n"
              << hit.base << "+" << hit.dice << "d" << hit.sides << "\n"
              << damage.base << "+" << damage.dice << "d" << damage.sides << "\n"
              << dodge.base << "+" << dodge.dice << "d" << dodge.sides << "\n"
              << defense.base << "+" << defense.dice << "d" << defense.sides << "\n"
              << speed.base << "+" << speed.dice << "d" << speed.sides << "\n"
              << attr.base << "+" << attr.dice << "d" << attr.sides << "\n"
              << value.base << "+" << value.dice << "d" << value.sides << "\n"
              << rarity << "\n"
              << (artifact ? "TRUE" : "FALSE") << "\n\n";
}
