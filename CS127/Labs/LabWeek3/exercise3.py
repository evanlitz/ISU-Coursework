# Evan Litzer          9-12-2022
# Lab Week 3 - Exercise #3

A = int(input("Input a value for A: "))
B = int(input("Input a value for B: "))
C = int(input("Input a value for C that doesn't equal 0 or A: "))

print("The sum of the three numbers equals:", A + B + C)

print("Modulus of A mod C equals:", A % C)

print("Multiplying A by B before dividing by C equals:", (A*B)/C)

temp = C - A
print("C divided by (C - A) equals:", C/temp)

print("The Average of A, B, and C equals:", (A + B + C)/3)
    
