// On linux, you can compile and run it like so:
// g++ blur_cpu.cpp -g -std=c++11 -I ../include -L ../bin -lHalide -lpthread -ldl -o blur_cpu 
// LD_LIBRARY_PATH=../bin ./blur_cpu

#include "Halide.h"
#include "clock.h"

using namespace Halide;

#include <stdio.h>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>


int main(int argc, char **argv) {
    // subject to change: the output file name
    std::string FILENAME = "halide_blur_cpu_300_points_Xeon.csv"; 
    std::ofstream ofile;
    ofile.open(FILENAME);
    // how many data instances to generate
    int NUM = 50;
    // input size ranges from 2^10 to 2^15
    for (int k = 0; k <= 5; k++){ 
        int p_input = 10 + k;
        for (int i = 0; i < NUM; i++) {

            if (i % 10 == 0) std::cout << i << std::endl;
            
            // Halide Blur operation
            Func blur_x, blur_y;
            Var x_, y_, xi, yi;

            Func input;
            input(x_,y_) = rand() % 1024 + 1;
            
            int power = 10;
            // varying parameters/knobs
            int p1 = rand() % power + 1; 
            int p2 = rand() % power + 1; 
            int p3 = rand() % p2 + 1; // p2 > p3
            int p4 = rand() % p3 + 1; // p3 > p4

            int v1 = pow(2,p1);
            int v2 = pow(2,p2);
            int v3 = pow(2,p3);
            int v4 = pow(2,p4);
            
            // write to the console
            std::cout << v1 << "," << v2 << "," << v3 << "," << v4 << std::endl;

            // The algorithm - no storage or order
            blur_x(x_, y_) = (input(x_-1, y_) + input(x_, y_) + input(x_+1, y_))/3;
            blur_y(x_, y_) = (blur_x(x_, y_-1) + blur_x(x_, y_) + blur_x(x_, y_+1))/3;

            // The schedule - defines order, locality; implies storage
            Var x_i("x_i");
            Var x_i_vi("x_i_vi");
            Var x_i_vo("x_i_vo");
            Var x_o("x_o");
            Var x_vi("x_vi");
            Var x_vo("x_vo");
            Var y_i("y_i");
            Var y_o("y_o");

            {
                Var x = blur_x.args()[0];
                blur_x
                    .compute_at(blur_y, x_o)
                    .split(x, x_vo, x_vi, v1)
                    .vectorize(x_vi);
            }
            {
                Var x = blur_y.args()[0];
                Var y = blur_y.args()[1];
                blur_y
                    .compute_root()
                    .split(x, x_o, x_i, v2)
                    .split(y, y_o, y_i, v3)
                    .reorder(x_i, y_i, x_o, y_o)
                    .split(x_i, x_i_vo, x_i_vi, v4)
                    .vectorize(x_i_vi)
                    .parallel(y_o)
                    .parallel(x_o);
            }


            double time = 0;
            int rounds = 5; 
            // for each data instance, run 5 times and take the average
            for (int j = 0; j < rounds; j++){
                // run
                double t1 = current_time();
                blur_y.realize(pow(2,p_input),pow(2,p_input)); 
                double t2 = current_time();
                
                time += (t2 - t1)/1000;
            }

            double avgtime = time/rounds; 
            std::cout << avgtime << std::endl;
            // define C
            // for blur operation, C = n^2, where n is the input dimension
            double cons = pow(2,p_input)*pow(2,p_input);
            // write to the output file
            ofile << avgtime << "," << pow(2,p_input) << "," << v1 << "," << v2 << "," << v3 << "," << v4 << ",";
            ofile << cons << "," << '\n';
        }
    }


    ofile.close();

    printf("Success!\n");

    return 0;
}
