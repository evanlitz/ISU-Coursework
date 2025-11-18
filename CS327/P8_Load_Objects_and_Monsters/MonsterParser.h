#pragma once

#include <vector>
#include <string>
#include <fstream>
#include "MonsterAttributes.h"

std::string trim(const std::string &str);

bool parseMonster(std::ifstream &file, MonsterAttributes &monster);

std::vector<MonsterAttributes> loadMonsterTemplates();
