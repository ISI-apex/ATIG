#include "data_movement.h"

Data_movement_t::Data_movement_t()
{
	this->k = 0;
	this->b = 0;
}

Data_movement_t::Data_movement_t(double k, double b)
{
	this->k = k;
	this->b = b;
}

performance_t Data_movement_t::eval(metadata_t input)
{
	struct performance_t ans;
	ans.exec_time = input.OPS*this->k + this->b;
	ans.latency = this->b;
	return ans;
}

void Data_movement_t::print(std::ostream & os)
{
	os << "Data_movement_t " << this->type << " " << this->id << " " << this->k << " " << this->b << "" << std::endl;
}


