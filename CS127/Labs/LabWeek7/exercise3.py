# Evan Litzer           October 4th, 2022
# Lab Week 7 Exercise 3            Section B

number = int(input("Enter a number: "))

for i in range(number) :
    for j in range(i + 1) :
        print("*", end = "")
    print()

while number > 0 :
    for i in range(number-1) :
        print("#", end = "")
    print()
    number -= 1