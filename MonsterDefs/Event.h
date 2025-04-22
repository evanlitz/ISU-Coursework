#pragma once

class Event {
public:
    int turnTime;
    bool isPC;
    int index;

    Event(int time = 0, bool pc = false, int idx = -1)
        : turnTime(time), isPC(pc), index(idx) {}
};
