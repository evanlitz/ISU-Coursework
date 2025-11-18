# Evan Litzer               9-13-2022
# Lab Week 4 - Conditional Results

import math

# Question 1
print("Question 1: ")
print()

#Initial hand computer answer
print("Hand Computer Answer: False")
print("x * x * x + y = {0}".format(355))
print("y * x + 47 = {0}".format(131))

# Computer answer
x = 7
y = 12
if x * x * x + y == y * x + 47:
    print("Computer Answer: True")
else:
    print("Computer Answer: False")

print("x * x * x + y = {0}".format(x * x * x + y))
print("y * x + 47 = {0}".format(y * x + 47))

# Divider
print("--------------------------------------------")
print()

# Question 2
print("Question 2: ")
print()

# Initial hand computer answer
print("Hand Computer Answer: True")
print("1000 * x / y / z + 2 = {0}".format(152))
print("x ** 2 * 20 = {0}".format(180))

# Computer Answer
x = 3
y= 4
z = 5

if 1000 * x / y / z + 2 <= x ** 2 * 20 :
    print("Computer Answer: True")
else:
    print("Computer Answer: False")

print("1000 * x/y/z + 2 = {0}".format(1000 * x/y/z + 2))
print("x**2 * 20 = {0}".format(x**2 * 20))

# Divider
print("--------------------------------------------")
print()

# Question 3
print("Question 3: ")
print()

# Initial hand computer answer
print("Hand Computer Answer: False")
print("x + y // z = {0}".format(28))
print("x * z % y + 2 = {0}".format(38))

# Computer Answer
x = 12
y = 47
z = 3
if x + y // z >= x * z % y + 2:
    print("Computer's Answer: True")
else:
    print("Computer's Answer: False")
print("x + y // z = {0}".format(x + y // z))
print("x * z % y + 2 = {0}".format(x * z % y + 2))

# Divider
print("--------------------------------------------")
print()

# Question 4
print("Question 4: ")
print()

# Initial hand computer answer
print("Hand Computer Answer: True")
print("x * y % z = {0}".format(2))
print("z % y * x = {0}".format(8))

# Computer Answer
if x * y % z != z % y * x:
    print("Computer's Answer: True")
else:
    print("Computer's Answer: False")
print("x * y % z = {0}".format(x * y % z))
print("z % y * x = {0}".format(z % y * x))

# Divider
print("--------------------------------------------")
print()

# Question 5
print("Question 5: ")
print()

# Initial hand computer answer
print("Hand Computer Answer: True")
print("x * y % z = {0}".format(0))
print("z % y * x = {0}".format(0))

# Computer Answer
x = 3
y = x + 400 // 3 ** 2
z = x * y % 10 + 2 ** 2

if z * y ** 2 % 5 == z * 2 ** y % 4:
    print("Computer's Answer: True")
else:
    print("Computer's Answer: False")
print("z * y ** 2 % 5 = {0}".format(z * y ** 2 % 5))
print("z * 2 ** y % 4 = {0}".format(z * 2 ** y % 4))


