# Evan Litzer          9-12-2022
# Lab Week 3 - Python Statement Results

# Statement: min(1, 2, 3, 4, 5) == 7%2
print("Statement: min(1,2,3,4,5) == 7%2")
print("Hand Computer Answer: True")
print("Computer's Answer:", min(1,2,3,4,5) == 7%2)

# Statement: float(round(10.4, 0))
print("Statement: float(round(10.4, 0)) = 10.0")
print("Hand Computer Answer: 10.0")
print("Computer's Answer:", float(round(10.4, 0)))

# Statement: pow(2, -2) == pow(2, .25)
print("Statement: pow(2, -2) == pow(2, .25)")
print("Hand Computer Answer: False")
print("Computer Answer:", pow(2, -2) == pow(2, .25))

# Statement: pow(float(round(3.4,0)),float(round(3.4,0)))
print("Statement: pow(float(round(3.4,0)),float(round(3.4,0)))")
print("Hand Computer Answer: 27.0")
print("Computer Answer:",  pow(float(round(3.4,0)),float(round(3.4,0))))


# Statement: pow(max(1,2,3),min(4,5,6))
print("Statement: pow(max(1,2,3),min(4,5,6))")
print("Hand Computer Answer: 81")
print("Computer Answer:", pow(max(1,2,3),min(4,5,6)))