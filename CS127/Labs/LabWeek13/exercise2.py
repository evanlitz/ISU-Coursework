# Evan Litzer               November 15th, 2022
# Lab Week 13 Exercise #2           Section B





def binbinToDec(binar) :
    prior = 0
    for char in binar :
        next = 2*prior + int(char)
        prior = next
    return next 


def main() :
    bin = str(input("Enter a (Binary) String: "))
    yay = binbinToDec(bin)
    print("The decimal representation is", yay)




if __name__ == "__main__":
    main()