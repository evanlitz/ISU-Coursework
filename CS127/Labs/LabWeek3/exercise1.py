# Evan Litzer          9-12-2022
# Lab Week 3 - Exercise #1
import math
a = int(input("Input the length of a: "))
b = int(input("Input the length of b: "))
c = int(input("Input the length of c: "))
s = float((a+b+c)/2)
area = math.sqrt(s*(s-a)*(s-b)*(s-c))
print("The area of the triangle is", area)
