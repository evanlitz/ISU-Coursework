# Evan Litzer             9/25/2022
# Assignment 2

print("Welcome to the Magic 9 Ball...")
print()

print("By: Evan Litzer")
print("[COM S 127 B]")
print()

print("What would you like to do?")
print()
choice = input("[c]alculator, [p]rediction, [q]uit: ")
print()

if choice == "c" :
    calc = str(input("Input a math operator: "))
    if calc == "+" :
        left = float(input("Input a number for the left side: "))
        right = float(input("Input a number for the right side: "))
        print(left + right)
    elif calc == "-" :
        left = float(input("Input a number for the left side: "))
        right = float(input("Input a number for the right side: "))
        print(left - right)
    elif calc == "*" :
        left = float(input("Input a number for the left side: "))
        right = float(input("Input a number for the right side: "))
        print(left * right)
    elif calc == "/" :
         left = float(input("Input a number for the left side: "))
         right = float(input("Input a number for the right side: "))      
         if right == 0 :
            print("Error. Dividing by 0. Please re-enter a different value.")
         else :
            print(left / right) 
    elif calc == "%" :
         left = float(input("Input a number for the left side: "))
         right = float(input("Input a number for the right side: "))      
         if right == 0 :
            print("Error. Dividing by 0. Please re-enter a different right-side value.")
         else :
            print(left % right) 
    elif calc == "**" :
         left = float(input("Input a number for the left side: "))
         right = float(input("Input a number for the right side: "))  
         print(left ** right)
    else :
        print("Error: You must enter either \"+\", \"-\", \"*\", \"/\", \"%\", or \"**\"")
elif choice == "p" :
    question = str(input("What's your question?: "))
    number = len(question) % 10
    if number == 0 :
        print("Absolutely.")
    elif number == 1 :
        print("Don't count on it.")
    elif number == 2 :
        print("Signs point to yes.")
    elif number == 3 :
        print("My sources say no.")
    elif number == 4 :
        print("Most likely yes.")
    elif number == 5 :
        print("No way.")
    elif number == 6 :
        print("YES YES YES YES YES!")
    elif number == 7 :
        print("Nope.")
    elif number == 8 :
        print("Ask again later.")
    elif number == 9 :
        print("Please shake me again.")
    else :
        print("Error: Please try again.")
elif choice == "q" :
    print("Maybe next time...")
else :
    print("Error: I did not understand your input. Please try again.")
    
