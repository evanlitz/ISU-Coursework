# Evan Litzer             October 10th, 2022
# Assignment 4 - Dungeon Crawl

import random
import sys

# GLOBAL CONSTANT VARIABLES
START_ROOM = 1
FINAL_ROOM = 9999

# Functions to represent dungeon rooms
# NOTE: You can change the number/ order of parameters being used in your room functions to fit the needs of your game.
def cavern(goldAmount, visited_room, playerHealth, maxHealth, playerAccuracy, playerDamage, currentRoom):
    currentRoom == "CAVERN"
    combatChance = random.randint(1,9)
    combat(combatChance, playerHealth, maxHealth, playerAccuracy, playerDamage)
    
    
    
    print()
def forest(goldAmount, visited_room, playerTotalHealth, playerCurrentHealth, playerDamage):
    


    print()
def temple(goldAmount, visited_room, playerTotalHealth, playerCurrentHealth, playerDamage):
    story(currentRoom, visited_room1)
    
    visited_room1 = True
    print()
def village(goldAmount, visited_room, playerTotalHealth, playerCurrentHealth, playerDamage):
    story(currentRoom, visited_room2)

    visited_room2 = True
    print()




def story(currentRoom, visited_room) :
    if currentRoom == "TEMPLE" & visited_room == False :
        print("Welcome to the mighty temple! This ancient wonder was constructed by the primitive Jangolorians thousands of years ago! Wisely left untouched until now, you will be the first to explore its crevices, as it definitiely contains valuable and shiny gold for your taking. Watch out for the spirit monsters, who will be defending the temple at every corner.")
    elif currentRoom == "VILLAGE" & visited_room == False :
        print("Welcome to the village! This abandoned settlement once was the capital and focal point of the Jangolorians. On one terrible day though, thousands died from the hands of the monsters as they were swiftly overrun and anillhated by the beasts. Lots of gold will be seemingly everywhere, as many citizens were murdered with their wealth as they attempted to escape. Monsters still do roam around here, waiting for their loved ones to return, plating them a delicious snack.")
        
        


def combat(combatChance, playerHealth, maxHealth, playerAccuracy, playerDamage):
    enemyName = ""
    enemyHealth = 0
    enemyAccuracy = 0
    enemyDamage = 0
# Check to see if we should engage in combat
    if combatChance > random.randint(0, 9):
        print("You have engaged in combat!")
        print()
# Randomly select an enemy
        monsterSelection = random.randint(0, 0)
        if monsterSelection == 0: # SLIME monster
            enemyName = "SLIME"
            maxEnemyHealth = 2
            enemyHealth = maxEnemyHealth
            enemyAccuracy = 5
            enemyDamage = 1
            print("You have encountered an enemy {0} monster...".format(enemyName))
            print()
            print("It has {0} HP and {1} ATTACK strength...".format(enemyHealth, enemyDamage))
            print()
        else:
            print("Error - 'combat' function: 'monsterSelection' value is invalid:", monsterSelection)
# Choose a random turn to go first
        currentTurn = random.randint(0, 1)
        if currentTurn == 0:
            print("You have taken the initiative!")
        else:
            print("The enemy {0} monster has struck first!".format(enemyName))
        print()
# Take turns
        while playerHealth > 0 and enemyHealth > 0:
            if currentTurn == 0: # Human Turn
# Get the action the human wants to take
                action = input("COMBAT: [a]ttack, [f]lee: ")
                while action != "a" and action != "f":
                    print("Invalid combat choice...")
                    action = input("COMBAT: [a]ttack, [f]lee: ")
                print()
# Engage in combat depending on the action
                if action == "a":
                    if random.randint(0, 9) < playerAccuracy:
                        enemyHealth -= playerDamage
                        print("You have HIT the enemy monster! Its HP is: {0} / {1}".format(enemyHealth, maxEnemyHealth))
                        print()
                    else:
                        print("You have MISSED the enemy monster...")
                        print()
                elif action == "f":
                    if random.randint(0, 9) < playerDamage:
                        print("You have escaped from combat!")
                        print()
                        break
                else:
                    print("Error - 'combat' function: 'action' value is invalid:", action)
            else: # Computer Turn
                if random.randint(0, 9) < enemyAccuracy:
                    playerHealth -= enemyDamage
                    print("You have been HIT by the the enemy {0} monster! Your HP is: {1} / {2}".format(enemyName, playerHealth, maxHealth))
                    print()
                else:
                    print("The enemy {0} monster has MISSED you...".format(enemyName))
                    print()
# switch turns
            currentTurn += 1
            currentTurn %= 2
