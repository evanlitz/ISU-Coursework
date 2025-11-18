# Evan Litzer            11-27-2022
# Assignment #6 Naval Battle

import random
import gameBoard

def getHumanInput():
    """This function takes in input from the human for wich row and column they want to attack.

    Returns:
        int, int: row and col are the integer values designating the row and column for the human to attack.
    """
    while True :
        try :
            row = int(input("Enter an integer: "))
        except ValueError :
            print("Please enter an INTEGER!")
            continue
        if row < 0 or row > gameBoard.GAME_BOARD_HEIGHT-1 :
            print("INVALID INPUT: Please enter a valid integer for the row value.")
            continue
        else :
            break
    pass


    while True :
        try :
            col = int(input("Enter an integer: "))
        except ValueError :
            print("Please enter an INTEGER!")
            continue
        if col < 0 or col > gameBoard.GAME_BOARD_HEIGHT-1 :
            print("INVALID INPUT: Please enter a valid number.")
            continue
        else :
            break
    pass


    return row, col

def getComputerInput():
    """This function randomly generates input from the computer for which row and column it wants to attack.

    Returns:
        int, int: row and col are the integer values designating the row and column for the computer to attack.
    """
    row = random.randint(0, gameBoard.GAME_BOARD_WIDTH - 1)
    pass
    col = random.randint(0, gameBoard.GAME_BOARD_WIDTH - 1)
    pass
    return row, col