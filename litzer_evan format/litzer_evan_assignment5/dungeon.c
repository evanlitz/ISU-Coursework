/*
    @Author Evan Litzer
    March 23rd, 2025
    Dungeon.c
*/

#ifdef _WIN32
    #include <windows.h>
    #define usleep(x) Sleep((x) / 1000)
#else
    #include <unistd.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>
#include <ncurses.h>
#include <errno.h>

#define MIN_ROOMS 6
#define MAX_ROOMS 10
#define MAX_ROOM_X_SIZE 15
#define MIN_ROOM_X_SIZE 4
#define MAX_ROOM_Y_SIZE 15
#define MIN_ROOM_Y_SIZE 4
#define MAX_STAIRCASE_DOWN 5
#define MAX_STAIRCASE_UP 5
#define NUM_MONSTERS 15

#define DUNGEON_WIDTH 80
#define DUNGEON_HEIGHT 21
#define FILE_MARKER "RLG327-S2025"
#define FILE_VERSION 0
#define DUNGEON_PATH "/.rlg327/dungeon"

#define MAX_TURNS 10000


typedef struct {
    int x, y;
    int width, height;
} Room;

typedef struct {
    int x, y ;
} UpStaircase;

typedef struct {
    int x, y ;
} DownStaircase;

typedef struct {
    int x, y;
    int distance;
} Point;

typedef struct {
    int x, y;
    bool tunnel ;
    int speed ;
    int type ;
    char symbol ;
    bool alive ;
    int lastSeenX ;
    int lastSeenY ;
} Monster;

typedef struct {
    int turnTime ;
    bool isPC ;
    int index ;
} Event;

typedef struct {
    Event events[MAX_TURNS] ;
    int size ;
} PriorityQueue;

int numUpStairs = 0 ;
int numDownStairs = 0 ;

// typedef struct {
//     char map[21][80];  
//     int hardness[21][80];     
//     int playerX, playerY;     
// } Dungeon;

Room rooms[MAX_ROOMS] ;
UpStaircase upStaircases[MAX_STAIRCASE_UP] ;
DownStaircase downStaircases[MAX_STAIRCASE_DOWN] ;
char originalDungeonMap[21][80] ;


void generateHardness(int hardness[21][80], char dungeonMap[21][80])
{
    for(int y = 0 ; y < 21 ; y++)
    {
        for(int x = 0 ; x < 80 ; x++)
        {
            if(y == 0 || y == 20 || x == 0 || x == 79)
            {
                hardness[y][x] = 255 ;
                dungeonMap[y][x] = ' ' ;
            }
            else
            {
                hardness[y][x] = (rand() % 254) + 1 ;
                dungeonMap[y][x] = ' ' ;
            }
        }
    }
}

void Dungeon::createRooms() {
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

            // Room placement is valid; assign and draw
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
}


bool isInRoom(int x, int y, int numRooms) {
    for (int i = 0; i < numRooms; i++) {
        if (x >= rooms[i].x && x < rooms[i].x + rooms[i].width &&
            y >= rooms[i].y && y < rooms[i].y + rooms[i].height) {
            return true;
        }
    }
    return false;
}

void getRoomCenter(Room room, int *centerX, int *centerY)
{
    *centerX = room.x + room.width / 2 ;
    *centerY = room.y + room.height / 2 ;
}

double pathDistanceCalc(int room1X, int room1Y, int room2X, int room2Y)
{
    return (room2X - room1X) * (room2X - room1X) + (room2Y - room1Y) * (room2Y - room1Y) ;
}

int createUpStaircases(char dungeonMap[21][80], int hardness[21][80], int totalRooms)
{
    int upstairTotal = (rand() % MAX_STAIRCASE_UP) + 1 ;
    int upstairsAmount = 0 ;

    while (upstairsAmount < upstairTotal)
    {
        int randomRoom = rand() % totalRooms ;

        int stairX = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
        int stairY = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);

        if (dungeonMap[stairY][stairX] == '.')
        {
            dungeonMap[stairY][stairX] = '<' ;
            hardness[stairY][stairX] = 0 ;

            upStaircases[upstairsAmount] = (UpStaircase){stairX, stairY};

            upstairsAmount++ ;
        }
    }

    numUpStairs = upstairsAmount ;
    return upstairTotal ;
}

int createDownStaircases(char dungeonMap[21][80], int hardness[21][80], int totalRooms)
{
    int downstairTotal = (rand() % MAX_STAIRCASE_DOWN) + 1 ;

    int downstairsAmount = 0 ;

    while (downstairsAmount < downstairTotal)
    {
        int randomRoom = rand() % totalRooms ;

        int stairX = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
        int stairY = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);

        if (dungeonMap[stairY][stairX] == '.')
        {
            dungeonMap[stairY][stairX] = '>' ;
            hardness[stairY][stairX] = 0 ;
            downStaircases[downstairsAmount] = (DownStaircase){stairX, stairY};
            downstairsAmount++ ;
        }
    }

    numDownStairs = downstairsAmount ;
    return downstairTotal ;
}

void generatePath(char dungeonMap[21][80], int hardness[21][80], int room1X, int room1Y, int room3X, int room3Y) {
    int x = room1X;
    int y = room1Y;

    while (x != room3X || y != room3Y) {
        if (x <= 0 || x >= 79 || y <= 0 || y >= 20) 
        {
            break; 
        }

        if (dungeonMap[y][x] == ' ') 
        {
            dungeonMap[y][x] = '#';
            hardness[y][x] = 0 ;
        }

        if (rand() % 2 == 0) 
        {
            if (x < room3X) x++;
            else if (x > room3X) x--;
        } else {
            if (y < room3Y) y++;
            else if (y > room3Y) y--;
        }
    }
}

