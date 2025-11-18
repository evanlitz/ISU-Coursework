# Evan Litzer           October 11th, 2022
# Lab Week 8 Exercise 3            Section B

x = int(input("Enter an integer: "))
y = int(input("Enter an integer: "))

def swap(a, b) :
    temp = 0
    temp = a
    a = b
    b = temp
    return a, b

x, y = swap(x, y)
print("The swapped values are: ", x,",", y)