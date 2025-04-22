Main function takes input in for puzzleSize and words, which are error-handled. [20][20] 2D character array named grid contains the letters in the wordsearch. 
Grid is first filled with periods as default, then inputted words are iterated through and are used as parameter to call InsertWord function. 
Once in InsertWord, wordLength is noted. A position array that represents every possible position of the wordsearch grid is then initialized, 
with the 0th element being the row and the 1st being the column.
This position array is then shuffled randomly to make the word placement sporatic. This is done by mixing the row and column values for the position array.
Then the direction array is used to distinguish between how a word is inserted into the puzzle. This direction array is also shuffled randomly.
Position and dirtection array are then iterated through, with each direction applying to all of the positions in the grid. 
Based on which direction is chosen, the next square is then error checked. Since both arrays were shuffled, the iteration is random.
The tempPositions array is filled with the valid positions for the word placement. 
If the position with the direction is then found to be valid, then the word is placed into the grid based on the outlined squares in tempPositions.
The insertWord function returns 1 if the word is placed and 0 is it could not be placed. 
If main reads in a 0 from insertWord, then an error message is produced and no grid is returned.
After that, the grid is iterated through and checked for default values. They are then replaced with a random letter character.
The grid is then printed before the words hidden in the grid are printed below it. Finally main returns 0.