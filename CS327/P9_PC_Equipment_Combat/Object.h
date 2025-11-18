#pragma once

#include <string>
#include "Dice.h"

class Object 
{
public:
    std::string name ;
    std::string type ;
    std::string description ;
    int color ;
    int weight ;
    int hit ;
    Dice damage;
    int dodge ;
    int defense ;
    int speed ;
    int attr ;
    int value ;
    bool artifact ;
    int x ;
    int y ;

    Object(
        const std::string& name = "",
        const std::string& type = "",
        const std::string& description = "",
        int color = 0,
        int weight = 0,
        int hit = 0,
        Dice damage = Dice(),
        int dodge = 0,
        int defense = 0,
        int speed = 0,
        int attr = 0,
        int value = 0,
        bool artifact = false,
        int x = -1,
        int y = -1
    ) :
    name(name), type(type), description(description), color(color), weight(weight),
    hit(hit), damage(damage), dodge(dodge), defense(defense), speed(speed), attr(attr),
    value(value), artifact(artifact), x(x), y(y) {}
};