void calculatePath(char dungeonMap[21][80], int totalRooms, int hardness[21][80])
{
    bool isConnected[totalRooms];
    for(int j = 0 ; j < totalRooms ; j++)
    {
        isConnected[j] = false ;
    }

    isConnected[0] = true ;

    for(int z = 1 ; z < totalRooms ; z++)
    {
        int nearestRoom = -10 ;
        double minDistance = 10000000 ;

        int room1X ;
        int room1Y ;
    
        getRoomCenter(rooms[z], &room1X, &room1Y) ;

        for(int a = 0 ; a < z ; a++)
        {
            if (isConnected[a] == true)
            {
                int room2X ;
                int room2Y ;
                getRoomCenter(rooms[a], &room2X, &room2Y) ;
                
                double distance = pathDistanceCalc(room1X, room1Y, room2X, room2Y) ;

                if(distance < minDistance)
                {
                    minDistance = distance ;
                    nearestRoom = a ;
                }
            }

            if(nearestRoom != -10)
            {
                int room3X, room3Y;
                getRoomCenter(rooms[nearestRoom], &room3X, &room3Y);

                int room1X, room1Y;
                getRoomCenter(rooms[z], &room1X, &room1Y);

                int room1XOffset = (rand() % (rooms[z].width / 2 + 1));
                if (rand() % 2 == 0) {
                    room1XOffset *= -1;
                }

                int room1YOffset = (rand() % (rooms[z].height / 2 + 1));
                if (rand() % 2 == 0) {
                    room1YOffset *= -1;
                }

                int room3XOffset = (rand() % (rooms[nearestRoom].width / 2 + 1));
                if (rand() % 2 == 0) {
                    room3XOffset *= -1;
                }

                int room3YOffset = (rand() % (rooms[nearestRoom].height / 2 + 1));
                if (rand() % 2 == 0) {
                    room3YOffset *= -1;
                }

                room1X += room1XOffset;
                room1Y += room1YOffset;
                room3X += room3XOffset;
                room3Y += room3YOffset;

                if (room1X < rooms[z].x) {
                room1X = rooms[z].x;
                } 
                else if (room1X >= rooms[z].x + rooms[z].width) {
                room1X = rooms[z].x + rooms[z].width - 1;
                }

                if (room1Y < rooms[z].y) {
                room1Y = rooms[z].y;
                } 
                else if (room1Y >= rooms[z].y + rooms[z].height) {
                room1Y = rooms[z].y + rooms[z].height - 1;
                }

                if (room3X < rooms[nearestRoom].x) {
                room3X = rooms[nearestRoom].x;
                } 
                else if (room3X >= rooms[nearestRoom].x + rooms[nearestRoom].width) {
                room3X = rooms[nearestRoom].x + rooms[nearestRoom].width - 1;
                }

                if (room3Y < rooms[nearestRoom].y) {
                room3Y = rooms[nearestRoom].y;
                } 
                else if (room3Y >= rooms[nearestRoom].y + rooms[nearestRoom].height) {
                room3Y = rooms[nearestRoom].y + rooms[nearestRoom].height - 1;
                }

                generatePath(dungeonMap, hardness, room1X, room1Y, room3X, room3Y);

                isConnected[z] = true;
            }
        }
    }


}

void generatePlayerPosition(char dungeonMap[21][80], int totalRooms, int *playerX, int *playerY, char *pcLastTile)
{
    int randomRoom = rand() % totalRooms ;

    while(rooms[randomRoom].width <= 0 || rooms[randomRoom].height == 0)
    {
        randomRoom = rand() % totalRooms ;
    }

    *playerX = rooms[randomRoom].x + (rand() % rooms[randomRoom].width);
    *playerY = rooms[randomRoom].y + (rand() % rooms[randomRoom].height);
    
    *pcLastTile = dungeonMap[*playerY][*playerX];
    dungeonMap[*playerY][*playerX] = '@';

}

void calculateDistanceMap(char dungeonMap[21][80], int hardness[21][80], int playerX, int playerY, int distanceMap[21][80], bool tunnelMonster)
{
    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1} ;
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1} ;

    bool visited[21][80] = { false } ;

    Point pq[1680] ;
    int pqSize = 0 ;

    for (int y = 0 ; y < 21 ; y++)
    {
        for (int x = 0 ; x < 80 ; x++)
        {
            distanceMap[y][x] = 1000000 ;
            visited[y][x] = false ;
        }
    }


    distanceMap[playerY][playerX] = 0 ;

    pq[pqSize++] = (Point){playerX, playerY, 0} ;

    while (pqSize > 0)
    {
        int minIndex = 0 ;
        for (int i = 1 ; i < pqSize ; i++)
        {
            if (pq[i].distance < pq[minIndex].distance)
            {
                minIndex = i ;
            }
        }

        Point curr = pq[minIndex];
        pq[minIndex] = pq[--pqSize];
        int x = curr.x ;
        int y = curr.y ;

        if (visited[y][x] == false)
        {
            visited[y][x] = true ;

            for(int i = 0 ; i < 8 ; i++)
            {
                int checkX = x + movesX[i] ;
                int checkY = y + movesY[i] ;

                if(checkX < 80 && checkX >= 0 && checkY >= 0 && checkY < 21 && visited[checkY][checkX] == false)
                {
                    int weight = 1 ;

                    if (tunnelMonster == true)
                    {
                        if (hardness[checkY][checkX] != 255)
                        {
                            weight += hardness[checkY][checkX] / 85 ;
                        }
                        else
                        {
                            continue ;
                        }
                    }
                    else
                    {
                        if (dungeonMap[checkY][checkX] == ' ' || hardness[checkY][checkX] > 0)
                        {
                            continue ;
                        }
                    }

                    int checkDistance = distanceMap[y][x] + weight ;

                    if (checkDistance < distanceMap[checkY][checkX])
                    {
                        distanceMap[checkY][checkX] = checkDistance ;
                        pq[pqSize++] = (Point){checkX, checkY, checkDistance} ;
                    }
                }
            }
        }
    }
}

