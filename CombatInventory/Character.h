#pragma once
#include "Dice.h"

class Character {
public:
    int x, y;
    int speed;
    char symbol;
    bool alive;
    int hp ;
    Dice damage ;

    Character(int x = 0, int y = 0, int speed = 10, char symbol = '?')
        : x(x), y(y), speed(speed), symbol(symbol), alive(true) {}

    virtual ~Character() = default;

    virtual void move() = 0; 
};
