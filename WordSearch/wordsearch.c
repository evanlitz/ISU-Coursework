/*
@Author Evan Litzer
1/28/2025 
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PUZZLE_SIZE 20
#define MAX_WORDS 150


int insertWord(char grid[MAX_PUZZLE_SIZE][MAX_PUZZLE_SIZE], int puzzleSize, char *word) 
{
    int wordLength = strlen(word) ;
    int positions[puzzleSize * puzzleSize][2] ;
    int positionItr = 0 ;

    for (int row = 0; row < puzzleSize; row++) 
    {
        for (int col = 0; col < puzzleSize; col++) 
        {
            positions[positionItr][0] = row;
            positions[positionItr][1] = col;
            positionItr++;
        }
    }

    for (int i = 0; i < positionItr - 1; i++) 
    {
        int range = positionItr - i;
        int randomNum = rand() % range;
        int k ;
        int j = i + randomNum;
        int tempRow = positions[i][0];
        int tempCol = positions[i][1];
        positions[i][0] = positions[j][0];
        positions[i][1] = positions[j][1];
        positions[j][0] = tempRow;
        positions[j][1] = tempCol;
    }

    int directions[4] = {0, 1, 2, 3};
    for (int i = 0; i < 3; i++) 
    {
        int j = i + rand() % (4 - i);
        int temp = directions[i];
        directions[i] = directions[j];
        directions[j] = temp;
    }

    for (int p = 0; p < positionItr; p++) 
    {
        int row = positions[p][0];
        int col = positions[p][1];

        for (int d = 0; d < 4; d++) 
        {
            int compass = directions[d];
            int valid = 1;

            int tempPositions[wordLength][2];
            for (int i = 0; i < wordLength; i++) 
            {
                int newRow = row, newCol = col;

                if (compass == 0) 
                { // Diagonal Up
                    newRow -= i;
                    newCol += i;
                } else if (compass == 1) 
                { // Rightward
                    newCol += i;
                } else if (compass == 2) 
                { // Diagonal Down
                    newRow += i;
                    newCol += i;
                } else if (compass == 3) 
                { // Downward
                    newRow += i;
                }

                tempPositions[i][0] = newRow;
                tempPositions[i][1] = newCol;

                if (newRow < 0 || newRow >= puzzleSize || newCol < 0 || newCol >= puzzleSize || (grid[newRow][newCol] != '.' && grid[newRow][newCol] != word[i])) 
                {
                    valid = 0;
                    break;
                }
            }

            if (valid == 1) 
            {
                for (int i = 0; i < wordLength; i++) 
                {
                    int finalRow = tempPositions[i][0];
                    int finalCol = tempPositions[i][1];
                    grid[finalRow][finalCol] = word[i];
                }
                return 1; // Word placed
            }
        }
    }

    return 0; // Word not placed

}




int main(int argc, char *argv[])
{
    int puzzleSize = atoi(argv[1]);
    char grid[MAX_PUZZLE_SIZE][MAX_PUZZLE_SIZE];
    int numWords = argc - 2;
    char *words[MAX_WORDS];
    int wordCount = 0 ;


    for (int i = 2; i < argc; i++) {
        words[i - 2] = argv[i]; 
        wordCount++ ;
    }

    if(puzzleSize > 20 || puzzleSize < 1)
    {
        printf("Invalid puzzle size\n");
        return 0;
    }

    for (int x = 0 ; x < puzzleSize ; x++)
    {
        for (int y = 0 ; y < puzzleSize ; y++)
        {
            grid[x][y] = '.' ;
        }
    }

    for (int i = 2; i < argc; i++) 
    {
        if (!insertWord(grid, puzzleSize, argv[i])) 
        {
            printf("Failed to place word: %s\n", argv[i]);
            printf("Please try entering valid words with a corresponding valid puzzle size.") ;

            return 0 ;
        }
    }



    for (int x = 0 ; x < puzzleSize ; x++)
    {
        for (int y = 0 ; y < puzzleSize ; y++)
        {
            if (grid[x][y] == '.')
            {
                grid[x][y] = 'a' + rand() % 26;
            }
        }
    }


    for (int x = 0; x < puzzleSize; x++) 
    {
        for (int y = 0; y < puzzleSize; y++) 
        {
            printf("%c ", grid[x][y]);
        }
        printf("\n");
    }

    printf("\n");
    printf("%s ", "Words to Find: ");


    for (int y = 0; y < wordCount; y++) 
        {
            printf("%s ", words[y]);
            printf("%s ", "");

        }
        printf("\n");
    


    return 0 ;
}


