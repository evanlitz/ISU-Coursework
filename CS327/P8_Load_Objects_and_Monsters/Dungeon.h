#pragma once

#include <vector>
#include "Room.h"
#include "UpStaircase.h"
#include "DownStaircase.h"
#include "Monster.h"
#include "PC.h"
#include "PriorityQueue.h"
#include "Event.h"
#include "Constants.h"
#include "Object.h"
#include <unordered_set>
#include <cstdint>
#include "ItemAttributes.h"
#include "MonsterAttributes.h"



class Dungeon {
public:

    bool fogToggle = true ;
    bool teleportMode = false ;
    bool forceFullRender = false;
    int teleportX = 0 ;
    int teleportY = 0 ;

    static const int MAX_STAIRCASE_DOWN = 5 ;
    static const int MAX_STAIRCASE_UP = 5 ;
    static const int NUM_MONSTERS = 15 ;

    std::vector<ItemAttributes> itemTemplates ;
    std::unordered_set<std::string> usedArtifacts ;

    std::vector<MonsterAttributes> monsterTemplates;
    std::unordered_set<std::string> usedUniques;

    std::vector<Monster> monsters;
    int numMonsters;

    std::vector<Object> objects;
    int numObjects ;



    Dungeon();

    void generate(int numMonsters);              
    void render();                
    void runGameLoop(int argc, char* argv[]);           
    void movePlayer(int dx, int dy);
    void printMonsters();         
    void saveDungeon();                  
    void loadDungeon();
    bool isMonsterSymbol(char c);
    bool isWalkable(int x, int y);
    void moveStraightLine(Monster &monster, int targetX, int targetY, int &newX, int &newY);
    void regenerateDungeon(int currentTurnTime);
    bool handlePlayerInput(int input, int currentTurnTime);
    bool checkVictory();   
    bool isInRoom(int x, int y);
    void updateVisibility();
    void handleTeleportInput() ;
               

private:
    char dungeonMap[HEIGHT][WIDTH];
    int hardness[HEIGHT][WIDTH];

    Room rooms[MAX_ROOMS];
    int numRooms;

    UpStaircase upStaircases[MAX_UP];
    int numUpStairs;

    DownStaircase downStaircases[MAX_DOWN];
    int numDownStairs;

    PC player;
    char pcLastTile;

    int distanceMapNonTunnel[HEIGHT][WIDTH];
    int distanceMapTunnel[HEIGHT][WIDTH];
    
    PriorityQueue pq;

    void generateHardness();
    int createRooms();
    void calculatePath();
    int createUpStaircases();
    int createDownStaircases();
    void generatePlayerPosition();
    void createMonsters(int numMonsters);
    void generateObjects();

    void generatePath(int x1, int y1, int x2, int y2);
    double pathDistanceCalc(int x1, int y1, int x2, int y2);
    void calculateDistanceMap(int distanceMap[HEIGHT][WIDTH], int playerX, int playerY, bool tunnelMonster);
    void getIntelligentPosition(int x, int y, int playerX, int playerY, int &nextX, int &nextY, bool tunnel);
    char getSymbolForObjectType(const std::string& type);

    void moveMonster(Monster &monster);

    void ensureDirectoryExists(const char *path);
    void loadFromFile(const char *path);
    void saveToFile(const char *path);
};