void drawDungeonMap(char dungeonMap[21][80]) {
    clear();
    for (int y = 0; y < 21; y++) 
    {
        for (int x = 0; x < 80; x++) 
        {
            move(y+1, x);
            addch(dungeonMap[y][x]);
        }
    }
    refresh(); 
}

void printDistanceMap(int distanceMap[21][80], char dungeonMap[21][80], int playerX, int playerY, bool tunnel) {
    for (int y = 0; y < 21; y++) 
    {
        for (int x = 0; x < 80; x++) 
        {
            if (x == playerX && y == playerY) 
            {
                printf("@");  
            } 
            else if (tunnel == false && (dungeonMap[y][x] == ' ' || distanceMap[y][x] == 1000000)) 
            {
                printf(" ");  
            } 
            else if (tunnel == true && distanceMap[y][x] == 1000000) 
            {
                printf("#");  
            } 
            else 
            {
                printf("%d", distanceMap[y][x] % 10);  
            }
        }
        printf("\n");  
    }
}

void printHardness(int hardness[21][80]) {
    for (int y = 0; y < 21; y++) {
        for (int x = 0; x < 80; x++) {
            printf("%d ", hardness[y][x]);
        }
        printf("\n");
    }
}

uint32_t to_big_endian_32(uint32_t value) {
    return ((value >> 24) & 0x000000FF) |
           ((value >> 8)  & 0x0000FF00) |
           ((value << 8)  & 0x00FF0000) |
           ((value << 24) & 0xFF000000);
}

uint16_t to_big_endian_16(uint16_t value) {
    return (value >> 8) | (value << 8);
}

void ensure_directory_exists(const char *dirpath) {
    struct stat st = {0};
    if (stat(dirpath, &st) == -1) {  
        #ifdef _WIN32
            if (mkdir(dirpath) != 0 && errno != EEXIST) {
                perror("Error creating directory");
                exit(1);
            }
        #else
            if (mkdir(dirpath, 0777) != 0 && errno != EEXIST) {
                perror("Error creating directory");
                exit(1);
            }
        #endif
    }
}

void getIntelligentPosition(int x, int y, int playerX, int playerY, int *nextX, int *nextY, int hardness[21][80], char dungeonMap[21][80], bool tunnel)
{
    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1} ;
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1} ;

    int distanceMap[21][80] ;

    calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMap, tunnel) ;

    int minDistance = distanceMap[y][x] ;
    *nextX = x ;
    *nextY = y ;

    for(int i = 0 ; i < 8 ; i++)
    {
        int checkX = x + movesX[i];
        int checkY = y + movesY[i];

        if (checkX > 0 && checkX < 80 && checkY > 0 && checkY < 21)
        {
            if (tunnel == true)
            {
                if (hardness[checkY][checkX] < 255)
                {
                    if (distanceMap[checkY][checkX] < minDistance)
                    {
                        minDistance = distanceMap[checkY][checkX] ;
                        *nextX = checkX ;
                        *nextY = checkY ;
                    }
                }
            }
            else 
            {
                if (dungeonMap[checkY][checkX] == '.' || dungeonMap[checkY][checkX] == '#')
                {
                    if (distanceMap[checkY][checkX] < minDistance)
                    {
                        minDistance = distanceMap[checkY][checkX] ;
                        *nextX = checkX ;
                        *nextY = checkY ;
                    }
                }
            }
        }        
    }
}

void moveStraightLine(Monster *monster, int playerX, int playerY, int *newX, int *newY) {
    int moveX = 0, moveY = 0;

    if (playerX > monster->x) {
        moveX = 1;
    } else if (playerX < monster->x) {
        moveX = -1;
    }

    if (playerY > monster->y) {
        moveY = 1;
    } else if (playerY < monster->y) {
        moveY = -1;
    }

    if (moveX != 0) {
        int tempX = monster->x + moveX ;
        if (tempX >= 1 && tempX <= 78)
        {
            *newX = tempX ;
            *newY = monster->y;
        }
    } 
    
    if (moveY != 0 && *newX == monster->x) {
        int tempY = monster->y + moveY;
        if (tempY >= 1 && tempY <= 19) 
        {  
            *newX = monster->x;
            *newY = tempY;
        }
    }
}

