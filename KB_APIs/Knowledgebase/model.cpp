#include "model.h"
#include "global.h"

Linear_1d_t::Linear_1d_t()
{
}

Linear_1d_t::Linear_1d_t(double k, double b)
{
	this->k = k;
	this->b = b;
}

void Linear_1d_t::set(double k, double b)
{
	this->k = k;
	this->b = b;
}

performance_t Linear_1d_t::eval(metadata_t input)
{
	struct performance_t ans;
	ans.exec_time = input.OPS*this->k + this->b;
	ans.latency = this->b;
	return ans;
}

void Linear_1d_t::print(std::ostream & os)
{
	os << "Performance_model_t " << this->type << " " << this->id << " " << this->k << " " << this->b << "" << std::endl;
}

Performance_model_t::Performance_model_t()
{
}

performance_t Performance_model_t::eval(metadata_t input)
{
	return performance_t();
}
