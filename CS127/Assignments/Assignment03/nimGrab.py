# Evan Litzer             October 3rd, 2022
# Assignment 3

# randint
# https://docs.python.org/3/library/random.html
import random 

print("Welcome to NIMGRAB!")
print()

print("By: Evan Litzer")
print("[COM S 127 Section B]")
print()

# Constant values
NUM_ITEMS_LOW = 4
NUM_ITEMS_HIGH = 8
NUM_TO_TAKE_LOW = 1
NUM_TO_TAKE_HIGH = 3

# Game flow variables
gameOver = False
currentTurn = 0 # 0 = human, 1 = computer NOTE: Alternate between turns 0 and 1 to play the game

# initial loop tasks ------------------------------------------------------------------------------------------------------------------------
while gameOver == False :
    choice = str(input("[p]lay, [i]nstructions, [q]uit?: "))
    if choice == "p" :
        number = random.randint(NUM_ITEMS_LOW, NUM_ITEMS_HIGH)
        while number > 0 :      
            if currentTurn == 0 :
                print("HUMAN TURN: ")
                print("There are currently", number, "items in the itempool")
                counter = 0 
                while counter < number :
                    print("|", end = "")
                    counter += 1
                print()
                take = False
                while not take or take not in list(range(NUM_TO_TAKE_LOW, NUM_TO_TAKE_HIGH + 1)):
                    try :
                     take = int(input("How many will you take?, ({0} - {1}):".format(NUM_TO_TAKE_LOW, NUM_TO_TAKE_HIGH)))                
                    except:
                     print("Please enter a number between", NUM_TO_TAKE_LOW, "and", NUM_TO_TAKE_HIGH)
                print("The human has taken", take, "items...")
                number -= take
            elif currentTurn == 1 :
                print("COMPUTER TURN: ")
                print("There are currently", number, "items in the itempool")
                counter = 0 
                while counter < number :
                    print("|", end = "")
                    counter += 1
                print()
                take = random.randint(NUM_TO_TAKE_LOW, NUM_TO_TAKE_HIGH)
                if number == 1 :
                    take = 1 
                elif number > 1 :
                    while(take >= number) :
                        take = random.randint(NUM_TO_TAKE_LOW, NUM_TO_TAKE_HIGH)
                print("The computer has taken", take, "items...")
                number -= take
            currentTurn += 1
            currentTurn = currentTurn % 2
        if number <= 0 :
            if currentTurn == 0 :
                print("The COMPUTER has taken the last item... Therefore, the HUMAN has won!")
            elif currentTurn == 1 :
                print("The HUMAN has taken the last item... Therefore, the COMPUTER has won!")
        currentTurn = 0






    elif choice == "i" :
        print("Each player, the human and the computer, take turns removing objects from a random pool.")
        print("Each player can remove between", NUM_TO_TAKE_LOW, "and", NUM_TO_TAKE_HIGH, "items total")
        print("The game progresses until the last item is removed from the pool.")
        print("The player to take the last item loses the game.")
        print("In this instance, the player will be paired against the computer. GOOD LUCK!")
    elif choice == "q" :
        gameOver = True
        print("Goodbye!")
    else :
        print("Please enter [p], [q], or [i]...")

# ---------------------------------------------------------------------------------------------------------------------------------------------


# ENDING THE GAME ------------------




# TODO: outside the 'if/ else' statement create above, set currentTurn to be zero (0). This will be at the same indentation level as the 'if/ else' statement and the 'gameplay' 'while loop'. This will ensure that the human will always go first in the event they start a new game.

# ---------------------------------------------------------------------------------------------------------------------------------------------
