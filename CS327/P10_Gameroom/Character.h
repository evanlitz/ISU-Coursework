#pragma once
#include "Dice.h"

class Character {
public:
    int x, y;
    int speed;
    char symbol;
    bool alive;
    int hp ;
    int maxHP ;
    int defense = 1;
    int dodge = 5;
    int hit = 5 ;
    Dice damage ;

    int lastRegenTurn ;

    Character(int x = 0, int y = 0, int speed = 10, char symbol = '?', int startingHP = 100)
    : x(x), y(y), speed(speed), symbol(symbol), alive(true), hp(startingHP), maxHP(startingHP), lastRegenTurn(0) {}

    virtual ~Character() = default;

    virtual void move() = 0; 

    void updateHP(int currentTurn)
    {
        if (currentTurn <= lastRegenTurn) return;
    
        int turnsPassed = currentTurn - lastRegenTurn;
    
        for (int i = 0; i < turnsPassed; i++) {
            int regenPercent = (rand() % 10) + 1;
            int regenAmount = (regenPercent * maxHP) / 100;
            hp += regenAmount ;
        }
    
        if (hp > maxHP) {
            hp = maxHP ;
        }
    
        lastRegenTurn = currentTurn;
    }

    int getMaxHP() const {
        return maxHP ;
    }
};