void createMonsters(char dungeonMap[21][80], Monster monsters[], int numMonsters, int hardness[21][80])
{
    for(int i = 0 ; i < numMonsters ; i++)
    {
        int monsterX, monsterY ;
        int monsterType = rand() % 16 ;
        bool tunnel = (monsterType & 0x4) != 0;

        do
        {
            monsterY = rand() % 19 + 1 ;
            monsterX = rand() % 78 + 1 ;
        }
        while((tunnel == false && dungeonMap[monsterY][monsterX] != '.') || (tunnel == true && hardness[monsterY][monsterX] == 255) || dungeonMap[monsterY][monsterX] == '@') ;
            
        monsters[i].x = monsterX ;
        monsters[i].y = monsterY ;
        monsters[i].speed = (rand() % 16) + 5;
        monsters[i].type = monsterType ;
        monsters[i].alive = true ;
        monsters[i].lastSeenX = -1;
        monsters[i].lastSeenY = -1;
        if(monsterType < 10)
        {
            monsters[i].symbol = '0' + monsterType ;
        }
        else 
        {
            monsters[i].symbol = 'a' + (monsterType - 10);
        }

        dungeonMap[monsterY][monsterX] = monsters[i].symbol ;
    }
}

// void movePlayer(char dungeonMap[21][80], int hardness[21][80], int *playerX, int *playerY, char *pcLastTile, Monster monsters[], int numMonsters)
// {
//     int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1} ;
//     int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1} ;

//     int randomMove = rand() % 8 ;
//     int checkX = *playerX + movesX[randomMove] ;
//     int checkY = *playerY + movesY[randomMove] ;

//     if (dungeonMap[checkY][checkX] >= '0' && dungeonMap[checkY][checkX] <= 'f') 
//     {
//         for (int i = 0; i < numMonsters; i++)
//         {
//             if (monsters[i].alive == true && monsters[i].x == checkX && monsters[i].y == checkY) 
//             {
//                 printf("\nPC killed monster at (%d, %d)!\n", checkX, checkY);
//                 monsters[i].alive = false; 
//                 dungeonMap[checkY][checkX] = '.';  
//                 break;
//             }
//         }
//     }

//     if (checkX > 0 && checkX < 79 && checkY > 0 && checkY < 20 && hardness[checkY][checkX] < 255)
//     {
//         if (hardness[checkY][checkX] > 0)
//         {
//             dungeonMap[checkY][checkX] = '#' ;
//             hardness[checkY][checkX] = 0 ;
//         }

//         dungeonMap[*playerY][*playerX] = *pcLastTile;

//         *pcLastTile = dungeonMap[checkY][checkX];

//         *playerX = checkX ;
//         *playerY = checkY ;
//         dungeonMap[*playerY][*playerX] = '@' ;
//     }
// }

void movePlayer(char dungeonMap[21][80], int hardness[21][80], int my, int mx, int *playerX, int *playerY, char *pcLastTile, Monster monsters[], int numMonsters)
{
    int moveToX = *playerX + mx ;
    int moveToY = *playerY + my ;

    if (moveToX < 1 || moveToX >= 79 || moveToY < 1 || moveToY >= 20)
    {
        return ;
    }

    if(dungeonMap[moveToY][moveToX] >= '0' && dungeonMap[moveToY][moveToX] <= 'f')
    {
        for (int i = 0 ; i < numMonsters ; i++)
        {
            if(monsters[i].x == moveToX && monsters[i].y == moveToY && monsters[i].alive == true)
            {
                monsters[i].alive = false ;
                dungeonMap[moveToY][moveToX] = '.' ;
                mvprintw(0, 0, "Monster killed at (%d, %d)!", moveToX, moveToY); 
                refresh() ;
                usleep(10000);
                break ;
            }
        }
    }

    if (hardness[moveToY][moveToX] == 0)
    {
        dungeonMap[*playerY][*playerX] = *pcLastTile ;
        *pcLastTile = dungeonMap[moveToY][moveToX] ;
        *playerX = moveToX ;
        *playerY = moveToY ;
        dungeonMap[*playerY][*playerX] = '@' ;
    }
}


