# Evan Litzer           October 18th, 2022
# Lab Week 9 Exercise 2            Section B
from math import sqrt

def calculateDistance(xpos, ypos, listName, listX, listY) :
    distanceList = []
    for x, y in enumerate(listName):
        myX = (xpos - listX[x])**2
        myY = (xpos - listY[x])**2

        distanceList.append(sqrt(myX + myY))
    return distanceList

def main() :
    xpos = int(input("Enter your X Amount: "))
    ypos = int(input("Enter your Y Amount: "))
    listName = ["Timizoara", "Zerind", "Fagaras", "Pitesti", "Vaslui"]
    listX = [2, 2, 4, 5, 9]
    listY = [9, 4, 2, 7, 8]
    minList = []
    newCity = ""
    while newCity != "*" :
        newCity = input("Type any cities you'd like to add to the system, or enter * to stop: ")
        if newCity != "*":
            listName.append(newCity)
            listX.append(int(input(f"What is the X coordinate of {newCity}?")))
            listY.append(int(input(f"What is the Y coordinate of {newCity}?")))

    for x,y in enumerate(listName):
        distanceList = calculateDistance(xpos, ypos, listName, listX, listY)
    smallest = min(distanceList)
    for x,y in enumerate(distanceList) :
        print(listName[x], distanceList[x])
        if distanceList[x] == smallest:
            minList.append(listName[x])
    if len(minList)>1:
        print(f"The cities with the shortest distance are {', '.join(minList)} with a distance of {smallest}")
    else :
        print(f"The closest city is {minList[0]} with a distance of {smallest}")

if __name__ == "__main__" :
    main()


    

