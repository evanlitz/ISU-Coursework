# Matthew Holman             8-11-2022
# Assignment #6 Naval Battle

import gameBoard
import gameInput

def _humanTurn(humanGameBoard, targetBoard, computerGameBoard, numComputerTargets):
    """This function controls what happens when it is the human's turn.

    Args:
        humanGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.

        targetBoard (list of lists): Contains the 'top part' of the gameboard - where the hits/ misses against the computer go. 
        Only the human needs one.

        computerGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.

        numComputerTargets (int): The number of computer targets remaining.
    
    Returns:
        list of lists, list of lists, list of lists, int: All of the relevant gameboards and the number of computer targets remaining.
    """

    ten = 10
    print("HUMAN'S TURN!")
    gameBoard.printBoard(targetBoard, ten, ten) # game board?
    gameBoard.printBoard(humanGameBoard, ten, ten) # target board?
    # use gameboard print function
    pass

    
    while True :
        try :
            row, col = gameInput.getHumanInput() 
        except :
            continue
        if targetBoard[row][col] == "X" or targetBoard[row][col] == "O" :
                print("Square has already been attacked! Please enter another input!")
                continue
        else :
            break

    pass
    print("The coordinates the human is targeting is [", row, ",", col, "]." )
    pass
    if computerGameBoard[row][col] == "@" :
        computerGameBoard[row][col] = "X"
        targetBoard[row][col] = "X"
        print("HIT!")
        numComputerTargets -= 1
    else :
        computerGameBoard[row][col] = "O"
        targetBoard[row][col] = "O"
        print("MISS!")
    pass
    
    return humanGameBoard, targetBoard, computerGameBoard, numComputerTargets

def _computerTurn(humanGameBoard, numHumanTargets):
    """This function controls what happens when it is the computer's turn.

    Args:
        humanGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.

        numHumanTargets (int): The number of human targets remaining.
    
    Returns:
        list of lists, int: All of the relevant gameboards and the number of human targets remaining.
    """
    print("COMPUTER'S TURN!")
    pass

    while True :
        try :
            row, col = gameInput.getComputerInput()
        except :
            continue
        if humanGameBoard[row][col] == "X" or humanGameBoard[row][col] == "O" :
            continue
        else :
            break
    pass

    print("The coordinates the COMPUTER is targeting is [", row, ",", col, "].")
    pass

    if humanGameBoard[row][col] == "@" :
        humanGameBoard[row][col] = "X"
        numHumanTargets -= 1
        print("HIT!")
    else :
        humanGameBoard[row][col] = "O"
        print("MISS!")
    pass
    
    return humanGameBoard, numHumanTargets

def _printWinner(numComputerTargets, computerGameBoard):
    """This function prints out which player has won the game, depending on the numComputerTargets remaining.

    Args:
        numComputerTargets (int): The number of computer targets left. If there are none, the human wins. Else - the computer wins.

        computerGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.
    """

    if numComputerTargets == 0 :
        print("THE HUMAN HAS WON!")
    else :
        print("THE COMPUTER HAS WON!")
    pass
    

    ten = 10
    gameBoard.printBoard(computerGameBoard, ten, ten) # ??????
    pass

    return

def runGame(humanGameBoard, targetBoard, computerGameBoard, numHumanTargets, numComputerTargets):
    """This function controls the flow of the game and switches turns between the human and the computer.

    Args:
        humanGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.

        targetBoard (list of lists): Contains the 'top part' of the gameboard - where the hits/ misses against the computer go. 
        Only the human needs one.

        computerGameBoard (list of lists): Contains the 'bottom part' of the gameboard - where the 'ships' are placed.

        numHumanTargets (int): The number of human targets left.

        numComputerTargets (int): The number of computer targets left.
    """
    currentTurn = 0 # 0 = human, 1 = computer

    # play the game (HUMAN goes first)
    while numHumanTargets > 0 and numComputerTargets > 0:
        if currentTurn == 0:
            humanGameBoard, targetBoard, computerGameBoard, numComputerTargets = _humanTurn(humanGameBoard, targetBoard, computerGameBoard, numComputerTargets)
        else:
            humanGameBoard, numHumanTargets = _computerTurn(humanGameBoard, numHumanTargets)

        # switch whose turn it is
        currentTurn += 1
        currentTurn %= 2
    
    # print the winner once the game is over
    _printWinner(numComputerTargets, computerGameBoard)

    return