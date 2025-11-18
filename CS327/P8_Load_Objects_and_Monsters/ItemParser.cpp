#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_set>
#include "ItemAttributes.h"
#include "Dice.h"
#include "ItemParser.h"
#include "Constants.h"



bool parseItem(std::ifstream &file, ItemAttributes &item) 
{
    std::string line;
    std::unordered_set<std::string> seen;
    bool parsingDesc = false;
    std::ostringstream descStream;

    while (std::getline(file, line)) 
    {
        line = trim(line);
        if (line == "END") break;

        if (parsingDesc) 
        {
            if (line == ".") 
            {
                item.description = descStream.str();
                parsingDesc = false;
            } 
            else 
            {
                descStream << line << "\n";
            }
            continue;
        }

        std::istringstream iss(line);
        std::string keyword;
        iss >> keyword;

        if (seen.count(keyword)) return false;
        seen.insert(keyword);

        if (keyword == "NAME") 
        {
            std::getline(iss, item.name), item.name = trim(item.name);
        }
        else if (keyword == "TYPE") 
        { 
            iss >> item.type;
        }
        else if (keyword == "COLOR") 
        {
            iss >> item.color;
        }
        else if (keyword == "DESC") 
        {
            parsingDesc = true;
        }
        else if (keyword == "WEIGHT")
        { 
            Dice::parse(iss.str().substr(7), item.weight);
        }
        else if (keyword == "HIT") 
        {
            Dice::parse(iss.str().substr(4), item.hit);
        }
        else if (keyword == "DAM") 
        {
            Dice::parse(iss.str().substr(4), item.damage);
        }
        else if (keyword == "DODGE") 
        {
            Dice::parse(iss.str().substr(6), item.dodge);
        }
        else if (keyword == "DEF") 
        {
            Dice::parse(iss.str().substr(4), item.defense);
        }
        else if (keyword == "SPEED") 
        {
            Dice::parse(iss.str().substr(6), item.speed);
        }
        else if (keyword == "ATTR") 
        {
            Dice::parse(iss.str().substr(5), item.attr);
        }
        else if (keyword == "VAL") 
        {
            Dice::parse(iss.str().substr(4), item.value);
        }
        else if (keyword == "RRTY") 
        {
            iss >> item.rarity;
        }
        else if (keyword == "ART") 
        {
            std::string val;
            iss >> val;
            item.artifact = (val == "TRUE");
        } 
        else 
        {
            return false;
        }
    }

    item.isComplete = !item.name.empty() && !item.type.empty() && !item.color.empty() && !item.description.empty() && item.rarity > 0;
    return item.isComplete;
}

std::vector<ItemAttributes> loadItemTemplates() {
    std::vector<ItemAttributes> items;

    const char* homeDir = std::getenv("HOME");
    if (!homeDir) homeDir = std::getenv("USERPROFILE");

    if (!homeDir) {
        std::cerr << "Could not determine home directory.\n";
        return items;
    }

    std::ifstream file(std::string(homeDir) + "/.rlg327/object_desc.txt");

    if (!file.is_open()) {
        std::cerr << "Failed to open object description file.\n";
        return items;
    }

    std::string header;
    std::getline(file, header);
    if (trim(header) != "RLG327 OBJECT DESCRIPTION 1") {
        std::cerr << "Invalid object file header.\n";
        return items;
    }

    std::string line;
    while (std::getline(file, line)) {
        if (trim(line) == "BEGIN OBJECT") {
            ItemAttributes item;
            if (parseItem(file, item)) {
                items.push_back(item);
            } else {
                std::cerr << "Malformed item skipped.\n";
            }
        }
    }

    return items;
}
