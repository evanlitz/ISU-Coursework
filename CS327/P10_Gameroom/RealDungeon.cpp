#ifdef _WIN32
    #include <windows.h>
    #define usleep(x) Sleep((x) / 1000)
#else
    #include <unistd.h>
#endif

#include "Dungeon.h"
#include "Room.h"
#include "UpStaircase.h"
#include "DownStaircase.h"
#include "Point.h"
#include "Monster.h"
#include "Event.h"
#include "PriorityQueue.h"
#include "PC.h"
#include "Casino.h"

#include <cstdlib>
#include <ctime>
#include <cstring>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <sys/stat.h>
#include <ncurses.h>
#include <cerrno>
#include <algorithm>
#include <sstream>


#define FILE_MARKER "RLG327-S2025"
#define DUNGEON_PATH "/.rlg327/dungeon"

Dungeon::Dungeon() {
    srand(time(NULL));
    // showFog = true;
}

void Dungeon::generate(int numMonsters) {
    this->numMonsters = numMonsters ;
    generateHardness();
    numRooms = createRooms();
    numUpStairs = createUpStaircases();
    numDownStairs = createDownStaircases();
    calculatePath();
    generatePlayerPosition();
    generateObjects() ;
    createMonsters(numMonsters);
    placeCasino();
    player.resetMemory();
    updateVisibility();
    // player.updateTerrainMemory(dungeonMap);
}

void Dungeon::generateHardness() {
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            if (y == 0 || y == HEIGHT - 1 || x == 0 || x == WIDTH - 1) {
                hardness[y][x] = 255;
                dungeonMap[y][x] = ' ';
            } else {
                hardness[y][x] = (rand() % 254) + 1;
                dungeonMap[y][x] = ' ';
            }
        }
    }
}

int Dungeon::createRooms() {
    numRooms = (rand() % (MAX_ROOMS - MIN_ROOMS + 1)) + MIN_ROOMS;
    int attempts = 1;

    for (int i = 0; i < numRooms; i++) {
        bool placed = false;

        while (!placed) {
            attempts++;

            int roomWidth  = (rand() % (MAX_ROOM_X_SIZE - MIN_ROOM_X_SIZE + 1)) + MIN_ROOM_X_SIZE;
            int roomHeight = (rand() % (MAX_ROOM_Y_SIZE - MIN_ROOM_Y_SIZE + 1)) + MIN_ROOM_Y_SIZE;
            int roomX = rand() % (WIDTH - roomWidth - 2) + 1;
            int roomY = rand() % (HEIGHT - roomHeight - 2) + 1;

            bool validPlacement = true;

            for (int y = roomY - 1; y <= roomY + roomHeight; y++) {
                for (int x = roomX - 1; x <= roomX + roomWidth; x++) {
                    if (x <= 0 || x >= WIDTH - 1 || y <= 0 || y >= HEIGHT - 1) {
                        validPlacement = false;
                        break;
                    }
                    if (dungeonMap[y][x] == '.') {
                        validPlacement = false;
                        break;
                    }
                }
                if (!validPlacement) break;
            }

            if (!validPlacement) continue;

            rooms[i] = Room(roomX, roomY, roomWidth, roomHeight);

            for (int y = roomY; y < roomY + roomHeight; y++) {
                for (int x = roomX; x < roomX + roomWidth; x++) {
                    dungeonMap[y][x] = '.';
                    hardness[y][x] = 0;
                }
            }

            placed = true;
        }
    }

    return numRooms;
}

void Dungeon::generatePlayerPosition() {
    int randomRoom = rand() % numRooms;

    while (rooms[randomRoom].width <= 0 || rooms[randomRoom].height == 0) {
        randomRoom = rand() % numRooms;
    }

    int px = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
    int py = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);

    pcLastTile = dungeonMap[py][px];
    player.updatePosition(px, py, pcLastTile);
}

void Dungeon::updateVisibility()
{
    int playerX = player.x ;
    int playerY = player.y ;

    for (int ry = -3; ry <= 3; ry++)
    {
        for(int rx = -3 ; rx <= 3 ; rx++)
        {
            int x = rx + playerX ;
            int y = ry + playerY ;

            if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT)
            {
                player.rememberedDungeon[y][x] = dungeonMap[y][x] ;
            }
        }
    }
}

void Dungeon::generateObjects()
{
    objects.clear() ;
    int placed = 0 ;

    while (placed < numObjects) 
    {
        if (itemTemplates.empty()) break ;

        int index = rand() % itemTemplates.size();
        const ItemAttributes& desc = itemTemplates[index];
        
        if (desc.artifact && usedArtifacts.count(desc.name)) continue ;

        if ((rand() % 100) >= desc.rarity) continue ;

        Object obj = desc.createInstance();

        int x, y, attempts = 0;
        do 
        {
            x = rand() % WIDTH ;
            y = rand() % HEIGHT ;
            attempts++ ;
        }
        while ((dungeonMap[y][x] != '.') && attempts < 100) ;

        if (dungeonMap[y][x] != '.') continue ;

        obj.x = x ;
        obj.y = y ;

        objects.push_back(obj) ;
        placed++ ;

        if (desc.artifact)
        {
            usedArtifacts.insert(desc.name);
        }
    }
}

void Dungeon::generatePath(int room1X, int room1Y, int room3X, int room3Y) {
    int x = room1X;
    int y = room1Y;

    while (x != room3X || y != room3Y) {
        if (x <= 0 || x >= WIDTH - 1 || y <= 0 || y >= HEIGHT - 1)
            break;

        if (dungeonMap[y][x] == ' ') {
            dungeonMap[y][x] = '#';
            hardness[y][x] = 0;
        }

        if (rand() % 2 == 0) {
            x += (x < room3X) ? 1 : (x > room3X ? -1 : 0);
        } else {
            y += (y < room3Y) ? 1 : (y > room3Y ? -1 : 0);
        }
    }
}

