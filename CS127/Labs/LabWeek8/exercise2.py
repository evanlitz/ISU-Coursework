# Evan Litzer           October 11th, 2022
# Lab Week 8 Exercise 2            Section B

x = int(input("Enter an integer: "))
y = int(input("Enter an integer: "))
z = int(input("Enter an integer: "))


def sort(a, b, c) :
    one = min(a, b, c)
    three = max(a, b, c)
    two = (a + b + c) - three - one
    return one, two, three



print("The sorted values are: ", sort(x, y, z))