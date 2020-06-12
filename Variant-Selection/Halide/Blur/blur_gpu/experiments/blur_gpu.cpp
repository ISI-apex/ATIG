// On linux, you can compile and run it like so:
// g++ blur_gpu.cpp -g -std=c++11 -I ../include -I ../tools -L ../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o blur_gpu
// LD_LIBRARY_PATH=../bin ./blur_gpu

#include "Halide.h"
#include "clock.h"

using namespace Halide;

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
    // subject to change: the output file name
    std::string FILENAME = "halide_blur_gpu_Quadro_test.csv"; 
    std::ofstream ofile;
    ofile.open(FILENAME);

    int vec_array [5] = { 2, 4, 8, 16 };

    // verify GPU target 
    Target target = find_gpu_target();
    if (!target.has_gpu_feature()) {
        return 1;
    }
    std::cout << "GPU target: "  << target.to_string().c_str() << std::endl;

    // input dimension ranges from 2^10 to 2^15
    for (int i = 0; i <= 5; i++) { 
        int p_input = 10 + i;
        // varying parameters/knobs
        for (int p1 = 0; p1 < 7; p1++){ 
        for (int p2 = 0; p2 < 7; p2++){ 
        for (int k = 0; k < 4; k++){ 
            // Halide Blur operation
            Func blur_x, blur_y;
            Var x_, y_, xi, yi;

            Func input;
            
            input(x_,y_) = rand() % 256;
                
            int v1 = pow(2,p1);
            int v2 = pow(2,p2);
            int v3 = vec_array[k];
            
            // write to the console
            std::cout << pow(2,p_input) << "," << v1 << "," << v2 << "," << v3 << std::endl;

            // The algorithm - no storage or order
            blur_x(x_, y_) = (input(x_-1, y_) + input(x_, y_) + input(x_+1, y_))/3;
            blur_y(x_, y_) = (blur_x(x_, y_-1) + blur_x(x_, y_) + blur_x(x_, y_+1))/3;

            // The GPU specific schedule - defines order, locality; implies storage
            Var y_inner("y_inner");
            blur_y.vectorize(x_, v3)
                .split(y_, y_, y_inner, v1)
                .reorder(y_inner, x_)
                .unroll(y_inner)
                .gpu_tile(x_, y_, xi, yi, v2, 1);

            blur_y.compile_jit(target);

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
            ofile << avgtime << "," << pow(2,p_input) << "," << v1 << "," << v2 << "," << v3 << ",";
            ofile << cons << "," << '\n';
            }
        }
        }
    }

    ofile.close();

    printf("Success!\n");

    return 0;
}
