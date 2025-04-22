#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <curses.h>
#include "Dice.h"
#include "Object.h"

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

    Object createInstance() const {
        Object obj;
    
        obj.name = this->name;
        obj.type = this->type;
        obj.description = this->description;
    
        obj.color = parseColor(this->color); 
    
        obj.weight = this->weight.base + (rand() % this->weight.sides + 1) * this->weight.dice;
        obj.hit    = this->hit.base    + (rand() % this->hit.sides + 1) * this->hit.dice;
        obj.damage = this->damage; 
        obj.dodge  = this->dodge.base  + (rand() % this->dodge.sides + 1) * this->dodge.dice;
        obj.defense= this->defense.base+ (rand() % this->defense.sides + 1) * this->defense.dice;
        obj.speed  = this->speed.base  + (rand() % this->speed.sides + 1) * this->speed.dice;
        obj.attr   = this->attr.base   + (rand() % this->attr.sides + 1) * this->attr.dice;
        obj.value  = this->value.base  + (rand() % this->value.sides + 1) * this->value.dice;
    
        obj.artifact = this->artifact;
        obj.x = -1;
        obj.y = -1;
    
        return obj;
    }

private:
    static int parseColor(const std::string& colorStr)
    {
        if (colorStr == "RED") return COLOR_RED;
        if (colorStr == "GREEN") return COLOR_GREEN;
        if (colorStr == "BLUE") return COLOR_BLUE;
        if (colorStr == "CYAN") return COLOR_CYAN;
        if (colorStr == "YELLOW") return COLOR_YELLOW;
        if (colorStr == "MAGENTA") return COLOR_MAGENTA;
        if (colorStr == "WHITE") return COLOR_WHITE ;
        return COLOR_WHITE;
    }
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