void moveMonster(char dungeonMap[21][80], int hardness[21][80], Monster *monster, int playerX, int playerY)
{
    if(monster->alive == false)
    {
        return ;
    }
    
    int movesX[] = {0, 0, 1, 1, 1, -1, -1, -1} ;
    int movesY[] = {1, -1, 0, 1, -1, 0, 1, -1} ;

    int distanceX = abs(playerX - monster->x);
    int distanceY = abs(playerY - monster->y);

    bool telepathic = (monster->type & 0x2) ;
    bool seePC = false ;
    bool intelligent = (monster->type & 0x1);
    bool tunneling = (monster->type & 0x4);

    int erratic = rand() % 2 ;
    
    if(monster->type & 0x8)
    {
        if (erratic == 0)
        {
            for (int i = 0 ; i < 16 ; i++) 
            {
                int randomMove = rand() % 8 ;
                int checkX = monster->x + movesX[randomMove] ;
                int checkY = monster->y + movesY[randomMove] ;

                if (checkX >= 1 && checkX <= 78 && checkY >= 1 && checkY <= 19 && hardness[checkY][checkX] < 255)
                {
                    if (hardness[checkY][checkX] == 0)
                    {
                        dungeonMap[monster->y][monster->x] = '.' ;
                        hardness[monster->y][monster->x] = 0 ;
                        monster->x = checkX ;
                        monster->y = checkY ;
                        dungeonMap[monster->y][monster->x] = monster->symbol ;
                        if (checkX == playerX && checkY == playerY) {
                            printf("\nGame Over! The PC has been slain by a monster at (%d, %d)!\n", checkX, checkY);
                            exit(0);  
                        }
                        return ;
                    }
                    else if(tunneling == true)
                    {
                        hardness[checkY][checkX] -= 85 ;
                        if (hardness[checkY][checkX] <= 0)
                        {
                            hardness[checkY][checkX] = 0 ;
                            dungeonMap[monster->y][monster->x] = '#' ;
                            hardness[monster->y][monster->x] = 0 ;
                            monster->x = checkX ;
                            monster->y = checkY ;
                            dungeonMap[monster->y][monster->x] = monster->symbol ;
                            if (checkX == playerX && checkY == playerY) {
                                printf("\nGame Over! The PC has been slain by a monster at (%d, %d)!\n", checkX, checkY);
                                exit(0);  
                            }
                            return ;
                        }
                        else
                        {
                            return ;
                        }
                    }
                }
            }
        }
    }

    if(telepathic == false)
    {
        int x1 = monster->x;
        int y1 = monster->y;
        int x2 = playerX;
        int y2 = playerY;

        int goX, goY ;
        if(x1 < x2)
        {
            goX = 1;
        }
        else
        {
            goX = -1 ;
        }

        if(y1 < y2)
        {
            goY = 1;
        }
        else
        {
            goY = -1 ;
        }

        int err = distanceX - distanceY ;

        while(x1 != x2 || y1 != y2)
        {
            if(x1 < 1 || x1 > 78 || y1 < 1 || y1 > 19)
            {
                seePC = false ;
                break ;
            }
            if (dungeonMap[y1][x1] == ' ')
            {
                seePC = false ;
                break ;
            }

            if (x1 == x2 && y1 == y2) 
            {
                seePC = true;
                monster->lastSeenX = playerX;
                monster->lastSeenY = playerY;
                break;
            }
            int e2 = 2 * err ;
            if(e2 > -distanceY)
            {
                err -= distanceY ;
                x1 += goX ;
            }
            if(e2 < distanceX)
            {
                err += distanceX ;
                y1 += goY ;
            }    
        }
    }
    else
    {
        seePC = true;
        monster->lastSeenX = playerX;
        monster->lastSeenY = playerY;
    }

    int newX = monster->x;
    int newY = monster->y;

    if(telepathic == false)
    {
        if (intelligent == true && monster->lastSeenX != -1 && monster->lastSeenY != -1)
        {
            getIntelligentPosition(monster->x, monster->y, monster->lastSeenX, monster->lastSeenY, &newX, &newY, hardness, dungeonMap, tunneling);
        }
        else if (intelligent == false && seePC == true)
        {
            moveStraightLine(monster, monster->lastSeenX, monster->lastSeenY, &newX, &newY) ; 
        }
    }
    else if(telepathic == true)
    {
        if(intelligent == true)
        {
            getIntelligentPosition(monster->x, monster->y, playerX, playerY, &newX, &newY, hardness, dungeonMap, tunneling);
        }
        else
        {
            moveStraightLine(monster, playerX, playerY, &newX, &newY) ;
        }
    }
    
    if (hardness[newY][newX] > 0)
    {
        if (tunneling == true && hardness[newY][newX] != 255)
        {
            hardness[newY][newX] -= 85 ;
            if (hardness[newY][newX] <= 0)
            {
                hardness[newY][newX] = 0 ;
                dungeonMap[monster->y][monster->x] = '#' ;
                hardness[monster->y][monster->x] = 0 ;
                monster->x = newX ;
                monster->y = newY ;
                dungeonMap[monster->y][monster->x] = monster->symbol ;
            }
            else
            {
                // do nothing
            }
        }
    }
    else
    {
        dungeonMap[monster->y][monster->x] = '.' ;
        hardness[monster->y][monster->x] = 0 ;
        hardness[newY][newX] = 0 ;
        monster->x = newX ;
        monster->y = newY ;
        dungeonMap[monster->y][monster->x] = monster->symbol ;
    }

    if (newX == playerX && newY == playerY) {
        printf("\nGame Over! The PC has been slain by a monster at (%d, %d)!\n", newX, newY);
        exit(0);  
    }

    return ;

}

void swap(Event *a, Event *b)
{
    Event temp = *a;
    *a = *b;
    *b = temp;
}

void push(PriorityQueue *pq, Event event)
{
    int i = pq->size++;
    pq->events[i] = event ;

    while(i > 0 && pq->events[i].turnTime < pq->events[(i-1) / 2].turnTime)
    {
        swap(&pq->events[i], &pq->events[(i-1) / 2]);
        i = (i-1) / 2 ;
    }
}

Event pop(PriorityQueue *pq)
{
    Event top = pq->events[0] ;
    pq->events[0] = pq->events[--pq->size] ;

    int i = 0 ;
    while (2 * i + 1 < pq->size) 
    {
        int minChild = 2 * i + 1;
        if (minChild + 1 < pq->size && pq->events[minChild + 1].turnTime < pq->events[minChild].turnTime) 
        {
            minChild++;
        }
        if (pq->events[i].turnTime <= pq->events[minChild].turnTime) break;
        swap(&pq->events[i], &pq->events[minChild]);
        i = minChild;
    }
    return top;
}

bool isEmpty(PriorityQueue *pq) {
    return pq->size == 0;
}


