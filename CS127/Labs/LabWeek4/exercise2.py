# Evan Litzer               9-13-2022
# Lab Week 4 - Exercise #2

import math

a = float(input("Input a float for 'a': "))
b = float(input("Input a float for 'b': "))
c = float(input("Input a float for 'c': "))
x = float(input("Input a float for 'x': "))
y = float(input("Input a float for 'y': "))

if y == (a * x**2 + b * x + c) :
    print("The point (", x, ",", y, ") lies on the parabola described by the equation: y =", a, "*", x, "** 2 +", b, x, "+", c)
else :
    print("The point (", x, y, ") does not line on the parabola described by the equation:  y =", a, "*", x, "** 2 +", b, "* x +", c)