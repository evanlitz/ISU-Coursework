#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <algorithm>
#include <unordered_set>

#include "MonsterAttributes.h"

std::string trim(const std::string &str) 
{
    const size_t first = str.find_first_not_of(" \t\r");
    const size_t last = str.find_last_not_of(" \t\r");
    if (first == std::string::npos) 
    {
        return "";
    } 
    else 
    {
        return str.substr(first, last - first + 1);
    }
}

void skipToEnd(std::ifstream &file)
{
    std::string line;
    while (std::getline(file, line))
    {
        if (trim(line) == "END") break ;
    }
}

bool parseMonster(std::ifstream &file, MonsterAttributes &monster) 
{
    std::string line;
    std::unordered_set<std::string> seenFields;
    bool parsingDesc = false;
    std::ostringstream descStream;

    while (std::getline(file, line)) {
        line = trim(line);

        if (line == "END") break;

        if (parsingDesc) 
        {
            if (line == ".") 
            {
                parsingDesc = false;
                monster.description = descStream.str();
                descStream.str("");  
            } else 
            {
                descStream << line << "\n";
            }
            continue;
        }

        std::istringstream iss(line);
        std::string keyword;
        iss >> keyword;

        if (seenFields.count(keyword))
        {
            while (std::getline(file, line) && trim(line) != "END");
            return false ;
        } 

        seenFields.insert(keyword);

        if (keyword == "NAME") 
        {
            std::getline(iss, monster.name);
            monster.name = trim(monster.name);
        } 
        else if (keyword == "DESC") 
        {
            parsingDesc = true;
        } 
        else if (keyword == "SYMB") 
        {
            char sym;
            iss >> sym;
            monster.symbol = sym;
        } 
        else if (keyword == "COLOR") 
        {
            std::string color;
            while (iss >> color) monster.colors.push_back(color);
        } 
        else if (keyword == "SPEED") 
        {
            std::string diceStr;
            iss >> diceStr;
            if (!Dice::parse(diceStr, monster.speed)) 
            {
                skipToEnd(file);
                return false;
            }
        } 
        else if (keyword == "HP") 
        {
            std::string diceStr;
            iss >> diceStr;
            if (!Dice::parse(diceStr, monster.hp)) 
            {
                skipToEnd(file);
                return false;
            }  
        } 
        else if (keyword == "DAM") 
        {
            std::string diceStr;
            iss >> diceStr;
            if (!Dice::parse(diceStr, monster.damage)) 
            {
                skipToEnd(file);
                return false;
            }            
        } 
        else if (keyword == "RRTY") 
        {
            iss >> monster.rarity;
            if (monster.rarity < 1 || monster.rarity > 100) 
            {
                skipToEnd(file);
                return false;
            }
        } 
        else if (keyword == "ABIL") 
        {
            std::string ab;
            while (iss >> ab) monster.abilities.push_back(ab);
        } 
        else 
        {
            while (std::getline(file, line) && trim(line) != "END");
            return false ; 
        }
    }

    monster.isComplete = !monster.name.empty() && !monster.description.empty() && monster.symbol && !monster.colors.empty() && monster.speed.dice >= 0 && !monster.abilities.empty() && monster.hp.dice >= 0 &&
        monster.damage.dice >= 0 && monster.rarity > 0;
    return monster.isComplete;
}

int main() {
    // std::ifstream file(".rlg327/monster_desc.txt");
    const char* homeDir = std::getenv("HOME");
    if (!homeDir) homeDir = std::getenv("USERPROFILE");  

    if (!homeDir) 
    {
        std::cerr << "Could not determine home directory.\n";
        return 1;
    }

    std::ifstream file(std::string(homeDir) + "/.rlg327/monster_desc.txt");


    if (!file.is_open()) 
    {
        std::cerr << "Failed to open monster description file.\n";
        return 1;
    }

    std::string header;
    std::getline(file, header);
    if (header != "RLG327 MONSTER DESCRIPTION 1") 
    {
        std::cerr << "Invalid monster description file header.\n";
        return 1;
    }

    std::string line;
    std::vector<MonsterAttributes> monsters;

    while (std::getline(file, line)) 
    {
        if (trim(line) == "BEGIN MONSTER") 
        {
            MonsterAttributes m;
            if (parseMonster(file, m)) 
            {
                monsters.push_back(m);
            } 
            else 
            {
                std::cerr << "Malformed monster skipped.\n";
            }
        }
    }

    for (MonsterAttributes &m : monsters) 
    {
        m.print();
    }

    return 0;
}
