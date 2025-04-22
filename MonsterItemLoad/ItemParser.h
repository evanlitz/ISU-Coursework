#pragma once

#include <vector>
#include <string>
#include <fstream>
#include "ItemAttributes.h"

std::string trim(const std::string &s);

bool parseItem(std::ifstream &file, ItemAttributes &item);

std::vector<ItemAttributes> loadItemTemplates();