void Dungeon::calculatePath() {
    std::vector<bool> isConnected(numRooms, false);
    isConnected[0] = true;

    for (int z = 1; z < numRooms; z++) {
        int nearestRoom = -1;
        double minDistance = 1e9;

        int room1X, room1Y;
        rooms[z].getCenter(room1X, room1Y);

        for (int a = 0; a < z; a++) {
            if (!isConnected[a]) continue;

            int room2X, room2Y;
            rooms[a].getCenter(room2X, room2Y);

            double distance = pathDistanceCalc(room1X, room1Y, room2X, room2Y);
            if (distance < minDistance) {
                minDistance = distance;
                nearestRoom = a;
            }
        }

        if (nearestRoom != -1) {
            int r1x, r1y, r2x, r2y;
            rooms[z].getCenter(r1x, r1y);
            rooms[nearestRoom].getCenter(r2x, r2y);

            r1x += (rand() % (rooms[z].width / 2 + 1)) * (rand() % 2 == 0 ? -1 : 1);
            r1y += (rand() % (rooms[z].height / 2 + 1)) * (rand() % 2 == 0 ? -1 : 1);
            r2x += (rand() % (rooms[nearestRoom].width / 2 + 1)) * (rand() % 2 == 0 ? -1 : 1);
            r2y += (rand() % (rooms[nearestRoom].height / 2 + 1)) * (rand() % 2 == 0 ? -1 : 1);

            r1x = std::clamp(r1x, rooms[z].x, rooms[z].x + rooms[z].width - 1);
            r1y = std::clamp(r1y, rooms[z].y, rooms[z].y + rooms[z].height - 1);
            r2x = std::clamp(r2x, rooms[nearestRoom].x, rooms[nearestRoom].x + rooms[nearestRoom].width - 1);
            r2y = std::clamp(r2y, rooms[nearestRoom].y, rooms[nearestRoom].y + rooms[nearestRoom].height - 1);

            generatePath(r1x, r1y, r2x, r2y);
            isConnected[z] = true;
        }
    }
}

void Dungeon::calculateDistanceMap(int distanceMap[HEIGHT][WIDTH], int playerX, int playerY, bool tunnelMonster) {
    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1};
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1};

    bool visited[HEIGHT][WIDTH] = { false };

    std::vector<Point> pq;

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            distanceMap[y][x] = 1000000;
            visited[y][x] = false;
        }
    }

    distanceMap[playerY][playerX] = 0;
    pq.push_back({playerX, playerY, 0});

    while (!pq.empty()) {
        int minIndex = 0;
        for (size_t i = 1; i < pq.size(); i++) {
            if (pq[i].distance < pq[minIndex].distance) {
                minIndex = i;
            }
        }

        Point curr = pq[minIndex];
        pq.erase(pq.begin() + minIndex);

        int x = curr.x;
        int y = curr.y;

        if (visited[y][x]) continue;
        visited[y][x] = true;

        for (int i = 0; i < 8; i++) {
            int checkX = x + movesX[i];
            int checkY = y + movesY[i];

            if (checkX >= 0 && checkX < WIDTH && checkY >= 0 && checkY < HEIGHT && !visited[checkY][checkX]) {
                int weight = 1;

                if (tunnelMonster) {
                    if (hardness[checkY][checkX] != 255) {
                        weight += hardness[checkY][checkX] / 85;
                    } else {
                        continue;
                    }
                } else {
                    if (dungeonMap[checkY][checkX] == ' ' || hardness[checkY][checkX] > 0) {
                        continue;
                    }
                }

                int checkDistance = distanceMap[y][x] + weight;
                if (checkDistance < distanceMap[checkY][checkX]) {
                    distanceMap[checkY][checkX] = checkDistance;
                    pq.push_back({checkX, checkY, checkDistance});
                }
            }
        }
    }
}


double Dungeon::pathDistanceCalc(int room1X, int room1Y, int room2X, int room2Y) {
    return (room2X - room1X) * (room2X - room1X) + (room2Y - room1Y) * (room2Y - room1Y);
}

int Dungeon::createUpStaircases() {
    int upstairTotal = (rand() % MAX_UP) + 1;
    int upstairsPlaced = 0;

    while (upstairsPlaced < upstairTotal) {
        int randomRoom = rand() % numRooms;

        int stairX = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
        int stairY = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);

        if (dungeonMap[stairY][stairX] == '.') {
            dungeonMap[stairY][stairX] = '<';
            hardness[stairY][stairX] = 0;

            upStaircases[upstairsPlaced] = UpStaircase(stairX, stairY);
            upstairsPlaced++;
        }
    }

    numUpStairs = upstairsPlaced;
    return numUpStairs ;
}

int Dungeon::createDownStaircases() {
    int downstairTotal = (rand() % MAX_DOWN) + 1;
    int downstairsPlaced = 0;

    while (downstairsPlaced < downstairTotal) {
        int randomRoom = rand() % numRooms;

        int stairX = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
        int stairY = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);

        if (dungeonMap[stairY][stairX] == '.') {
            dungeonMap[stairY][stairX] = '>';
            hardness[stairY][stairX] = 0;

            downStaircases[downstairsPlaced] = DownStaircase(stairX, stairY);
            downstairsPlaced++;
        }
    }

    numDownStairs = downstairsPlaced;
    return numDownStairs ;
}

void Dungeon::placeCasino() {
    int roomIndex = rand() % numRooms;
    int attempts = 10;

    while ((rooms[roomIndex].contains(player.x, player.y) || rooms[roomIndex].width <= 0)
           && attempts-- > 0) {
        roomIndex = rand() % numRooms;
    }

    int cx, cy;
    rooms[roomIndex].getCenter(cx, cy);

    dungeonMap[cy][cx] = '^';  

    hardness[cy][cx] = 0;

    
}


bool Dungeon::isMonsterSymbol(char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
}

bool Dungeon::isWalkable(int x, int y) {
    return x > 0 && x < WIDTH - 1 && y > 0 && y < HEIGHT - 1 &&
           hardness[y][x] < 255;
}

uint32_t to_big_endian_32(uint32_t val) {
    return ((val & 0xff) << 24) | ((val & 0xff00) << 8) |
           ((val & 0xff0000) >> 8) | ((val & 0xff000000) >> 24);
}

uint16_t to_big_endian_16(uint16_t val) {
    return ((val & 0xff) << 8) | ((val & 0xff00) >> 8);
}

void PriorityQueue::swap(Event &a, Event &b) {
    Event temp = a;
    a = b;
    b = temp;
}

void PriorityQueue::push(const Event& event) {
    int i = size++;
    events[i] = event;

    while (i > 0 && events[i].turnTime < events[(i - 1) / 2].turnTime) {
        swap(events[i], events[(i - 1) / 2]);
        i = (i - 1) / 2;
    }
}

Event PriorityQueue::pop() {
    Event top = events[0];
    events[0] = events[--size];

    int i = 0;

    while (2 * i + 1 < size) {
        int child = 2 * i + 1;
        if (child + 1 < size && events[child + 1].turnTime < events[child].turnTime) {
            child++;
        }
        if (events[i].turnTime <= events[child].turnTime) break;
        swap(events[i], events[child]);
        i = child;
    }

    return top;
}


bool Dungeon::isInRoom(int x, int y) {
    for (int i = 0; i < numRooms; i++) {
        if (rooms[i].contains(x, y)) return true;
    }
    return false;
}

