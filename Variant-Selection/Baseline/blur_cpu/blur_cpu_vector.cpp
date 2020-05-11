// Halide tutorial lesson 1: Getting started with Funcs, Vars, and Exprs

// This lesson demonstrates basic usage of Halide as a JIT compiler for imaging.


// On os x:
// g++ blur_cpu_vector.cpp -g -Wall -o blur_cpu_vector -std=c++11
// ./blur_cpu_vector

#include <ctime>
// We'll also include stdio for printf.
#include <stdio.h>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>
#include <stdlib.h>     /* malloc, free, rand */
#include <vector>




int main(int argc, char **argv) {


    std::string FILENAME = "naive_blur.csv"; // here
    std::ofstream ofile;
    ofile.open(FILENAME);

    for (int i = 0; i <= 0; i++) {

        int W, H;
        /*
        W = pow(2,i);
        H = pow(2,i);
        */

        W = 32768;
        H = 32768;
        


        
        //static char in[32768][32768];
        //static char blur[32768][32768];
        //char out[32768][32768];
        
        
        /*
        static char in[W][H];
        static char blur[W][H];
        static char out[W][H];
        */

        std::vector< std::vector<char> > in[W][H];
        std::vector< std::vector<char> > blur[W][H];
        std::vector< std::vector<char> > out[W][H];

        

        // initialize input
        for (int x = 0; x < W; x++){
            for (int y = 0; y < H; y++){
                in[x][H].pushback(rand() % 1024 + 1);
            }
        }

        /*
        double time = 0;
        int rounds = 5; // here

        for (int j = 0; j < rounds; j++){

            std::clock_t t1 = std::clock();

            // blur
            for (int x = 0; x < W; x++){
                for (int y = 0; y < H; y++){
                    blur[x][y] = (in[x-1][y] + in[x][y] + in[x+1][y])/3;
                }
            }

            for (int x = 0; x < W; x++){
                for (int y = 0; y < H; y++){
                    out[x][y] = (blur[x][y-1] + blur[x][y] + blur[x][y+1])/3;
                }
            }
            
            std::clock_t t2 = std::clock();

            time += ( t2 - t1 ) / (double) CLOCKS_PER_SEC; // unit: s


           
        }

        double avgtime = time/rounds; 

        std::cout << avgtime << std::endl;
        */




        // ofile << avgtime << "," << '\n';
    }


    ofile.close();

    // Everything worked! We defined a Func, then called 'realize' on
    // it to generate and run machine code that produced an Buffer.
    printf("Success!\n");

    return 0;
}