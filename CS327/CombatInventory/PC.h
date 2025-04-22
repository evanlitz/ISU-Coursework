#pragma once
#include "Character.h"
#include "Constants.h"
#include "Object.h"
#include <ncurses.h>

class PC : public Character {
public:
    char pcLastTile;

    char rememberedDungeon[HEIGHT][WIDTH] ;

    Object* inventory[10] = {nullptr};
    Object* equipment[12] = {nullptr};

    enum EquipmentSlot {
        WEAPON, OFFHAND, RANGED, ARMOR, HELMET, CLOAK, GLOVES, BOOTS, AMULET, LIGHT, RING1, RING2
    };


    void listInventory() const {
        for (int i = 0 ; i < 10 ; i++)
        {
            if (inventory[i])
            {
                mvprintw(i + 1, 0, "%d: %s", i, inventory[i]->name.c_str());
            }
        }
    }
    void listEquipment() const {
        const char* labels[] = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"};
        for (int i = 0; i < 12; i++)
        {
            if (equipment[i])
            {
                mvprintw(i + 1, 40, "%s: %s", labels[i], equipment[i]->name.c_str());
            }
        }
    }

    bool wearItem(int invIndex) {
        if (invIndex < 0 || invIndex >= 10 || inventory[invIndex] == nullptr) return false;

        Object* obj = inventory[invIndex];
        int slot = getEquipmentIndexForType(obj->type);
        if (slot == -1) return false;
    
        if (equipment[slot]) {
            inventory[invIndex] = equipment[slot];
        } else {
            inventory[invIndex] = nullptr;
        }
    
        equipment[slot] = obj;
        return true;
    }

    bool takeOffItem(int equipIndex) {
        if (equipIndex < 0 || equipIndex >= 12 || equipment[equipIndex] == nullptr)
        {
            return false ;
        }
        int invSlot = getFirstEmptyInventorySlot() ;
        if (invSlot == -1)
        {
            return false ;
        }

        inventory[invSlot] = equipment[equipIndex];
        equipment[equipIndex] = nullptr;
        return true;
    }

    bool dropItem(int invIndex, std::vector<Object>& dungeonObjects)
    {
        if (invIndex < 0 || invIndex >= 10 || inventory[invIndex] == nullptr)
        {
            return false ;
        }

        Object* obj = inventory[invIndex];
        obj->x = x;
        obj->y = y;
        dungeonObjects.push_back(*obj);  
        delete obj;
        inventory[invIndex] = nullptr;
        return true;
    }

    bool expungeItem(int invIndex) {
        if (invIndex < 0 || invIndex >= 10 || inventory[invIndex] == nullptr)
        {
            return false ;
        }
        delete inventory[invIndex] ;
        inventory[invIndex] = nullptr ;
        return true ;
    }

    int getEquipmentIndexForType(const std::string& type) 
    {
        if (type == "WEAPON") return WEAPON;
        if (type == "OFFHAND") return OFFHAND;
        if (type == "RANGED") return RANGED;
        if (type == "ARMOR") return ARMOR;
        if (type == "HELMET") return HELMET;
        if (type == "CLOAK") return CLOAK;
        if (type == "GLOVES") return GLOVES;
        if (type == "BOOTS") return BOOTS;
        if (type == "AMULET") return AMULET;
        if (type == "LIGHT") return LIGHT;
        if (type == "RING") {
            if (equipment[RING1] == nullptr) return RING1;
            return RING2;
        }
        return -1;
    }

    int getFirstEmptyInventorySlot() const {
        for (int i = 0; i < 10; i++)
        {
            if (inventory[i] == nullptr) 
            {
                return i ;
            }
        }
        return -1 ;
    }

    bool addToInventory(Object* item) {
        int slot = getFirstEmptyInventorySlot();
        if (slot == -1) {
            return false ;
        }
        inventory[slot] = item ;
        return true ;
    }

    int getModifiedSpeed() const {
        int total = speed ;
        for (int i = 0 ; i < 12 ; i++)
        {
            if (equipment[i])
            {
                total += equipment[i]->speed;
            }
        }
        return total ;
    }

    Dice getModifiedDamage() const {
        Dice total = damage ;
        for (int i = 0 ; i < 12 ; i++)
        {
            if (equipment[i])
            {
                total.base += equipment[i]->damage.base;
                total.dice += equipment[i]->damage.dice;
                total.sides += equipment[i]->damage.sides;
            }
        }
        return total;
    }   


    PC(int x = 0, int y = 0, int speed = 10)
        : Character(x, y, speed, '@') {
        hp = 50;
        damage = Dice{0, 1, 4};
        pcLastTile = '.';
    }

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