void Dungeon::ensureDirectoryExists(const char *path) {
    struct stat st;
    memset(&st, 0, sizeof(st));
    if (stat(path, &st) == -1) {
        mkdir(path, 0777);
    }
}

void Dungeon::createMonsters(int numMonsters) {
    monsters.clear();  
    int placed = 0;

    while (placed < numMonsters) {
        if (monsterTemplates.empty()) break;

        int idx = rand() % monsterTemplates.size();
        const MonsterAttributes& desc = monsterTemplates[idx];

        if ((rand() % 100) >= desc.rarity) continue;

        if (desc.name.find("UNIQUE") != std::string::npos &&
            usedUniques.count(desc.name)) continue;

        int monsterX, monsterY, tries = 0;
        do {
            monsterY = rand() % (HEIGHT - 2) + 1;
            monsterX = rand() % (WIDTH - 2) + 1;
            tries++;
        } while (
            (dungeonMap[monsterY][monsterX] != '.' &&
            dungeonMap[monsterY][monsterX] != '#') ||
            (monsterX == player.x && monsterY == player.y) &&
            tries < 100
        );

        if (tries >= 100) continue;

        Monster m = desc.createInstance(monsterX, monsterY);
        monsters.push_back(m);
        dungeonMap[monsterY][monsterX] = m.symbol;

        placed++;
    }
}

void Dungeon::getIntelligentPosition(int x, int y, int playerX, int playerY, int &nextX, int &nextY, bool tunnel) {
    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1};
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1};

    int distanceMap[HEIGHT][WIDTH];
    calculateDistanceMap(distanceMap, playerX, playerY, tunnel);  

    int minDistance = distanceMap[y][x];
    nextX = x;
    nextY = y;

    for (int i = 0; i < 8; i++) {
        int checkX = x + movesX[i];
        int checkY = y + movesY[i];

        if (checkX > 0 && checkX < WIDTH && checkY > 0 && checkY < HEIGHT) {
            if (tunnel) {
                if (hardness[checkY][checkX] < 255 &&
                    distanceMap[checkY][checkX] < minDistance) {
                    minDistance = distanceMap[checkY][checkX];
                    nextX = checkX;
                    nextY = checkY;
                }
            } else {
                if ((dungeonMap[checkY][checkX] == '.' || dungeonMap[checkY][checkX] == '#') &&
                    distanceMap[checkY][checkX] < minDistance) {
                    minDistance = distanceMap[checkY][checkX];
                    nextX = checkX;
                    nextY = checkY;
                }
            }
        }
    }
}

char Dungeon::getSymbolForObjectType(const std::string& type)
{
    if (type == "WEAPON") return '|';
    if (type == "OFFHAND") return ')';
    if (type == "RANGED") return '}';
    if (type == "ARMOR") return '[';
    if (type == "HELMET") return ']';
    if (type == "CLOAK") return '(';
    if (type == "GLOVES") return '{';
    if (type == "BOOTS") return '\\';
    if (type == "RING") return '=';
    if (type == "AMULET") return '"';
    if (type == "LIGHT") return '_';
    if (type == "SCROLL") return '~';
    if (type == "BOOK") return '?';
    if (type == "FLASK") return '!';
    if (type == "GOLD") return '$';
    if (type == "AMMUNITION") return '/';
    if (type == "FOOD") return ',';
    if (type == "WAND") return '-';
    if (type == "CONTAINER") return '%';
    if (type == "STACK") return '&';
    return '*';
}

void Dungeon::moveStraightLine(Monster &monster, int targetX, int targetY, int &newX, int &newY) {
    int moveX = 0, moveY = 0;

    if (targetX > monster.x) moveX = 1;
    else if (targetX < monster.x) moveX = -1;

    if (targetY > monster.y) moveY = 1;
    else if (targetY < monster.y) moveY = -1;

    newX = monster.x;
    newY = monster.y;

    if (moveX != 0) {
        int tempX = monster.x + moveX;
        if (tempX >= 1 && tempX < WIDTH - 1) {
            newX = tempX;
            newY = monster.y;
        }
    }

    if (moveY != 0 && newX == monster.x) {
        int tempY = monster.y + moveY;
        if (tempY >= 1 && tempY < HEIGHT - 1) {
            newX = monster.x;
            newY = tempY;
        }
    }
}


void Dungeon::render() {
    clear();

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            move(y + 1, x);  

            char tileToRender;

            if (teleportMode || lookMode) {
                if (x == player.x && y == player.y) {
                    tileToRender = '@';
                } else {
                    tileToRender = dungeonMap[y][x];
                }
            }
            else if (!fogToggle || (abs(x - player.x) <= 3 && abs(y - player.y) <= 3)) {
                if (x == player.x && y == player.y) {
                    tileToRender = '@';
                } else {
                    bool objectFound = false ;
                    for (const Object& obj : objects)
                    {
                        if (obj.x == x && obj.y == y)
                        {
                            attron(COLOR_PAIR(obj.color));
                            tileToRender = getSymbolForObjectType(obj.type) ;
                            addch(tileToRender) ;
                            attroff(COLOR_PAIR(obj.color)) ;

                            objectFound = true ;
                            break ;
                        }
                    }
                    if (objectFound == true)
                    {
                        continue ;
                    }

                    bool monsterFound = false;
                    for (const Monster& m : monsters) {
                        if (m.x == x && m.y == y && m.alive) {
                            attron(COLOR_PAIR(m.color));
                            addch(m.symbol);
                            attroff(COLOR_PAIR(m.color));
                            monsterFound = true;
                            break;
                        }
                    }
                    if (monsterFound) continue;
                    tileToRender = dungeonMap[y][x] ;
                }
            }
            else {
                char remembered = player.rememberedDungeon[y][x];
                tileToRender = (remembered == '\0' || remembered == ' ') ? ' ' : remembered;
            }

            if ((teleportMode || lookMode) && x == teleportX && y == teleportY) {
                attron(A_BOLD | A_STANDOUT);
                addch('*');
                attroff(A_BOLD | A_STANDOUT);
            } else {
                addch(tileToRender);
            }
        }
    }

    refresh();
}

