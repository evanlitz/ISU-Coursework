# Evan Litzer             11/27/2022
# Assignment #6 Naval Battle

import gameBoard
import gamePlay

def main():
    """This is the main function of the game. It controls the flow/ execution of the entire script.
    """
    gameOver = False

    gameboardChoice = 0
    humanGameBoard = None
    targetBoard = None
    computerGameBoard = None
    
    numHumanTargets = 0
    numComputerTargets = 0
    
    print("Welcome to Naval Battle!")
    print()
    
    print("By: Evan Litzer")
    print("[COM S 127 B]")
    print()

    while gameOver == False:
        choice = input("[p]lay, [i]nstructions, or [q]uit?: ")
        print()
        if choice == "p": 
            gameboardChoice = gameBoard.chooseHumanGameBoard()
            pass
            humanGameBoard, numHumanTargets = gameBoard.loadGameBoard(gameboardChoice)
            pass
            gameboardChoice = gameBoard.chooseComputerGameBoard()
            pass
            computerGameBoard, numComputerTargets = gameBoard.loadGameBoard(gameboardChoice)
            pass
            targetBoard = gameBoard.loadTargetBoard()
            pass
            gamePlay.runGame(humanGameBoard, targetBoard, computerGameBoard, numHumanTargets, numComputerTargets)
        elif choice == "i":
            print("Enter a row and column to fire on the ships of the COMPUTER!")
            print("Destroy all of the COMPUTER's ships before it destroys yours!")
            pass
        elif choice == "q":
            gameOver = True
            print("GOODBYE!")
            pass
        else:
            print()
            print("Please enter [p], [i], or [q]...")
            print()

if __name__ == "__main__":
    main()