void loadDungeon(char dungeonMap[21][80], int hardness[21][80], int *playerX, int *playerY, int *numRooms, int *numUpStairs, int *numDownStairs)
{
    char *home = getenv("HOME");
    if (!home) {
        home = getenv("USERPROFILE"); 
    }
    
    if (!home) {
        fprintf(stderr, "Error: Could not find home directory.\n");
        exit(1);
    }

    char filepath[1024] ;
    snprintf(filepath, sizeof(filepath), "%s%s", home, DUNGEON_PATH);

    FILE *file = fopen(filepath, "rb");
    if (!file)
    {
        fprintf(stderr, "Error: Could not open dungeon file at %s\n", filepath);
        return ;
    }

    char marker[13];
    uint32_t version ;
    uint32_t fileSize ;

    fread(marker, 1, 12, file);
    marker[12] = '\0' ;
    if (strcmp(marker, "RLG327-S2025") != 0)
    {
        fprintf(stderr, "Error: Invalid file format. \n") ;
        fclose(file) ;
        return ;
    }

    fread(&version, sizeof(uint32_t), 1, file) ;
    version = to_big_endian_32(version) ;

    if(version != 0)
    {
        fprintf(stderr, "Error: Unsupported file version (%u). \n", version);
        fclose(file);
        return ;
    }

    fread(&fileSize, sizeof(uint32_t), 1, file) ;
    fileSize = to_big_endian_32(fileSize) ;

    uint8_t playerposX ;
    uint8_t playerposY ;
    fread(&playerposX, sizeof(uint8_t), 1, file) ;
    fread(&playerposY, sizeof(uint8_t), 1, file) ;

    *playerX = playerposX ;
    *playerY = playerposY ;

    memset(rooms, 0, sizeof(rooms));


    for(int y = 0 ; y < 21 ; y++)
    {
        for(int x = 0 ; x < 80; x++)
        {
            uint8_t pixel ;
            fread(&pixel, sizeof(uint8_t), 1, file);
            hardness[y][x] = pixel ;

        }
    }

    uint16_t roomCount ;
    fread(&roomCount, sizeof(uint16_t), 1, file);
    roomCount = to_big_endian_16(roomCount) ;
    *numRooms = roomCount ;

    for (int z = 0 ; z < *numRooms ; z++)
    {
        uint8_t x ;
        uint8_t y ;
        uint8_t width ;
        uint8_t height ;
        fread(&x, sizeof(uint8_t), 1, file);
        fread(&y, sizeof(uint8_t), 1, file);
        fread(&width, sizeof(uint8_t), 1, file);
        fread(&height, sizeof(uint8_t), 1, file);

        rooms[z].x = x ;
        rooms[z].y = y ;
        rooms[z].width = width ;
        rooms[z].height = height ;

    }  
    
    for(int y = 0 ; y < 21 ; y++)
    {
        for(int x = 0 ; x < 80; x++)
        {
            if(hardness[y][x] == 0)
            {
                if (isInRoom(x, y, *numRooms))
                {
                    dungeonMap[y][x] = '.' ;
                }
                else{
                    dungeonMap[y][x] = '#' ;
                }
            }
            else
            {
                dungeonMap[y][x] = ' ' ;
            }
        }
    }

    *numUpStairs = 0;
    *numDownStairs = 0;
    
    uint16_t upCount ;
    fread(&upCount, sizeof(uint16_t), 1, file) ;
    upCount = to_big_endian_16(upCount);

    for (int i = 0; i < upCount ; i++) {
        fread(&upStaircases[i].x, sizeof(uint8_t), 1, file);
        fread(&upStaircases[i].y, sizeof(uint8_t), 1, file);
        dungeonMap[upStaircases[i].y][upStaircases[i].x] = '<';
    }
    *numUpStairs = upCount ;

    uint16_t downCount;
    fread(&downCount, sizeof(uint16_t), 1, file);
    downCount = to_big_endian_16(downCount);

    for (int i = 0; i < downCount ; i++) {
        fread(&downStaircases[i].x, sizeof(uint8_t), 1, file);
        fread(&downStaircases[i].y, sizeof(uint8_t), 1, file);
        dungeonMap[downStaircases[i].y][downStaircases[i].x] = '>';
    }
    *numDownStairs = downCount ;

    if (dungeonMap[*playerY][*playerX] != '.' && dungeonMap[*playerY][*playerX] != '#') {
        *playerX = rooms[0].x + 1;
        *playerY = rooms[0].y + 1;
        dungeonMap[*playerY][*playerX] = '@';
    }
    else{
        dungeonMap[*playerY][*playerX] = '@';
    }
    fclose(file);

}

void saveDungeon(int hardness[21][80], int totalRooms, int numUpStairs, int numDownStairs)
{
    char *home = getenv("HOME");
    if (!home) {
        home = getenv("USERPROFILE");
    }
    if (!home) {
        fprintf(stderr, "Error: Could not find home directory.\n");
        exit(1);
    }

    char dirpath[512];
    snprintf(dirpath, sizeof(dirpath), "%s/.rlg327", home);

    char filename[512];
    if (snprintf(filename, sizeof(filename), "%s/dungeon", dirpath) >= (int)sizeof(filename))
    {
        fprintf(stderr, "Error: Dungeon filepath is too long! \n");
        return ;
    }

    ensure_directory_exists(dirpath);

    FILE *file = fopen(filename, "wb");
    if (!file) {
        perror("Error opening file for saving.");
        return;
    }


    fwrite(FILE_MARKER, 1, 12, file);

    uint32_t version = 0;
    fwrite(&version, sizeof(uint32_t), 1, file);

    uint32_t file_size = 1708 + (totalRooms * 4) + (numUpStairs * 2) + (numDownStairs * 2);
    file_size = to_big_endian_32(file_size);
    fwrite(&file_size, sizeof(uint32_t), 1, file);

    uint8_t pc_x = rooms[0].x + 1;
    uint8_t pc_y = rooms[0].y + 1;
    fwrite(&pc_x, sizeof(uint8_t), 1, file);
    fwrite(&pc_y, sizeof(uint8_t), 1, file);

    for (int y = 0; y < 21; y++) {
        for (int x = 0; x < 80; x++) {
            uint8_t hardness_value = (uint8_t)hardness[y][x];
            fwrite(&hardness_value, sizeof(uint8_t), 1, file);
        }
    }

    uint16_t num_rooms = to_big_endian_16(totalRooms);
    fwrite(&num_rooms, sizeof(uint16_t), 1, file);    

    for (int i = 0; i < totalRooms; i++) {
        uint8_t room_data[4] = {rooms[i].x, rooms[i].y, rooms[i].width, rooms[i].height};
        fwrite(room_data, sizeof(uint8_t), 4, file);
    }

    uint16_t upstair_count = to_big_endian_16(numUpStairs);
    fwrite(&upstair_count, sizeof(uint16_t), 1, file);

    for (int i = 0; i < numUpStairs; i++) {
        fwrite(&upStaircases[i].x, sizeof(uint8_t), 1, file);
        fwrite(&upStaircases[i].y, sizeof(uint8_t), 1, file);
    }

    uint16_t downstair_count = to_big_endian_16(numDownStairs);
    fwrite(&downstair_count, sizeof(uint16_t), 1, file);

    for (int i = 0; i < numDownStairs; i++) {
        fwrite(&downStaircases[i].x, sizeof(uint8_t), 1, file);
        fwrite(&downStaircases[i].y, sizeof(uint8_t), 1, file);
    }

    fclose(file);
}