void Dungeon::moveMonster(Monster &monster) {
    if (!monster.alive) return;

    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1};
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1};

    // int distanceX = abs(player.x - monster.x);
    // int distanceY = abs(player.y - monster.y);

    bool telepathic = (monster.type & 0x2);
    bool intelligent = (monster.type & 0x1);
    bool tunneling = monster.tunnel;
    bool seePC = false;
    int erratic = (monster.type & 0x8) ? rand() % 2 : 1;

    if ((monster.type & 0x8) && erratic == 0) {
        for (int i = 0; i < 16; i++) {
            int moveIdx = rand() % 8;
            int checkX = monster.x + movesX[moveIdx];
            int checkY = monster.y + movesY[moveIdx];

            if (checkX >= 1 && checkX <= WIDTH - 2 && checkY >= 1 && checkY <= HEIGHT - 2 && hardness[checkY][checkX] < 255) {
                if (hardness[checkY][checkX] == 0) {
                    dungeonMap[monster.y][monster.x] = '.';
                    monster.x = checkX;
                    monster.y = checkY;
                    dungeonMap[monster.y][monster.x] = monster.symbol;
                    if (checkX == player.x && checkY == player.y) {
                        printf("\nGame Over! The PC has been slain by monster '%c' at (%d, %d)!\n", monster.symbol, monster.y, monster.x);
                        exit(0);
                    }
                    return;
                } else if (tunneling) {
                    hardness[checkY][checkX] -= 85;
                    if (hardness[checkY][checkX] <= 0) {
                        hardness[checkY][checkX] = 0;
                        dungeonMap[monster.y][monster.x] = '#';
                        monster.x = checkX;
                        monster.y = checkY;
                        dungeonMap[monster.y][monster.x] = monster.symbol;
                        if (checkX == player.x && checkY == player.y) {
                            printf("\nGame Over! The PC has been slain by monster '%c' at (%d, %d)!\n", monster.symbol, monster.y, monster.x);
                            exit(0);
                        }
                    }
                    return;
                }
            }
        }
    }

    if (!telepathic) {
        int x1 = monster.x, y1 = monster.y, x2 = player.x, y2 = player.y;
        int dx = abs(x2 - x1), dy = abs(y2 - y1);
        int sx = (x1 < x2) ? 1 : -1;
        int sy = (y1 < y2) ? 1 : -1;
        int err = dx - dy;

        while (x1 != x2 || y1 != y2) {
            if (x1 < 1 || x1 >= WIDTH - 1 || y1 < 1 || y1 >= HEIGHT - 1 || dungeonMap[y1][x1] == ' ') {
                seePC = false;
                break;
            }
            if (x1 == x2 && y1 == y2) {
                seePC = true;
                monster.lastSeenX = player.x;
                monster.lastSeenY = player.y;
                break;
            }
            int e2 = 2 * err;
            if (e2 > -dy) { err -= dy; x1 += sx; }
            if (e2 < dx)  { err += dx; y1 += sy; }
        }
    } else {
        seePC = true;
        monster.lastSeenX = player.x;
        monster.lastSeenY = player.y;
    }

    int newX = monster.x, newY = monster.y;
    if (telepathic) {
        if (intelligent) {
            getIntelligentPosition(monster.x, monster.y, player.x, player.y, newX, newY, tunneling);
        } else {
            moveStraightLine(monster, player.x, player.y, newX, newY);
        }
    } else if (seePC) {
        if (intelligent && monster.lastSeenX != -1) {
            getIntelligentPosition(monster.x, monster.y, monster.lastSeenX, monster.lastSeenY, newX, newY, tunneling);
        } else {
            moveStraightLine(monster, monster.lastSeenX, monster.lastSeenY, newX, newY);
        }
    }

    if (hardness[newY][newX] > 0) {
        if (tunneling && hardness[newY][newX] != 255) {
            hardness[newY][newX] -= 85;
            if (hardness[newY][newX] <= 0) {
                hardness[newY][newX] = 0;
                dungeonMap[monster.y][monster.x] = '#';
                monster.x = newX;
                monster.y = newY;
                dungeonMap[monster.y][monster.x] = monster.symbol;
            }
        }
    } else {
        Monster* occupant = getMonsterAt(newX, newY) ;
        if (occupant && occupant != &monster)
        {
            if (!displaceMonster(*occupant))
            {
                std::swap(monster.x, occupant->x);
                std::swap(monster.y, occupant->y);

                dungeonMap[monster.y][monster.x] = monster.symbol;
                dungeonMap[occupant->y][occupant->x] = occupant->symbol ;
            }
            else
            {
                dungeonMap[monster.y][monster.x] = '.' ;
                monster.x = newX;
                monster.y = newY;
                dungeonMap[monster.y][monster.x] = monster.symbol ;
            }

            return ;    
        }
    }

    if (newX == player.x && newY == player.y) {
        int rawdmg = monster.damage.base + (rand() % monster.damage.sides + 1) * monster.damage.dice;
        int defense = player.getModifiedDefense();
        int dmg = rawdmg - defense ;
        int dodgeChance = player.getModifiedDodge() ;

        if ((rand() % 100) < dodgeChance)
        {
            mvprintw(HEIGHT + 1, 0, "You dodged an attack from '%c'!", monster.symbol);
            mvprintw(HEIGHT + 2, 0, "Your HP: %d", player.hp);
            refresh();
            usleep(600000);
            return;
        }

        if (dmg < 0) dmg = 0;

        player.hp -= dmg;

        mvprintw(HEIGHT + 1, 0, "You were hit by %c! Raw Dmg: %d, Defense: %d, Final Damage: %d", 
            monster.symbol, rawdmg, defense, dmg); 
        mvprintw(HEIGHT + 2, 0, "Your HP: %d", player.hp);
        
        refresh();
        usleep(600000);

        if (player.hp <= 0)
        {
            endwin() ;
            printf("\nGame Over! The PC was slain by monster '%c'.\n", monster.symbol);
            exit(0);
        }

        return ;
    }
}

Monster* Dungeon::getMonsterAt(int x, int y) {
    for (auto& m : monsters) {
        if (m.alive && m.x == x && m.y == y) {
            return &m;
        }
    }
    return nullptr;
}

bool Dungeon::displaceMonster(Monster& target) {
    int dx[] = {0, 0, 1, -1, 1, -1, 1, -1};
    int dy[] = {1, -1, 0, 0, 1, 1, -1, -1};

    for (int i = 0; i < 8; ++i) {
        int nx = target.x + dx[i];
        int ny = target.y + dy[i];

        if (nx <= 0 || nx >= WIDTH - 1 || ny <= 0 || ny >= HEIGHT - 1)
            continue;

        if (dungeonMap[ny][nx] == '.' || dungeonMap[ny][nx] == '#') {
            if (!getMonsterAt(nx, ny)) {
                dungeonMap[target.y][target.x] = '.'; // vacate old spot
                target.x = nx;
                target.y = ny;
                dungeonMap[ny][nx] = target.symbol;
                return true;
            }
        }
    }
    return false;
}