# Announce the winner
        if playerHealth > 0 and enemyHealth <= 0:
            print("Congratulations! You have defeated the enemy {0} monster...".format(enemyName))
            print()
        elif playerHealth > 0 and enemyHealth > 0:
            print("That was a close one! The enemy {0} monster almost got you!".format(enemyName))
            print()
        else:
            print("Sadly, the enemy {0} monster was victorious...".format(enemyName))
            print()
    else:
        print("Fortunately, there were no monsters in this room...")
        print()
    return playerHealth


def shop(goldAmount, playerHealth, maxHealth, playerDamage, playerAccuracy) :
    catalog = ["Strength Boost", "Smelted Armor", "Healing Potion", "Eye of Hercules", "Heart of Cupid", "Lightning Bolt"]
    catalogprices = [20, 25, 10, 50, 50, 1000]
    print("Welcome to the shop! Run by goblins, we have any item you'd need for combat upgrades! Just take a look at our catalog!")
    print()
    counter = len(catalog) - 1
    while counter >= 0 :
        print(catalog[counter], "-------", catalogprices[counter], "------- id: ", counter)
        counter -= 1
    choice = 

    
    
    # TODO: Create a function which implements a simple 'shop' for the player to pay some amount of gold to restore their health.
    # Not every room has to have a shop. (1 pt.)
    #
    # HINT: You can accomplish this any way you want - use your imagination. However, it will have to print out/ take input for
    # whatever you want to have happen.
    #
    # HINT: Perhaps players can also pay gold to upgrade their maximum possible health or their attack power.
    #
    # HINT: Whatever stats for shopping you want to implement should likelyh exist inside the 'shop' function.
    #
    # HINT: Your 'shop' function can, itself, call other sub-functions as well.

    # TODO: Create a function which accepts parameters representing the player's 'goldAmount' value, a 'gold' value representing 
    # the amount of gold that the room contains, and a boolean flag indicating whether the room has been visited or not. 
    #
    # This function will operate in a manner similar to the code below, and should return the new 'goldAmount' value that the 
    # player has after adding the gold from the room to their total 'goldAmount'. It should also mark the 'room visited' boolean 
    # flag as 'True', and return that value as well. When returning, assign the new amount of gold to the 'goldAmount' variable, and
    # assign the 'room visited' return value to the 'visited_room' variable. If the room has already been visited before, print
    # out a string indicating this. 
    #
    # This function should be used in all subsequent room functions. (1 pt.)
    #
    # HINT: If the player's health is less than zero, they shouldn't be able to visit rooms anymore.
    #
    # HINT: Study how the 'visited_room' variable is returned at the bottom of this function, and how it interacts with the 
    # 'visited_roomX' variables in the main() function.
    if visited_room == False:
        gold = 10 # This is the amount of gold the room contains.
    
        print()
        print("The room has", gold, "gold pieces in it...")
        goldAmount += gold
        print("After taking the gold, you currently have", goldAmount, "gold pieces in your posession...")
        print()

        # Mark the room as 'visited'
        visited_room = True
    else:
        print()
        print("You have already visited this room before...")
        print()

    # TODO: Create a function which takes in input for the directions the player can go in the dungeon.
    # This function will control how the player moves around the dungeon.
    # This function should replace the following code below this TODO and before the 'return' statement.
    # This function should be used in all subsequent room functions. 
    # This function should return a valid 'roomChoice' value. (1 pt.)
    #
    # HINT: You can do this any way you want. However, it might be an easy solution to take in arguments that 
    # specify valid directions for the player to move, and which rooms they can move to.
    # For example, arguments for N, S, E, W => 2, -1, 3, -1 might allow the player to move north to room 2, 
    # and east to room 3. The values of -1 indicate that the player cannot move that direction.
    #
    # HINT: If you want to give the player fewer than four directions to go, how would you accomplish this in the command print-out? 
    # There are multiple ways to go about this. You don't have to print all the commands on one line. Perhaps you could print out 
    # each command on a different line, and then have the final prompt for the 'input' function just read "What is our choice?: " 
    # or something like that.
    #
    # HINT: If the player's health is less than zero, they shouldn't be able to move to different rooms anymore.
    direction = input("[n] [s] [e] [w]?: ")
    while direction != "n" and direction != "s" and direction != "e" and direction != "w":
        print("Invalid input...")
        direction = input("[n] [s] [e] [w]?: ")
    
    roomChoice = -1 # HINT: Once this section is encapsulated into a function, it would be wise to have a default roomChoice value outside that function.
    if direction == "n":
        roomChoice = 2
    elif direction == "s":
        roomChoice = 2
    elif direction == "e":
        roomChoice = 2
    elif direction == "w":
        roomChoice = 2
    
    # NOTE: You can change the number/ order of variables being returned to fit the needs of your game.
    return roomChoice, goldAmount, visited_room

