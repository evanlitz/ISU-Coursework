# Evan Litzer               9-13-2022
# Lab Week 4 - Exercise #4

import math

m1 = float(input("Input a float for m1: "))
m2 = float(input("Input a float for m2: "))

if (1 + m1 * m2) == 0 :
    print("The lines with slopes m1:", m1, "and m2:", m2, "are perpendicular to eachother.")
elif (m1 - m2) == 0 :
    print("The lines with slopes m1:", m1, "and m2:", m2, "are parallel.")
else:
    print("The lines with slopes m1:", m1, "and m2:", m2, "are at an angle of", abs((180/math.pi) * math.atan((m1 - m2) / (1 + m1 * m2))), "degrees.")


