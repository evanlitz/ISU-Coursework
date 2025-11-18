# Evan Litzer                           12-6-2022
# COM S 127                             Section B

# This is a game inspired by the popular 'Everybody Talks and Nobody Explodes' game. The premise of this program is that the user has to diffuse 
# a bomb through completing puzzles and battling the AI (in this case the bomb system). These games include commonplace and childish activites like
# rock-paper-scissors and higher/lower number guessing. There is also a password you have to remember, along with cutting wires. There are a total
# of three difficulties that determine how many lives (strikes) you get to expend, basically the leverage counted in mistakes when completing the
# tasks. When the strikes run out, the bomb explodes and the program terminates. Each activity is its own program, with the password having one
# for randomly generating it (based on lists) and one for entering it. I definitely could have added one more program for something math-related,
# or maybe even a timer function, but I decided to just end it here. There is also a menu similar to the other games that we have programmed,
# commanding the user to enter either p (play), i (instructions), or q (quit). Strikes (lives) and gameOver are passed into most of the functions.
# The code is a bit messy, but it gets the job done.
import random

def passwordSet() :
    colors = ["red", "blue", "yellow", "green", "purple", "orange", "brown", "pink", "gray", "white", "burgundy", "turquoise"]
    animals = ["chicken", "cow", "dolphin", "pig", "tiger", "monkey", "giraffe", "eagle", "ant", "mouse", "dog", "sheep"]
    nombre = random.randint(100, 999)
    password = colors[random.randint(0, len(colors)-1)] + animals[random.randint(0, len(animals)-1)] + str(nombre)
    print("PASSWORD =", password)
    print(password, "IS YOUR SET PASSWORD. REMEMBER THIS!")
    a = input("Ready to proceed? Enter anything...: ")
    print("\n" * 10000) 
    return password

def higherLower(strike, gameOver) :
    print("Guess the correct number between 1 and 100.")
    print("You will be told higher or lower based on your guess!")
    print("You get 5 buffer guesses before strikes are counted!")
    number = random.randint(1, 100)
    marker = False
    indicator = 0
    while marker == False and strike > 0:
        guess = (input("Enter an integer between 1-100: "))
        if guess == number :
            print("CORRECT! SYSTEM HAS CALIBRATED, BOMB WEAKSPOTS HAVE BEEN IDENTIFIED!")
            marker = True
        elif guess < number :
            print("TOO LOW! GUESS HIGHER!")
            indicator += 1
        elif guess > number :
            print("TOO HIGH! GUESS LOWER!")
            indicator += 1    
        else :
            print("GUESS A VALID NUMBER!")        
            indicator += 1
    if strike > indicator - 5 and indicator >= 5:
        strike -= (indicator - 5)
    elif  strike > (indicator - 5) and indicator < 5:
        pass
    else :
        gameOver = True 
    return strike, gameOver

def enterPassword(password, strike, gameOver) :
    print("THE WIRE PANEL REQUIRES A PASSWORD! TRY THE ONE GENERATED FOR YOU!")
    print()
    check = False
    while check == False and strike > 0:
        attempt = input("ENTER YOUR PASSWORD: ")
        print()
        if attempt == password :
            print("SUCCESSFUL! THE PANEL HAS BEEN OPENED!")
            print()
            check = True
        else :
            print("UNSUCCESSFUL! TRY AGAIN!")
            print()
            strike += 1
    if strike == 0 :
        gameOver = True
    return strike, gameOver

def RPS(strike, gameOver) :
    print("OL' CLASSIC ROCK PAPER SCISSORS!")
    print("BEAT THE AI TO CONTINUE ON YOUR PATH!")
    print("EVERY TIME YOU LOSE, A STRIKE WILL BE ADDED!")
    a = input("Ready to proceed? Enter anything...: ")
    decisions = ["r", "p", "s"]
    marker = False 
    while marker == False and strike > 0:
        computer = decisions[random.randint(0, len(decisions) - 1)]
        human = input("Enter [r]ock, [p]aper, or [s]cissors: ")
        if human == "r" and computer == "s" :
            print("The system chose", computer)
            print("SUCCESSFUL! ANOTHER LAYER OF SECURITY HAS BEEN CRACKED!")
            print()
            marker = True
        elif human == "p" and computer == "r" :
            print("The system chose", computer)
            print("SUCCESSFUL! ANOTHER LAYER OF SECURITY HAS BEEN CRACKED!")
            print()
            marker = True
        elif human == "s" and computer == "p" :
            print("The system chose", computer)
            print("SUCCESSFUL! ANOTHER LAYER OF SECURITY HAS BEEN CRACKED!")
            print()
            marker = True
        elif human == computer :
            print("The system chose", computer)
            print("TIE! TRY AGAIN!")
        else :
            strike -= 1
            print("The computer has chosen", computer)
            print("FAILURE! A STRIKE HAS BEEN GIVEN! TRY AGAIN!")
            print()
    if strike == 0 :
        gameOver = True
    return strike, gameOver

