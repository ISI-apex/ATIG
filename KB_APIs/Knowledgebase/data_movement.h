#pragma once
#include "global.h"

class Data_movement_t
{
private:
	double k;
	double b;
public:
	std::string type;
	int id;
	Data_movement_t();
	Data_movement_t(double k, double b);
	struct performance_t eval(struct metadata_t input);
	void print(std::ostream &os);
};