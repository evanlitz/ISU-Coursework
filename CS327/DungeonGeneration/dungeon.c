/*
    @Author Evan Litzer
    Feburary 5th, 2025
    Dungeon.c
*/


#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>

#define MIN_ROOMS 6
#define MAX_ROOMS 8
#define MAX_ROOM_X_SIZE 15
#define MIN_ROOM_X_SIZE 4
#define MAX_ROOM_Y_SIZE 6
#define MIN_ROOM_Y_SIZE 3
#define MAX_STAIRCASE_DOWN 2
#define MAX_STAIRCASE_UP 2

#define DUNGEON_WIDTH 80
#define DUNGEON_HEIGHT 21
#define FILE_MARKER "RLG327-S2025"
#define FILE_VERSION 0

typedef struct {
    int x, y;
    int width, height;
} Room;

Room rooms[MAX_ROOMS] ;

int createRooms(char dungeonMap[21][80], int hardness[21][80])
{
    int attempts = 1 ;
    int totalRooms = (rand() % (MAX_ROOMS - MIN_ROOMS + 1)) + MIN_ROOMS ;
    for (int i = 0 ; i < totalRooms ; i++)
    {
        int placed = 0 ;
        while (placed == 0)
        {   
            attempts++;
            int roomWidth = (rand() % (MAX_ROOM_X_SIZE - MIN_ROOM_X_SIZE + 1)) + MIN_ROOM_X_SIZE ;
            int roomHeight = (rand() % (MAX_ROOM_Y_SIZE - MIN_ROOM_Y_SIZE + 1)) + MIN_ROOM_Y_SIZE ;
            int roomX = rand() % (78 - roomWidth - 1 - 1) + 1 ;
            int roomY = rand() % (19 - roomHeight - 1 - 1) + 1 ;

            bool validPlacement = true ;
            for (int y = roomY - 1 ; y <= roomY + roomHeight ; y++)
            {
                for (int x = roomX - 1 ; x <= roomX + roomWidth ; x++)
                {
                    if (x<=0 || x >= 79 || y <= 0 ||  y >= 20)
                    {
                        validPlacement = false ;
                        break ;
                    }
                    if (dungeonMap[y][x] == '.')
                    {
                        validPlacement = false ;
                        break ;
                    }
                }
                if (validPlacement == false)
                {
                    break ;
                }
            }


            if (validPlacement == false)
            {
                continue ;
            } 

            rooms[i] = (Room){roomX, roomY, roomWidth, roomHeight};

            for(int y = roomY ; y < roomY + roomHeight ; y++)
            {
                for(int x = roomX; x < roomX + roomWidth ; x++)
                {
                    dungeonMap[y][x] = '.' ;
                    hardness[y][x] = 0 ;
                }
            }

            placed = 1 ;
    
        }

    }

    return totalRooms ;

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
            hardness[stairY][stairX] = 2 ;
            upstairsAmount++ ;
        }
    }

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
            hardness[stairY][stairX] = 3 ;
            downstairsAmount++ ;
        }
    }

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
            hardness[y][x] = 1 ;
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


void printDungeonMap(char dungeonMap[21][80]) {
    for (int y = 0; y < 21; y++) {
        for (int x = 0; x < 80; x++) {
            printf("%c", dungeonMap[y][x]);
        }
        printf("\n");
    }
}

void printHardness(int hardness[21][80]) {
    for (int y = 0; y < 21; y++) {
        for (int x = 0; x < 80; x++) {
            printf("%3d ", hardness[y][x]);
        }
        printf("\n");
    }
}

// void saveGame(char dungeonMap[21][80], int totalRooms, int totalUpcases, int totalDowncases);


int main() {
    srand(time(NULL)) ;
    char dungeonMap[21][80] ;
    int hardness[21][80] ;

    for (int y = 0 ; y < 21 ; y++)
    {
        for (int x = 0 ; x < 80 ; x++)
        {
            dungeonMap[y][x] = ' ' ;
            hardness[y][x] = 255 ;
        }
    }

    int totalRooms = createRooms(dungeonMap, hardness);

    int totalUpStaircases = createUpStaircases(dungeonMap, hardness, totalRooms) ;

    int totalDownStaircases = createDownStaircases(dungeonMap, hardness, totalRooms) ;

    calculatePath(dungeonMap, totalRooms, hardness) ;

    printDungeonMap(dungeonMap); 

    printf("Printing hardness map:\n");
    printHardness(hardness);
    
    return 0 ;
}