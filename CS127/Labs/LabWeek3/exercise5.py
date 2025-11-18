# Evan Litzer          9-12-2022
# Lab Week 3 - Exercise #5

c1 = str(input("Input Class 1: "))
g1 = int(input("Grade: "))
c2 = str(input("Input Class 2: "))
g2 = int(input("Grade: "))
c3 = str(input("Input Class 3: "))
g3 = int(input("Grade: "))
c4 = str(input("Input Class 4: "))
g4 = int(input("Grade: "))

average = float((g1 + g2 + g3 + g4)/ 4)
print("The Average grade between", c1, c2, c3, "and", c4, "is", average)
