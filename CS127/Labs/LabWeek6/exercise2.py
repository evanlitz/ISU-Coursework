# Evan Litzer               9-27-2022
# Lab Week 6                Exercise 2

counter1 = int(input("Enter an integer: "))
reset = int(input("Enter an integer: "))

while counter1 > 0 :
    counter2 = reset
    while counter2 > 0 :
        print(counter1 * counter2, " ", end = "")
        counter2 -= 1
    print()
    counter1 -= 1