void printMonsters(Monster monsters[], int numMonsters, int playerY, int playerX)
{
    int scroll = 0 ;
    int ch ;
    int aliveCount = 0 ;
    
    while (1)
    {
        clear();
        mvprintw(0, 0, "Monster List: Press Escape to Quit, Up & Down Arrows to Scroll");
        
        int line = 1 ;
        int displayed = 0 ;

        for(int i = 0; i < numMonsters; i++)
        {
            if (monsters[i].alive == false)
            {
                continue ;
            }

            aliveCount++ ;

            if (displayed < scroll)
            {
                displayed++ ;
                continue ;
            }
            if (line >= 22)
            {
                mvprintw(22, 0, "~~Press Down Arrow to Scroll Down~~");
                break ;
            }

            int dfpX = monsters[i].x - playerX ;
            int dfpY = monsters[i].y - playerY ;
            
            const char *dirY;
            const char *dirX;
            if(dfpY < 0)
            {
                dirY = "North" ;
            }
            else if (dfpY > 0)
            {
                dirY = "South" ;
            }
            else
            {
                dirY = "Same Row" ;
            }

            if(dfpX < 0)
            {
                dirX = "West" ;
            }
            else if (dfpX > 0)
            {
                dirX = "East" ;
            }
            else
            {
                dirX = "Same Column" ;
            }

            mvprintw(line, 0, "%c, %d %s and %d %s", monsters[i].symbol, abs(dfpY), dirY, abs(dfpX), dirX);
            line++ ;
            displayed++ ;
        }
    

        refresh();
        ch = getch();

        if(ch == 27)
        {
            break ;
        }
        else if(ch == KEY_DOWN && scroll + 1 < aliveCount)
        {
            scroll++ ;
        }
        else if(ch == KEY_UP && scroll > 0)
        {
            scroll-- ;
        }
    }
}