void Dungeon::movePlayer(int dx, int dy) {
    int targetX = player.x + dx;
    int targetY = player.y + dy;

    if (targetX < 1 || targetX >= WIDTH - 1 || targetY < 1 || targetY >= HEIGHT - 1)
        return;

    char targetTile = dungeonMap[targetY][targetX];

    if (getMonsterAt(targetX, targetY)) {
        for (auto& monster : monsters) {
            if (monster.alive && monster.x == targetX && monster.y == targetY) {
                Dice pcDamage = player.getModifiedDamage() ;
                int dmg = pcDamage.base + (rand() % pcDamage.sides + 1) * pcDamage.dice ;
                
                int critChance = 10 + player.getModifiedHit() ;
                bool isCritical = (rand() % 100) < critChance ;

                if (isCritical)
                {
                    dmg *= 2 ;
                }

                monster.hp -= dmg ;
                int outputOS = 0 ;
                if (isCritical)
                {
                    mvprintw(HEIGHT + 1, 0, "Critical hit! You dealt %d damage to monster '%c'.", dmg, monster.symbol);  
                }
                else
                {
                    mvprintw(HEIGHT + 1, 0, "You dealt %d damage to monster '%c'.", dmg, monster.symbol);
                }
                mvprintw(HEIGHT + 2, 0, "Remaining HP of monster '%c': %d", monster.symbol, monster.hp);
                outputOS += 2 ;
                refresh();
                usleep(600000);
                
                if (monster.hp <= 0)
                {
                    monster.alive = false ;

                    for (const auto& attr : monsterTemplates) 
                    {
                        if (attr.symbol == monster.symbol && attr.name == "SpongeBob SquarePants") {
                            mvprintw(0, 0, "You defeated the BOSS! You win!");
                            refresh();
                            usleep(2000000);
                            endwin();
                            exit(0);
                        }
                        if (attr.symbol == monster.symbol &&
                            attr.name.find("UNIQUE") != std::string::npos) {
                            usedUniques.insert(attr.name);
                            break;
                        }
                    }

                    dungeonMap[targetY][targetX] = '.';
                    mvprintw(HEIGHT + 1 + outputOS, 0, "Monster killed at (%d, %d)!", targetX, targetY);
                    refresh();
                    usleep(600000);
                }
                return ;
            }
        }
    }

    for (int i = 0 ; i < objects.size() ; i++)
    {
        if (objects[i].x == targetX && objects[i].y == targetY)
        {
            Object* obj = new Object(objects[i]);
            if (player.addToInventory(obj))
            {
                objects.erase(objects.begin() + i);
            }
            else {
                delete obj ;
            }
            break ;
        }
    }


    if (hardness[targetY][targetX] == 0 && !getMonsterAt(targetX, targetY)) {
        dungeonMap[player.y][player.x] = pcLastTile;
        pcLastTile = dungeonMap[targetY][targetX];
        player.updatePosition(targetX, targetY, pcLastTile);
        updateVisibility();
    }
}

void Dungeon::regenerateDungeon(int currentTurnTime) {
    generateHardness();
    createRooms();
    createUpStaircases();
    createDownStaircases();
    calculatePath();
    generatePlayerPosition();
    createMonsters(numMonsters);

    pq.clear();

    int pcTurnTime = currentTurnTime + 1;  
    pq.push(Event(pcTurnTime, true, -1));  

    int monsterDelay = 2;  

    for (size_t i = 0; i < monsters.size(); i++) {
        int monsterTurnTime = pcTurnTime + monsterDelay + (1000 / monsters[i].speed);
        pq.push(Event(monsterTurnTime, false, static_cast<int>(i)));
    }

    player.resetMemory();
    updateVisibility();
}

bool Dungeon::handlePlayerInput(int input, int currentTurnTime) {
    bool playerActed = false;

    if (input == '7' || input == 'y') { 
        movePlayer(-1, -1);
        playerActed = true;
    } else if (input == '8' || input == 'k') { 
        movePlayer(0, -1);
        playerActed = true;
    } else if (input == '9' || input == 'u') {
        movePlayer(1, -1);
        playerActed = true;
    } else if (input == '6' || input == 'l') { 
        movePlayer(1, 0);
        playerActed = true;
    } else if (input == '3' || input == 'n') {
        movePlayer(1, 1);
        playerActed = true;
    } else if (input == '2' || input == 'j') {
        movePlayer(0, 1);
        playerActed = true;
    } else if (input == '1' || input == 'b') { 
        movePlayer(-1, 1);
        playerActed = true;
    } else if (input == '4' || input == 'h') {
        movePlayer(-1, 0);
        playerActed = true;
    } else if (input == '5' || input == ' ' || input == '.') {
        playerActed = true;
    } else if (input == 'm') {
        printMonsters();
        render() ; 
    } else if (input == '<' && pcLastTile == '<') {
        regenerateDungeon(currentTurnTime);
        playerActed = true;
    } else if (input == '>' && pcLastTile == '>') {
        regenerateDungeon(currentTurnTime);
        playerActed = true;
    } 
    else if (input == 'f')
    {
        fogToggle = !fogToggle ;
        render() ;
    }
    else if (input == 'g')
    {
        teleportMode = true ;
        teleportX = player.x ;
        teleportY = player.y ;
        handleTeleportInput();
        render();
        return false ;
    }
    else if (input == 'i')
    {
        clear();
        mvprintw(0, 0, "Inventory:");
        player.listInventory();
        mvprintw(12, 0, "Press any key to continue...");
        getch();
        render();
    }
    else if (input == 'I')
    {
        clear();
        mvprintw(0, 0, "Inspect Item: Enter inventory slot (0-9) or ESC to cancel");
        player.listInventory(); 
    
        int ch = getch();
        if (ch >= '0' && ch <= '9')
        {
            int slot = ch - '0';
            clear();
            if (player.inventory[slot])
            {
                clear();
                Object* item = player.inventory[slot];
                Dice d = item->damage;
            
                int line = 0;
                mvprintw(line++, 0, "Name: %s", item->name.c_str());
                mvprintw(line++, 0, "Type: %s", item->type.c_str());
                mvprintw(line++, 0, "Description: %s", item->description.c_str());
                mvprintw(line++, 0, "Damage: %d+%dd%d", d.base, d.dice, d.sides);
                mvprintw(line++, 0, "Hit Bonus: %d", item->hit);
                mvprintw(line++, 0, "Dodge Bonus: %d", item->dodge);
                mvprintw(line++, 0, "Defense: %d", item->defense);
                mvprintw(line++, 0, "Speed Bonus: %d", item->speed);
                mvprintw(line++, 0, "Attribute Modifier: %d", item->attr);
                mvprintw(line++, 0, "Weight: %d", item->weight);
                mvprintw(line++, 0, "Value: %d", item->value);
                mvprintw(line++, 0, "Artifact: %s", item->artifact ? "Yes" : "No");
            }
            else {
                mvprintw(0, 0, "Slot empty.");  
            }
            mvprintw(10, 0, "Press any key to continue...");
            getch();
        }
        render();
    }
    else if (input == 'w')
    {
        handleWearItemInput();
    }
    else if (input == 't')
    {
        const char* labels = "abcdefghijkl" ;
        clear() ;
        mvprintw(0, 0, "Take Off: Enter equipment slot (a-l), ESC to cancel");
        player.listEquipment();
        int ch = getch() ;
        if (ch == 27)
        {
            return false ;
        }

        int index = strchr(labels, ch) - labels ;
        if (index >= 0 && index < 12)
        {
            player.takeOffItem(index) ;
        }
        render();
    }
    else if (input == 'd')
    {
        clear();
        mvprintw(0, 0, "Drop: Enter inventory slot (0-9), ESC to cancel");
        for (int i = 0 ; i < 10 ; i++)
        {
            if (player.inventory[i])
            {
                mvprintw(i + 1, 0, "%d: %s", i, player.inventory[i]->name.c_str());
            }
        }

        int ch = getch();
        if (ch == 27)
        {
            return false ;
        }
        if (ch >= '0' && ch <= '9')
        {
            player.dropItem(ch - '0', objects);
        }
        render();

    }
    else if (input == 'x')
    {
        clear();
        mvprintw(0, 0, "Expunge: Enter inventory slot (0-9), ESC to cancel");
        for (int i = 0; i < 10; i++)
        {
            if (player.inventory[i])
            {
                mvprintw(i + 1, 0, "%d: %s", i, player.inventory[i]->name.c_str());
            }
        }
        int ch = getch();
        if (ch == 27) 
        {
            return false;
        }
        if (ch >= '0' && ch <= '9') 
        {
            player.expungeItem(ch - '0');
        }
        render();
    }
    else if (input == 'L')
    {
        lookMode = true ;
        teleportX = player.x ;
        teleportY = player.y ;
        handleLookMode() ;
        render();
        return false ;
    }
    else if (input == 'e')
    {
        clear();
        mvprintw(0, 0, "Equipment:");
        player.listEquipment();
        mvprintw(12, 0, "Press any key to continue...");
        getch();
        render();
    }
    else if (input == '^' && pcLastTile == '^')
    {
        Casino::enterCasino(player) ;
        render() ;
        return false ;
    }
    else if (input == 'Q') {
        endwin();
        exit(0);
    }

    return playerActed;
}

