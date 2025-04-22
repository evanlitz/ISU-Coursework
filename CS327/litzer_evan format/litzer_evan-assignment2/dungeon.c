/*
    @Author Evan Litzer
    Feburary 12th, 2025
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
#define MAX_ROOMS 12
#define MAX_ROOM_X_SIZE 15
#define MIN_ROOM_X_SIZE 2
#define MAX_ROOM_Y_SIZE 15
#define MIN_ROOM_Y_SIZE 2
#define MAX_STAIRCASE_DOWN 5
#define MAX_STAIRCASE_UP 5

#define DUNGEON_WIDTH 80
#define DUNGEON_HEIGHT 21
#define FILE_MARKER "RLG327-S2025"
#define FILE_VERSION 0
#define DUNGEON_PATH "/.rlg327/dungeon"


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

void saveDungeon(char dungeonMap[21][80], int hardness[21][80], int totalRooms, int numUpStairs, int numDownStairs)
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
    if (snprintf(filename, sizeof(filename), "%s/dungeon", dirpath) >= sizeof(filename))
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

int main(int argc, char *argv[]) {
    srand(time(NULL)) ;
    char dungeonMap[21][80] ;
    int hardness[21][80] ;
    int playerX, playerY ;

    for (int y = 0 ; y < 21 ; y++)
    {
        for (int x = 0 ; x < 80 ; x++)
        {
            dungeonMap[y][x] = ' ' ;
            hardness[y][x] = 255 ;
        }
    }

    bool save = false ;
    bool load = false ;

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
    }

    int totalRooms, totalUpStaircases, totalDownStaircases ;

    if (load == true) 
    {
        loadDungeon(dungeonMap, hardness, &playerX, &playerY, &totalRooms, &numUpStairs, &numDownStairs) ;
        (void)totalUpStaircases;
        (void)totalDownStaircases;
    }
    else 
    {
        totalRooms = createRooms(dungeonMap, hardness);
        numUpStairs = createUpStaircases(dungeonMap, hardness, totalRooms) ;
        numDownStairs = createDownStaircases(dungeonMap, hardness, totalRooms) ; 
        calculatePath(dungeonMap, totalRooms, hardness) ;
    }

    printDungeonMap(dungeonMap); 



    if (save == true)
    {
        saveDungeon(dungeonMap, hardness, totalRooms, numUpStairs, numDownStairs) ;
    }
    
    return 0 ;
}