#pragma once
#include "global.h"

class Performance_model_t
{
public:
	std::string type;
	int id;
	Performance_model_t();
	virtual struct performance_t eval(struct metadata_t input);
	virtual void print(std::ostream &os) {};
};

class Linear_1d_t: public Performance_model_t
{
private:
	double k;
	double b;
public:
	Linear_1d_t();
	Linear_1d_t(double k,double b);
	void set(double k, double b);
	struct performance_t eval(struct metadata_t input);
	void print(std::ostream &os);
};