# NOTE: You can change the number/ order of parameters being used in your room functions to fit the needs of your game.
def room2(goldAmount, visited_room):
    # NOTE: If your room uses a shop/ combat function, it should likely be placed at the top of the room function it appears in.

    # NOTE: Replace this portion of code with the 'room visited'/ 'gold amount' function created in the 'room1' function above.
    if visited_room == False:
        gold = 20 # This is the amount of gold the room contains.

        print()
        print("The room has", gold, "gold pieces in it...")
        goldAmount += gold
        print("After taking the gold, you currently have", goldAmount, "gold pieces in your posession...")
        print()

        visited_room = True
    else:
        print()
        print("You have already visited this room before...")
        print()

    # NOTE: Replace this code before the 'return' statement with the 'direction' function created in the 'room1' function above.
    direction = input("[n] [s]?: ")
    while direction != "n" and direction != "s":
        print("Invalid input...")
        direction = input("[n] [s]?: ")
    
    roomChoice = -1
    if direction == "n":
        roomChoice = FINAL_ROOM
    elif direction == "s":
        roomChoice = 1

    # NOTE: You can change the number/ order of variables being returned to fit the needs of your game.
    return roomChoice, goldAmount, visited_room

# Main function
def main():
    # Set to 'True' when the game is over.
    gameOver = False

    # Player status variables/ constants. 
    playerHealth = 100
    maxHealth = 100
    playerDamage = 2
    playerAccuarcy = 5

    # HINT: If you have other player variables to use, such as health, damage, etc. add them here.
    START_GOLD = 0 # HINT: This is a 'constant' value. Notice how it is used to set/ reset the goldAmount value.
    goldAmount = START_GOLD
    currentRoom = START_ROOM
    visited_room1 = False # HINT: Carefully study how these 'visited room' variables are used.
    visited_room2 = False
    visited_room3 = False
    visited_room4 = False

    print("Welcome to Dungeon Crawl...")
    print()

    print("By: Evan Litzer")
    print("[COM S 127 B]")
    print()

    while gameOver == False:
        choice = input("MAIN MENU: [p]lay, [i]nstructions, or [q]uit?: ")
        print()
        if choice == "p": # (**"p" Section Tasks**)
            # TODO: Add at least four (4) additional rooms to the dungeon - creating a new 'room' function for each of them (1 pt.)
            #
            # HINT: This will require planning out the layout of your dungeon so that all the 'rooms' connect together correctly.
            #
            # HINT: Study this code carefully to see how the rooms connect, and which room the player is currently inside.
            #
            # NOTE: The other TODO tasks for this assignment can be found in the 'room1' function above.
            while currentRoom != FINAL_ROOM: # HINT: When implmenting combat, if the player's health is <= 0, this loop should not execute.
                if currentRoom == 1:
                    currentRoom, goldAmount, visited_room1 = room1(goldAmount, visited_room1)
                elif currentRoom == 2:
                    currentRoom, goldAmount, visited_room2 = room2(goldAmount, visited_room2)
                else:
                    print("Error - currentRoom number", currentRoom, "does not correspond with available rooms")
                    sys.exit()
            
            # HINT: If the player's health is > 0 when they escape the dungeon print a message like this one. 
            # Otherwise print a message stating that they perished in the dungeon.
            print()
            print("You have escaped with", goldAmount, "gold from the dungeon!")
            print()

            # Reset player values back to their original state
            # HINT: If you add other player values, you will have to reset them to their original values to restart the game.
            #
            # HINT: You can create 'constants' that you can assign to these variables. Doing so means you will only need to 
            # change the values you want to use in one place if you wish to change them.
            goldAmount = START_GOLD
            currentRoom = START_ROOM
            visited_room1 = False
            visited_room2 = False
        elif choice == "i": # (**"i" Section Tasks**)
            print("Good day to you explorer! Let me give you a firsthand guide on the adventures you will soon endure!")
            print("The dungeons down here are dangerous! Monsters are crawling in every crevice, waiting for you to make a mistake.")
            print("Fight these monsters if you are daring and brave enough, but remember to collect the plentiful and valuable gold. With it, you'll be rich!")
            
        elif choice == "q": 
            gameOver = True
            print("Goodbye!")
        else:
            print()
            print("Please enter [p], [i], or [q]...")
            print()

if __name__ == "__main__":
    main()