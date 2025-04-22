CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17
LDFLAGS = -lncurses

SRC = main.cpp RealDungeon.cpp ItemParser.cpp MonsterParser.cpp
OBJ = $(SRC:.cpp=.o)

TARGET = dungeon

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(OBJ) -o $(TARGET) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

monsterparser: MonsterParser.cpp MonsterAttributes.h Dice.h
	g++ -std=c++17 -o monsterparser MonsterParser.cpp

itemparser: ItemParser.cpp ItemAttributes.h Dice.h
	g++ -std=c++17 -o itemparser ItemParser.cpp

