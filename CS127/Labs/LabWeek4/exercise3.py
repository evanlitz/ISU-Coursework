# Evan Litzer               9-13-2022
# Lab Week 4 - Exercise #3

import math

x1 = float(input("Input a float for x1: "))
y1 = float(input("Input a float for y1: "))
x2 = float(input("Input a float for x2: "))
y2 = float(input("Input a float for y2: "))

if (x2-x1) == 0 :
    print("The line described by points (", x1, ",", y1, ") and (", x2, ",", y2, ") is vertical.")
elif (y2 - y1)/(x2-x1) == 0 :
    print("The line described by points (", x1, ",", y1, ") and (", x2, ",", y2, ") is horizontal.")
else: 
    print("The line described by points (", x1, ",", y1, ") and (", x2, ",", y2, ") has a slope of", (y2 - y1)/(x2-x1), ".")

