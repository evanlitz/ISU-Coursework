#pragma once
#include "Character.h"
#include "Constants.h"

class PC : public Character {
public:
    char pcLastTile;

    char rememberedDungeon[HEIGHT][WIDTH] ;

    PC(int x = 0, int y = 0, int speed = 10)
        : Character(x, y, speed, '@'), pcLastTile('.') {}

    void move() override {

    }

    void updatePosition(int newX, int newY, char newTile) {
        x = newX;
        y = newY;
        pcLastTile = newTile;
    }

    void resetMemory()
    {
        for (int y = 0 ; y < HEIGHT ; y++)
        {
            for (int x = 0 ; x < WIDTH ; x++)
            {   
                rememberedDungeon[y][x] = ' ' ;
            }
        }
    }

};
