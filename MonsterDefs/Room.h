#pragma once

class Room {
public:
    int x, y;
    int width, height;

    Room(int x = 0, int y = 0, int w = 0, int h = 0)
        : x(x), y(y), width(w), height(h) {}

    void getCenter(int &cx, int &cy) const {
        cx = x + width / 2;
        cy = y + height / 2;
    }

    bool contains(int px, int py) const {
        return px >= x && px < x + width && py >= y && py < y + height;
    }
};