void Dungeon::handleTeleportInput()
{
    mvprintw(0, 0, "Teleport Mode: Move with hjkl, g=confirm, r=random, ESC=cancel");
    clrtoeol();
    refresh();

    forceFullRender = true;

    int ch;
    render(); 
    while ((ch = getch())) {
        if (ch == 'g') {
            if (hardness[teleportY][teleportX] != 255) {
                dungeonMap[player.y][player.x] = pcLastTile;
                pcLastTile = dungeonMap[teleportY][teleportX];
                player.updatePosition(teleportX, teleportY, pcLastTile);
                updateVisibility();
            }
            teleportMode = false;
        }
        else if (ch == 'r') {
            while (true) {
                int rx = rand() % WIDTH;
                int ry = rand() % HEIGHT;
                if (hardness[ry][rx] != 255) {
                    dungeonMap[player.y][player.x] = pcLastTile;
                    pcLastTile = dungeonMap[ry][rx];
                    player.updatePosition(rx, ry, pcLastTile);
                    updateVisibility();
                    break;
                }
            }
            teleportMode = false;
        }
        else if (ch == 27) { 
            teleportMode = false;
        }
        else {
            int dx = 0, dy = 0;
            if (ch == 'h') dx = -1;
            else if (ch == 'l') dx = 1;
            else if (ch == 'k') dy = -1;
            else if (ch == 'j') dy = 1;
            else if (ch == 'y') { dx = -1; dy = -1; }
            else if (ch == 'u') { dx = 1; dy = -1; }
            else if (ch == 'b') { dx = -1; dy = 1; }
            else if (ch == 'n') { dx = 1; dy = 1; }

            int nx = teleportX + dx;
            int ny = teleportY + dy;
            if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) {
                teleportX = nx;
                teleportY = ny;
            }
        }

        render();

        if (!teleportMode) break;  
    }

    forceFullRender = false;
}

void Dungeon::handleWearItemInput()
{
    while (true)
    {
        clear();
        mvprintw(0, 0, "Wear: Enter inventory slot (0-9), ESC to cancel");
        for (int i = 0 ; i < 10 ; i++)
        {
            if (player.inventory[i])
            {
                mvprintw(i + 1, 0, "%d: %s", i, player.inventory[i]->name.c_str());
            }
        }

        int ch = getch() ;
        if (ch == 27)
        {
            break ;
        }
    
        if (ch >= '0' && ch <= '9') {
            player.wearItem(ch - '0');
        }
    }

    render();
}

void Dungeon::handleLookMode() {
    mvprintw(0, 0, "Look Mode: Move with hjklbynu, t=inspect, ESC=exit");
    clrtoeol();
    refresh();

    forceFullRender = true;
    int ch;
    render();

    while ((ch = getch())) 
    {
        if (ch == 't') 
        {
            for (const auto& monster : monsters) 
            {
                if (monster.alive && monster.x == teleportX && monster.y == teleportY) 
                {
                    clear();
                    mvprintw(0, 0, "Monster Info:");
                    int line = 1 ;

                    for (const auto& attr : monsterTemplates) 
                    {
                        if (attr.symbol == monster.symbol) 
                        {
                            mvprintw(line++, 0, "Name: %s", attr.name.c_str());
                            mvprintw(line++, 0, "Description: %s", attr.description.c_str());
                            std::istringstream descStream(attr.description);
                            std::string descLine;
                            while (std::getline(descStream, descLine)) 
                            {
                                mvprintw(line++, 0, "%s", descLine.c_str());
                            }
                    
                            std::string abilities = "Abilities: ";
                            for (const std::string& ab : attr.abilities)
                            {
                                abilities += ab + " ";
                            }

                            mvprintw(line++, 0, "%s", abilities.c_str());
                    
                            std::string colors = "Color(s): ";
                            for (const std::string& c : attr.colors)
                            {
                                colors += c + " ";
                            }
                            mvprintw(line++, 0, "%s", colors.c_str());
                    
                            mvprintw(line++, 0, "Speed: %d+%dd%d", attr.speed.base, attr.speed.dice, attr.speed.sides);
                            mvprintw(line++, 0, "HP: %d (current: %d)", attr.hp.base, monster.hp);
                            mvprintw(line++, 0, "Damage: %d+%dd%d", attr.damage.base, attr.damage.dice, attr.damage.sides);
                            break;
                        }
                    }
                    
                    if (line == 1) {
                        mvprintw(line++, 0, "This is monster '%c' at (%d,%d)", monster.symbol, monster.x, monster.y);
                        mvprintw(line++, 0, "HP: %d", monster.hp);
                    }
                    
                    mvprintw(line + 1, 0, "Press any key to return...");
                    getch() ;
                    break;
                }
            }
        } 
        else if (ch == 27) 
        {  
            lookMode = false;
        } 
        else 
        {
            int dx = 0, dy = 0;
            if (ch == 'h') {
                dx = -1;
            }
            else if (ch == 'l') {
                dx = 1;
            }
            else if (ch == 'k') { 
                dy = -1;
            }
            else if (ch == 'j') {
                dy = 1;
            }
            else if (ch == 'y') { 
                dx = -1; dy = -1; 
            }
            else if (ch == 'u') { 
                dx = 1; dy = -1; 
            }
            else if (ch == 'b') { 
                dx = -1; dy = 1; 
            }
            else if (ch == 'n') { 
                dx = 1; dy = 1; 
            }

            int nx = teleportX + dx;
            int ny = teleportY + dy;
            if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) 
            {
                teleportX = nx;
                teleportY = ny;
            }
        }

        render();
        if (!lookMode) break;
    }

    forceFullRender = false;
}


