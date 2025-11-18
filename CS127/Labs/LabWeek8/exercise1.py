# Evan Litzer           October 11th, 2022
# Lab Week 8 Exercise 1            Section B

x = int(input("Enter an integer: "))
y = int(input("Enter an integer: "))

def product(a, b) :
    sum = 0
    while b > 0 :
        sum += a
        b -= 1
    return sum


print("The product of", x, "x", y, "=", product(x, y))