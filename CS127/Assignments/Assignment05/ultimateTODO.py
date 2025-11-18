# Evan Litzer             11/2/2022
# Assignment 5 

import sys
import pickle

def initList():
    todoList = {}
    todoList["backlog"] = []
    todoList["todo"] = []
    todoList["in_progress"] = []
    todoList["in_review"] = []
    todoList["done"] = []

    return todoList

def saveList(todoList):
    try:
        listName = input("Enter List Name (Exclude .lst Extension): ")
        with open("./" + listName + ".lst", "wb") as pickle_file:
            pickle.dump(todoList, pickle_file)
    except:
        print("ERROR (saveList): ./{0}.lst is not a valid file name!".format(listName))
        sys.exit()

def loadList():
    try:
        listName = input("Enter List Name (Exclude .lst Extension): ")
        with open("./" + listName + ".lst", "rb") as pickle_file:
            todoList = pickle.load(pickle_file)
    except:
        print("ERROR (loadList): ./{0}.lst was not found!".format(listName))
        sys.exit()
    
    return todoList

def checkItem(item, todoList):
    itemFound = False
    keyName = ""
    index = -1
    counter = -1
    for k in todoList.keys() :
        counter += 1
        if item in todoList[k] :
            itemFound = True
            keyName = k
            index = counter
    return itemFound, keyName, index    

def addItem(item, toList, todoList):
    itemFound, keyName, index = checkItem(item, todoList)
    if itemFound == True :
        print("Error:", item, "already exists in the TODO list", keyName, "at the index of", index, "!")
    else :
        todoList[toList].append(item)
    return todoList


def deleteItem(item, todoList):
    itemFound, keyName, index = checkItem(item, todoList)
    if itemFound == True :
        todoList[keyName].remove(item)  # Problem in this line.
    else :
        print("The task", item, "is not in this list.")
    return itemFound, todoList

def moveItem(item, toList, todoList):
    itemFound, todoList = deleteItem(item, todoList)
    if itemFound == True :
        todoList = addItem(item, toList, todoList)
    return todoList

def printTODOList(todoList):
    for k, j in todoList.items() :
        print(k, ":", j)
    return None

def runApplication(todoList):
    while True:
        print("-----------------------------------------------------------------")
        choice = input("APPLICATION MENU: [a]dd to backlog, [m]ove item, [d]elete item, [s]ave list, or [q]uit to main menu?: ")
        print()

        if choice == "a":
            item = input("Enter an item to add: ")
            todoList = addItem(item, "backlog", todoList)
            printTODOList(todoList) 
            pass
        elif choice == "m":
            nothing = True
            for k in todoList.keys() :
                if len(todoList[k]) != 0:
                    nothing = False 
            if nothing == True :
                print("Error: No items exist in the list to move.")
                break
            item = input("Enter an item to move: ")
            itemFound, keyName, index = checkItem(item, todoList)
            while itemFound == False :
                print("Error: Entered item does not exist. Please enter another item.")
                item = (input("Enter an item to move: "))
                itemFound, keyName, index = checkItem(item, todoList)
            keyName = (input("Enter a key for your item to move to: "))
            while keyName not in todoList.keys() :
                print("Error: Key does not exist in list. Please enter another key.")
                keyName = (input("Enter a key for your item to move to: "))
            todoList = moveItem(item, keyName, todoList)
            printTODOList(todoList)
            
        elif choice == "d":
            nothing = True
            for k in todoList.keys() :
                if todoList[k] != [] :
                    nothing = False 
            if nothing == True :
                print("Error: No items exist in the list to delete.")
                # Somehow break code?
            item = (input("Enter an item to delete: "))
            itemFound, todoList = deleteItem(item, todoList)
            if itemFound == False :
                print("Error: Entered item does not exist in the list. Please try again.")
                while itemFound == False :
                    item = (input("Enter an item to delete: "))
                    itemFound, todoList = deleteItem(item, todoList)    
            printTODOList(todoList)
            pass
        elif choice == "s":
            saveList(todoList)
            print("Saving List...")
            print()
            printTODOList(todoList)
        elif choice == "q":
            print("Returning to MAIN MENU...")
            print()
            break
        else:
            print("ERROR: Please enter [a], [m], [d], [s], or [q].")
            print()

    return todoList

def main():
    taskOver = False

    print("The Ultimate TODO List")
    print()
    
    print("By: Evan Litzer")
    print("[COM S 127 B]")
    print()

    while taskOver == False:
        print("-----------------------------------------------------------------")
        choice = input("MAIN MENU: [n]ew list, [l]oad list, or [q]uit?: ")
        print()
        if choice == "n": 
            todoList = initList()

            printTODOList(todoList)
            
            runApplication(todoList)
        elif choice == "l":
            todoList = loadList()

            printTODOList(todoList)
            
            runApplication(todoList)
        elif choice == "q":
            taskOver = True
            print("Goodbye!")
            print()
        else:
            print("Please enter [n], [l], or [q]...")
            print()

if __name__ == "__main__":
    main()