void Dungeon::printMonsters() {
    int scroll = 0;
    int ch;
    int aliveCount = 0;

    while (true) {
        clear();
        mvprintw(0, 0, "Monster List: Press Escape to Quit, Up & Down Arrows to Scroll");

        int line = 1;
        int displayed = 0;
        aliveCount = 0;

        for (const auto& monster : monsters) {
            if (!monster.alive) continue;
            aliveCount++;

            if (displayed < scroll) {
                displayed++;
                continue;
            }

            if (line >= 22) {
                mvprintw(22, 0, "~~Press Down Arrow to Scroll Down~~");
                break;
            }

            int dfpY = monster.y - player.y;
            int dfpX = monster.x - player.x;

            const char* dirY = (dfpY < 0) ? "North" :
                               (dfpY > 0) ? "South" : "Same Row";

            const char* dirX = (dfpX < 0) ? "West" :
                               (dfpX > 0) ? "East" : "Same Column";

            mvprintw(line++, 0, "%c, %d %s and %d %s",
                     monster.symbol, abs(dfpY), dirY, abs(dfpX), dirX);

            displayed++;
        }

        refresh();
        ch = getch();

        if (ch == 27) {  
            break;
        } else if (ch == KEY_DOWN && scroll + 1 < aliveCount) {
            scroll++;
        } else if (ch == KEY_UP && scroll > 0) {
            scroll--;
        }
    }
}

void Dungeon::loadDungeon() {
    const char* home = getenv("HOME");
    if (!home) home = getenv("USERPROFILE");
    if (!home) {
        fprintf(stderr, "Error: Could not find home directory.\n");
        exit(1);
    }

    char filepath[1024];
    snprintf(filepath, sizeof(filepath), "%s%s", home, DUNGEON_PATH);

    FILE* file = fopen(filepath, "rb");
    if (!file) {
        fprintf(stderr, "Error: Could not open dungeon file at %s\n", filepath);
        return;
    }

    char marker[13];
    uint32_t version, fileSize;

    fread(marker, 1, 12, file); marker[12] = '\0';
    if (strcmp(marker, FILE_MARKER) != 0) {
        fprintf(stderr, "Error: Invalid file format.\n");
        fclose(file);
        return;
    }

    fread(&version, sizeof(uint32_t), 1, file);
    version = to_big_endian_32(version);
    if (version != 0) {
        fprintf(stderr, "Error: Unsupported version (%u)\n", version);
        fclose(file);
        return;
    }

    fread(&fileSize, sizeof(uint32_t), 1, file);
    fileSize = to_big_endian_32(fileSize);

    uint8_t pc_x, pc_y;
    fread(&pc_x, 1, 1, file);
    fread(&pc_y, 1, 1, file);
    player.x = pc_x;
    player.y = pc_y;

    for (int y = 0; y < HEIGHT; y++)
        for (int x = 0; x < WIDTH; x++)
            fread(&hardness[y][x], 1, 1, file);

    uint16_t roomCount;
    fread(&roomCount, sizeof(uint16_t), 1, file);
    roomCount = to_big_endian_16(roomCount);
    memset(rooms, 0, sizeof(rooms)); 
    numRooms = roomCount;             
    
    for (int i = 0; i < numRooms; i++) {
        uint8_t x, y, w, h;
        fread(&x, 1, 1, file); fread(&y, 1, 1, file);
        fread(&w, 1, 1, file); fread(&h, 1, 1, file);
        rooms[i] = Room(x, y, w, h);
    }
    for (int y = 0; y < HEIGHT; y++)
        for (int x = 0; x < WIDTH; x++)
            dungeonMap[y][x] = (hardness[y][x] == 0) ? (this->isInRoom(x, y) ? '.' : '#') : ' ';

    uint16_t upCount;
    fread(&upCount, sizeof(uint16_t), 1, file);
    upCount = to_big_endian_16(upCount);
    numUpStairs = upCount;

    for (int i = 0; i < numUpStairs; i++) {
        uint8_t x, y;
        fread(&x, 1, 1, file); fread(&y, 1, 1, file);
        upStaircases[i] = UpStaircase(x, y);
        dungeonMap[y][x] = '<';
    }

    uint16_t downCount;
    fread(&downCount, sizeof(uint16_t), 1, file);
    downCount = to_big_endian_16(downCount);
    numDownStairs = downCount;

    for (int i = 0; i < numDownStairs; i++) {
        uint8_t x, y;
        fread(&x, 1, 1, file); fread(&y, 1, 1, file);
        downStaircases[i] = DownStaircase(x, y);
        dungeonMap[y][x] = '>';
    }
    
    if (dungeonMap[player.y][player.x] != '.' && dungeonMap[player.y][player.x] != '#') {
        player.x = rooms[0].x + 1;
        player.y = rooms[0].y + 1;
    }

    pcLastTile = dungeonMap[player.y][player.x];
    dungeonMap[player.y][player.x] = '@';

    fclose(file);
}

