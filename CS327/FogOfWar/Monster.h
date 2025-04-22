#pragma once
#include "Character.h"

class Monster : public Character {
public:
    int type;
    bool tunnel;
    int lastSeenX, lastSeenY;

    Monster(int x = 0, int y = 0, int speed = 10, int type = 0)
        : Character(x, y, speed, '?'), type(type), tunnel((type & 0x4) != 0),
          lastSeenX(-1), lastSeenY(-1) {
        alive = true;
    }

    Monster(int x, int y, char symbol, int type, int speed, bool tunnel)
        : Character(x, y, speed, symbol), type(type), tunnel(tunnel),
          lastSeenX(-1), lastSeenY(-1) {
        alive = true;
    }

    void move() override {

    }
};