def cutWires(strike, gameOver) :
    print("YOU WILL HAVE TO CUT ONE WIRE IN ORDER TO DIFFUSE THE BOMB!")     
    print("EVERY TIME YOU CUT A WRONG WIRE, A STRIKE IS GIVEN!")       
    print("GOOD LUCK AND BE CAREFUL!")
    a = input("Ready to proceed? Enter anything...: ")
    wires = ["red", "white", "blue", "green", "black"]
    correct = wires[random.randint(0, len(wires) - 1)]
    marker = False
    while marker == False and strike > 0:
        print()
        print(wires)
        print("CHOOSE A WIRE TO CUT!")
        choice = input("Enter a wire color: ")
        if choice == correct :
            marker = True
            print("Nice choice! You cut the correct wire!")
        else :
            print("WRONG WIRE! A STRIKE HAS BEEN GIVEN!")
            strike -= 1 
            wires.remove(choice)
    if strike == 0 :
        gameOver = True

    return strike, gameOver

def main() :
    gameOver = False 
    print("Welcome to Diffuser La Bombe!")
    print()

    print("By: Evan Litzer")
    print("[COM S 127 B]")
    print()
    while gameOver == False:
        print("-----------------------------------------------------------------")
        selection = input("MAIN MENU: [p]lay game, [i]nstructions, or [q]uit?: ")
        if selection == "p" :
            difficulty = input("Enter your desired difficulty: [e]asy, [h]ard, or [i]mpossible?: ")
            if difficulty == "e" :
                strike = 10
                password = passwordSet()
                strike, gameOver = higherLower(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = RPS(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = enterPassword(password, strike, gameOver)  
                if gameOver == False :
                    strike, gameOver = cutWires(strike, gameOver)  
                if gameOver == True :
                    print("BOOOOOOOOOOOOM!")
                    print("THE BOMB EXPLODED.....")
                    print("NOBODY SURVIVED. CLICK RUN TO TRY AGAIN!")
                else :
                    print("CONGRATULATIONS!")
                    print("YOU HAVE DIFFUSED THE BOMB AND TERMINATED THE THREAT!")
                    print("TRY AGAIN ON A HARDER DIFFICULTY!")
                    gameOver = True
            if difficulty == "h" :
                strike = 7
                password = passwordSet()
                strike, gameOver = higherLower(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = RPS(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = enterPassword(password, strike, gameOver)  
                if gameOver == False :
                    strike, gameOver = cutWires(strike, gameOver)  
                if gameOver == True :
                    print("BOOOOOOOOOOOOM!")
                    print("THE BOMB EXPLODED.....")
                    print("NOBODY SURVIVED. CLICK RUN TO TRY AGAIN!")
                else :
                    print("CONGRATULATIONS!")
                    print("YOU HAVE DIFFUSED THE BOMB AND TERMINATED THE THREAT!")
                    print("TRY AGAIN ON IMPOSSIBLE!")
                    gameOver = True
            if difficulty == "i" :
                strike = 5
                password = passwordSet()
                strike, gameOver = higherLower(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = RPS(strike, gameOver)
                if gameOver == False :
                    strike, gameOver = enterPassword(password, strike, gameOver)  
                if gameOver == False :
                    strike, gameOver = cutWires(strike, gameOver)  
                if gameOver == True :
                    print("BOOOOOOOOOOOOM!")
                    print("THE BOMB EXPLODED.....")
                    print("NOBODY SURVIVED. CLICK RUN TO TRY AGAIN!")
                else :
                    print("CONGRATULATIONS!")
                    print("YOU HAVE DIFFUSED THE BOMB AND TERMINATED THE THREAT!")
                    print("YOU ARE VERY SKILLED! YOU ARE THE PROFESSIONAL BOMB DIFFUSER MASTER!")
                    gameOver = True
            if difficulty != "i" or difficulty != "e" or difficulty != "h"  :
                print("Enter a real difficulty!")
        if selection == "i" :
            print("Diffuse the bomb by completing all the logic puzzles.")
            print("Depending on the difficulty, you are given an amount of strikes that will determine when the bomb will blow up.")
            print("Complete all the necesscary steps to successfully win and avoid danger.")
            print("Make as little amount of mistakes as possible!")
        if selection == "q" :
            gameOver = True
            print("Goodbye!")
        if selection != "q" or selection != "p" or selection != "p" :
            print("Please enter [p], [i], or [q]")
if __name__ == "__main__":
    main()