// Halide tutorial lesson 1: Getting started with Funcs, Vars, and Exprs

// This lesson demonstrates basic usage of Halide as a JIT compiler for imaging.

// On linux, you can compile and run it like so:
// g++ blur.cpp -g -std=c++11 -I ../include -I ../tools -L ../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o blur
// LD_LIBRARY_PATH=../bin ./blur

// If you have the entire Halide source tree, you can also build it by
// running:
//    make tutorial_lesson_01_basics
// in a shell with the current directory at the top of the halide
// source tree.

// The only Halide header file you need is Halide.h. It includes all of Halide.
#include "Halide.h"
#include "clock.h"


using namespace Halide;

// We'll also include stdio for printf.
#include <stdio.h>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>

// A helper function to check if OpenCL, Metal or D3D12 is present on the host machine.

Target find_gpu_target() {
    // Start with a target suitable for the machine you're running this on.
    Target target = get_host_target();

    std::vector<Target::Feature> features_to_try;
    if (target.os == Target::Windows) {
        // Try D3D12 first; if that fails, try OpenCL.
        if (sizeof(void*) == 8) {
            // D3D12Compute support is only available on 64-bit systems at present.
            features_to_try.push_back(Target::D3D12Compute);
        }
        features_to_try.push_back(Target::OpenCL);
    } else if (target.os == Target::OSX) {
        // OS X doesn't update its OpenCL drivers, so they tend to be broken.
        // CUDA would also be a fine choice on machines with NVidia GPUs.
        features_to_try.push_back(Target::Metal);
    } else {
        features_to_try.push_back(Target::OpenCL);
    }
    // Uncomment the following lines to also try CUDA:
    features_to_try.push_back(Target::CUDA);

    for (Target::Feature f : features_to_try) {
        Target new_target = target.with_feature(f);
        if (host_supports_target_device(new_target)) {
            return new_target;
        }
    }

    printf("Requested GPU(s) are not supported. (Do you have the proper hardware and/or driver installed?)\n");
    return target;
}


int main(int argc, char **argv) {



    std::string FILENAME = "halide_blur_3x3_gpu_quadro.csv"; // here
    std::ofstream ofile;
    ofile.open(FILENAME);

    int vec_array [5] = { 2, 4, 8, 16 };

    //std::cout << vec_array[0] << std::endl;

    Target target = find_gpu_target();
    if (!target.has_gpu_feature()) {
        return 1;
    }

    std::cout << "GPU target in fft.cpp: "  << target.to_string().c_str() << std::endl;


    for (int i = 0; i <= 5; i++) { // 5

        
        //int NUM = 1000;

        int p_input = 10 + i;

        for (int p1 = 0; p1 < 7; p1++){ // p_input
        for (int p2 = 0; p2 < 7; p2++){ // p_input

            for (int k = 0; k < 4; k++){ // 4
            
            Func blur_x, blur_y;
            Var x_, y_, xi, yi;

            Func input;
            
            input(x_,y_) = rand() % 256;
                
            //int p1 = rand() % p_input + 1; 
            //int p2 = rand() % p_input + 1; 
            //int p3 = rand() % p_input + 1; 


                int v1 = pow(2,p1);
                int v2 = pow(2,p2);
                int v3 = vec_array[k];
                

                //if (j % 10 == 0) std::cout << j << std::endl;
                std::cout << pow(2,p_input) << "," << v1 << "," << v2 << "," << v3 << std::endl;


                // The algorithm - no storage or order
                blur_x(x_, y_) = (input(x_-1, y_) + input(x_, y_) + input(x_+1, y_))/3;
                blur_y(x_, y_) = (blur_x(x_, y_-1) + blur_x(x_, y_) + blur_x(x_, y_+1))/3;

                // The schedule - defines order, locality; implies storage
                

                //blur_y.tile(x, y, xi, yi, tilew, tilel).vectorize(xi, vec).parallel(y);
                //blur_x.compute_at(blur_y, x).vectorize(x, vec);



                //int factor = sizeof(int) / sizeof(short);
                Var y_inner("y_inner");
                blur_y.vectorize(x_, v3)
                    .split(y_, y_, y_inner, v1)
                    .reorder(y_inner, x_)
                    .unroll(y_inner)
                    .gpu_tile(x_, y_, xi, yi, v2, 1);

                blur_y.compile_jit(target);


                double time = 0;
                int rounds = 3; // here

                for (int j = 0; j < rounds; j++){
                    
                    double t1 = current_time();
                    blur_y.realize(pow(2,p_input),pow(2,p_input)); // here
                    double t2 = current_time();
                    
                    
                    time += (t2 - t1)/1000;

                   
                }

                double avgtime = time/rounds; 

                std::cout << avgtime << std::endl;



                //if (j > 9)
                ofile << avgtime << "," << pow(2,p_input) << "," << v1 << "," << v2 << "," << v3 << "," << '\n';
            }
        }
        }
    }



    ofile.close();

    // Everything worked! We defined a Func, then called 'realize' on
    // it to generate and run machine code that produced an Buffer.
    printf("Success!\n");

    return 0;
}
