# Evan Litzer               9-13-2022
# Lab Week 4 - Exercise #1

import math

length = float(input("Input a float for the length: "))
height = float(input("Input a float for the height: "))

print("The perimeter equals", 2*(length + height))

if length == height :
    print("The rectangle is a square.")
else :
    print("The rectangle is not a square.")