void Dungeon::saveDungeon() {
    const char* home = getenv("HOME");
    if (!home) home = getenv("USERPROFILE");
    if (!home) {
        fprintf(stderr, "Error: Could not find home directory.\n");
        exit(1);
    }

    char dirpath[512];
    if (snprintf(dirpath, sizeof(dirpath), "%s/.rlg327", home) >= (int)sizeof(dirpath)) {
        fprintf(stderr, "Directory path too long\n");
        return;
    }

    char filename[512];

    if (snprintf(filename, sizeof(filename), "%s/dungeon", dirpath) >= (int)sizeof(filename)) {
        fprintf(stderr, "Dungeon path too long\n");
        return;
    }    
    ensureDirectoryExists(dirpath);

    FILE* file = fopen(filename, "wb");
    if (!file) {
        perror("Error opening file for saving.");
        return;
    }

    fwrite(FILE_MARKER, 1, 12, file);
    uint32_t version = 0;
    fwrite(&version, sizeof(uint32_t), 1, file);

    uint32_t fileSize = 1708 + (numRooms * 4) + (numUpStairs + numDownStairs) * 2;
    fileSize = to_big_endian_32(fileSize);
    fwrite(&fileSize, sizeof(uint32_t), 1, file);

    uint8_t pc_x = player.x;
    uint8_t pc_y = player.y;
    fwrite(&pc_x, 1, 1, file);
    fwrite(&pc_y, 1, 1, file);

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            uint8_t h = hardness[y][x];
            fwrite(&h, 1, 1, file);
        }
    }

        uint16_t roomCount = to_big_endian_16(numRooms);
        fwrite(&roomCount, sizeof(uint16_t), 1, file);
        
        for (int i = 0; i < numRooms; i++) {
            uint8_t data[4] = {
                (uint8_t)rooms[i].x,
                (uint8_t)rooms[i].y,
                (uint8_t)rooms[i].width,
                (uint8_t)rooms[i].height
            };
            fwrite(data, 1, 4, file);
        }

    uint16_t ups = to_big_endian_16(numUpStairs);
    fwrite(&ups, sizeof(uint16_t), 1, file);
    
    for (int i = 0; i < numUpStairs; i++) {
        fwrite(&upStaircases[i].x, 1, 1, file);
        fwrite(&upStaircases[i].y, 1, 1, file);
    }
    

    uint16_t downs = to_big_endian_16(numDownStairs);
    fwrite(&downs, sizeof(uint16_t), 1, file);
    
    for (int i = 0; i < numDownStairs; i++) {
        fwrite(&downStaircases[i].x, 1, 1, file);
        fwrite(&downStaircases[i].y, 1, 1, file);
    }

    fclose(file);
}


bool Dungeon::checkVictory() {
    for (auto &m : monsters)
        if (m.alive) return false;
    return true;
}

void Dungeon::runGameLoop(int argc, char* argv[]) {
    srand(time(NULL));

    // ncurses init
    initscr();
    start_color() ;
    init_pair(COLOR_RED, COLOR_RED, COLOR_BLACK);
    init_pair(COLOR_GREEN, COLOR_GREEN, COLOR_BLACK);
    init_pair(COLOR_YELLOW, COLOR_YELLOW, COLOR_BLACK);
    init_pair(COLOR_BLUE, COLOR_BLUE, COLOR_BLACK);
    init_pair(COLOR_CYAN, COLOR_CYAN, COLOR_BLACK);
    init_pair(COLOR_MAGENTA, COLOR_MAGENTA, COLOR_BLACK);
    init_pair(COLOR_WHITE, COLOR_WHITE, COLOR_BLACK);
    raw();
    keypad(stdscr, TRUE);
    set_escdelay(10); 
    noecho();
    curs_set(0);

    bool save = false;
    bool load = false;
    int numMonsters = rand() % 11 + 10;
    bool suppressMonsterTurns = false;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--save") == 0) {
            save = true;
        } else if (strcmp(argv[i], "--load") == 0) {
            load = true;
        } else if (strcmp(argv[i], "--nummon") == 0 && i + 1 < argc) {
            numMonsters = atoi(argv[i + 1]);
            if (numMonsters <= 0) numMonsters = 10;
        }
    }

    
    if (load) {
        loadDungeon(); 
        calculateDistanceMap(distanceMapNonTunnel, player.x, player.y, false);
        calculateDistanceMap(distanceMapTunnel, player.x, player.y, true);
    } else {
        generate(numMonsters);
    }

    if (save) {
        saveDungeon();
    }

    calculateDistanceMap(distanceMapNonTunnel, player.x, player.y, false);
    calculateDistanceMap(distanceMapTunnel, player.x, player.y, true);

    pq.clear();

    Event pcTurn(0, true, -1);
    pq.push(pcTurn);
    int pcFirstTurnTime = 0 ;
    int monsterDelay = 1 ;

    for (size_t i = 0; i < monsters.size(); i++) {
        int monsterTurnTime = pcFirstTurnTime + monsterDelay + (1000 / monsters[i].speed);
        Event monsterTurn(monsterTurnTime, false, static_cast<int>(i));
        pq.push(monsterTurn);
    }

    int gameTime = 0;

    while (!pq.isEmpty()) {
        Event current = pq.pop();
        gameTime = current.turnTime;

        if (current.isPC) {
            
           if (player.hp < player.maxHP && (rand() % 3 == 0))
           {
                player.updateHP(gameTime) ;
           } 

            while (teleportMode) {
                handleTeleportInput();
                render();  
            }
            render();
            int input = getch();
            bool playerActed = handlePlayerInput(input, current.turnTime);

            if (teleportMode) { 
                continue;
            }

            if (!playerActed) { 
                suppressMonsterTurns = true ;
                pq.push(current); 
                continue;         
            }

            if (playerActed) {
                suppressMonsterTurns = false ;
                calculateDistanceMap(distanceMapNonTunnel, player.x, player.y, false);
                calculateDistanceMap(distanceMapTunnel, player.x, player.y, true);

                if (!(pcLastTile == '<' && input == '<') && !(pcLastTile == '>' && input == '>')) {
                    current.turnTime += (1000 / player.getModifiedSpeed());
                    pq.push(current);
                }
            }

        } else if (suppressMonsterTurns == false && monsters[current.index].alive) {
            Monster& m = monsters[current.index];
            if (m.hp < m.maxHP && (rand() % 3 == 0))
            {
                m.updateHP(gameTime) ;
            }
            moveMonster(monsters[current.index]);
            current.turnTime += (1000 / monsters[current.index].speed);
            pq.push(current);
        }

        int aliveMonsters = std::count_if(monsters.begin(), monsters.end(),
                                          [](const Monster &m) { return m.alive; });

        // if (aliveMonsters == 0) {
        //     endwin();
        //     printf("\nAll monsters have been slain! You win!\n");
        //     exit(0);
        // }

        usleep(10);
    }

    endwin();
}
