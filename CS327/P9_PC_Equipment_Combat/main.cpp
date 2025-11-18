#include "Dungeon.h"
#include "ItemAttributes.h"
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include "ItemParser.h"
#include "MonsterParser.h"



int main(int argc, char* argv[]) {
    Dungeon d;
    d.numObjects = 10 ;
    d.itemTemplates = loadItemTemplates();
    d.monsterTemplates = loadMonsterTemplates();
    d.runGameLoop(argc, argv);
    return 0;
}
