#pragma once
#include "Event.h"

class PriorityQueue {
public:
    static const int MAX_SIZE = 10000;
    Event events[MAX_SIZE];
    int size = 0;

    void push(const Event& event);
    Event pop();
    bool isEmpty() const { return size == 0; }

    void clear() { size = 0; }

private:
    void swap(Event &a, Event &b);
};
