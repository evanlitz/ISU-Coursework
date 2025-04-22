#pragma once
#include "Character.h"
#include "Dice.h"

class Monster : public Character {
public:
    int type;
    bool tunnel;
    int lastSeenX, lastSeenY;
    int hp;
    int color ;
    Dice damage ;

    Monster(int x = 0, int y = 0, int speed = 10, int type = 0, int hp = 0, Dice damage = Dice(), int color = 0)
        : Character(x, y, speed, '?'), type(type), tunnel((type & 0x4) != 0),
          lastSeenX(-1), lastSeenY(-1), hp(hp), damage(damage), color(color) {
        alive = true;
    }

    Monster(int x, int y, char symbol, int type, int speed, bool tunnel, int hp, Dice damage, int color)
        : Character(x, y, speed, symbol), type(type), tunnel(tunnel),
          lastSeenX(-1), lastSeenY(-1), hp(hp), damage(damage), color(color) {
        alive = true;
    }

    void move() override {

    }
};
