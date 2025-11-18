#pragma once
#include <string>
#include <cctype>

constexpr int WIDTH = 80;
constexpr int HEIGHT = 21;
constexpr int MAX_ROOMS = 10;
constexpr int MIN_ROOMS = 5;
constexpr int MAX_ROOM_X_SIZE = 14;
constexpr int MIN_ROOM_X_SIZE = 4;
constexpr int MAX_ROOM_Y_SIZE = 10;
constexpr int MIN_ROOM_Y_SIZE = 3;
constexpr int MAX_UP = 3;
constexpr int MAX_DOWN = 3;
constexpr int MAX_TURNS = 10000;

inline std::string trim(const std::string& str) {
    const size_t first = str.find_first_not_of(" \t\r");
    const size_t last = str.find_last_not_of(" \t\r");
    return (first == std::string::npos) ? "" : str.substr(first, last - first + 1);
}