int main(int argc, char *argv[]) {
    srand(time(NULL)) ;

    initscr();             
    raw();                 
    keypad(stdscr, TRUE);  
    noecho();              
    curs_set(0);           


    char dungeonMap[21][80] ;
    int hardness[21][80] ;
    int distanceMapTunnel[21][80] ;
    int distanceMapNonTunnel[21][80] ;
    int playerX, playerY ;
    char pcLastTile = '.' ;

    generateHardness(hardness, dungeonMap);

    bool save = false ;
    bool load = false ;

    int numMonsters = NUM_MONSTERS ;
    

    for(int i = 1 ; i < argc; i++)
    {
        if (strcmp(argv[i], "--save") == 0)
        {
            save = true ;
        }
        else if (strcmp(argv[i], "--load") == 0)
        {
            load = true ;
        }
        else if (strcmp(argv[i], "--nummon") == 0)
        {
            numMonsters = atoi(argv[i+1]);
            if (numMonsters <=0 )
            {
                numMonsters = 10 ;
            }
        }
    }

    Monster monsters[numMonsters];

    int totalRooms, totalUpStaircases, totalDownStaircases ;

    if (load == true) 
    {
        loadDungeon(dungeonMap, hardness, &playerX, &playerY, &totalRooms, &totalUpStaircases, &totalDownStaircases) ;
        calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapNonTunnel, false);
        calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapTunnel, true);
        (void)totalUpStaircases;
        (void)totalDownStaircases;
    }
    else 
    {
        totalRooms = createRooms(dungeonMap, hardness);
        numUpStairs = createUpStaircases(dungeonMap, hardness, totalRooms) ;
        numDownStairs = createDownStaircases(dungeonMap, hardness, totalRooms) ; 
        calculatePath(dungeonMap, totalRooms, hardness) ;
        generatePlayerPosition(dungeonMap, totalRooms, &playerX, &playerY, &pcLastTile) ;
    }

    if (save == true)
    {
        saveDungeon(hardness, totalRooms, numUpStairs, numDownStairs) ;
    }

    createMonsters(dungeonMap, monsters, numMonsters, hardness);
    calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapNonTunnel, false);
    calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapTunnel, true);

    PriorityQueue pq ;
    pq.size = 0 ;

    Event pcTurn ;
    pcTurn.turnTime = 0 ;
    pcTurn.isPC = true ;
    pcTurn.index = -1 ;

    push(&pq, pcTurn) ;

    for(int i = 0 ; i < numMonsters ; i++)
    {
        int startTurn = 1000 / monsters[i].speed ;
        Event monsterTurn ;
        monsterTurn.turnTime = startTurn ;
        monsterTurn.isPC = false ;
        monsterTurn.index = i;
        push(&pq, monsterTurn) ;
    }

    int gameTime = 0 ;

    while (isEmpty(&pq) == false && gameTime < MAX_TURNS)
    {
        Event current = pop(&pq);

        gameTime = current.turnTime ;

        if(current.isPC)
        {
            drawDungeonMap(dungeonMap);
            int playerInput = getch();
            bool playerActed = false ;
            
            if (playerInput =='7' || playerInput == 'y')
            {
                movePlayer(dungeonMap, hardness, -1, -1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '8' || playerInput == 'k')
            {
                movePlayer(dungeonMap, hardness, -1, 0, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '9' || playerInput == 'u')
            {
                movePlayer(dungeonMap, hardness, -1, 1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '6' || playerInput == 'l')
            {
                movePlayer(dungeonMap, hardness, 0, 1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '3' || playerInput == 'n')
            {
                movePlayer(dungeonMap, hardness, 1, 1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '2' || playerInput == 'j')
            {
                movePlayer(dungeonMap, hardness, 1, 0, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '1' || playerInput == 'b')
            {
                movePlayer(dungeonMap, hardness, 1, -1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '4' || playerInput == 'h')
            {
                movePlayer(dungeonMap, hardness, 0, -1, &playerX, &playerY, &pcLastTile, monsters, numMonsters);
                playerActed = true;
            }
            else if (playerInput == '5' || playerInput == ' ' || playerInput == '.')
            {
                // do nothing
                playerActed = true;
            }
            else if (playerInput == 'm')
            {
                printMonsters(monsters, numMonsters, playerY, playerX);
            }
            else if (playerInput == '<' && pcLastTile == '<')
            {
                generateHardness(hardness, dungeonMap);
                totalRooms = createRooms(dungeonMap, hardness);
                numUpStairs = createUpStaircases(dungeonMap, hardness, totalRooms);
                numDownStairs = createDownStaircases(dungeonMap, hardness, totalRooms);
                calculatePath(dungeonMap, totalRooms, hardness);
                generatePlayerPosition(dungeonMap, totalRooms, &playerX, &playerY, &pcLastTile);
                createMonsters(dungeonMap, monsters, numMonsters, hardness);
            
                pq.size = 0;
            
                Event newPC;
                newPC.turnTime = current.turnTime;
                newPC.isPC = true;
                newPC.index = -1;
                push(&pq, newPC);
            
                for (int i = 0; i < numMonsters; i++) {
                    Event monsterTurn;
                    monsterTurn.turnTime = newPC.turnTime + (1000 / monsters[i].speed);
                    monsterTurn.isPC = false;
                    monsterTurn.index = i;
                    push(&pq, monsterTurn);
                }
            
                playerActed = true;
            }
            else if (playerInput == '>' && pcLastTile == '>')
            {
                generateHardness(hardness, dungeonMap);
                totalRooms = createRooms(dungeonMap, hardness);
                numUpStairs = createUpStaircases(dungeonMap, hardness, totalRooms);
                numDownStairs = createDownStaircases(dungeonMap, hardness, totalRooms);
                calculatePath(dungeonMap, totalRooms, hardness);
                generatePlayerPosition(dungeonMap, totalRooms, &playerX, &playerY, &pcLastTile);
                createMonsters(dungeonMap, monsters, numMonsters, hardness);
            
                pq.size = 0;
            
                Event newPC;
                newPC.turnTime = current.turnTime;
                newPC.isPC = true;
                newPC.index = -1;
                push(&pq, newPC);
            
                for (int i = 0; i < numMonsters; i++) {
                    Event monsterTurn;
                    monsterTurn.turnTime = newPC.turnTime + (1000 / monsters[i].speed);
                    monsterTurn.isPC = false;
                    monsterTurn.index = i;
                    push(&pq, monsterTurn);
                }
            
                playerActed = true;
            }
            
            else if (playerInput == 'Q')
            {
                endwin() ;
                exit(0);
            }

            if(playerActed == true)
            {
                calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapNonTunnel, false);
                calculateDistanceMap(dungeonMap, hardness, playerX, playerY, distanceMapTunnel, true);
        
                if (!(pcLastTile == '<' && playerInput == '<') && !(pcLastTile == '>' && playerInput == '>'))
                {
                    int entitySpeed = 10; 
                    current.turnTime += (1000 / entitySpeed);
                    push(&pq, current);
                }
            }
        }
        else
        {
            if(monsters[current.index].alive == true)
            {
                moveMonster(dungeonMap, hardness, &monsters[current.index], playerX, playerY);
            }
        }

        int aliveMonsters = 0 ;
        for(int i = 0 ; i < numMonsters ; i++)
        {
            if (monsters[i].alive == true)
            {
                aliveMonsters++ ;
            }
        }
        if (aliveMonsters == 0)
        {
            printf("\n All monsters have been slain, PC has won the game! Winner, winner, chicken dinner! \n");
            exit(0);
        }

        int monsterEntitySpeed = monsters[current.index].speed;  
        current.turnTime += (1000 / monsterEntitySpeed);
        push(&pq, current);

        usleep(10);
    }

    printf("\nGame Over! Time has run out, and the PC survives!\n");

    endwin();
    return 0 ;
}