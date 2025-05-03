#pragma once

#include <string>
#include <cstdio>  

class Dice 
{
public:
    int base;
    int dice;
    int sides;

    Dice() 
    {
        base = 0;
        dice = 0;
        sides = 0;
    }

    Dice(int base, int dice, int sides)
        : base(base), dice(dice), sides(sides) {}

    static bool parse(std::string input, Dice &outDice) 
    {
        int b, d, s;
        if (sscanf(input.c_str(), "%d+%dd%d", &b, &d, &s) == 3) 
        {
            outDice.base = b;
            outDice.dice = d;
            outDice.sides = s;
            return true;
        }
        return false;
    }
};
