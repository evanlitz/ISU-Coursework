#pragma once

class Point {
public:
    int x, y;
    int distance;

    Point(int x = 0, int y = 0, int distance = 0)
        : x(x), y(y), distance(distance) {}

    bool operator<(const Point &other) const {
        return distance > other.distance; 
    }
};
