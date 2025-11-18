# Evan Litzer           October 18th, 2022
# Lab Week 9 Exercise 1            Section B
import random


a = int(input("Enter an integer: "))
b = int(input("Enter another integer: "))

numbers = []

def listCreation(list, x, y) :
    update = x
    while update > 0 :
        list.append(random.randint(x, x + y))
        update -= 1
    print(list)

def listSorting(list, y) :
    newlist = []
    for j in list :
        if j % y == 0 :
            newlist.append(j)
    return newlist

listCreation(numbers, a, b)
print(listSorting(numbers, b))