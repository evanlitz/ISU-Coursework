# Evan Litzer               November 15th, 2022
# Lab Week 13 Exercise #1           Section B

def decToBin(number) :
    bin = "" 
    first = number
    if number == 0 :
        return "The binary representation of", number, "is", number
    number = abs(number)
    while number != 0 :
        bin += str(number % 2)
        number //= 2
    if first < 0 :
        bin += "-"
    return "The binary representation of", first, "is", bin[::-1]


def main() :
    num1 = int(input("Enter an integer: "))
    string = decToBin(num1)
    print(string)



if __name__ == "__main__":
    main()