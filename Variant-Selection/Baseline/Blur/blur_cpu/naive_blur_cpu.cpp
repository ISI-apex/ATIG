// Compile it with:
// g++ naive_blur_cpu.cpp -g -Wall -o naive_blur_cpu -std=c++11
// Run it with:
// ./naive_blur_cpu

#include <ctime>
#include <stdio.h>
#include <cmath>
#include <random>
#include <iostream>
#include <fstream>
#include <stdlib.h>    

int main(int argc, char **argv) {

    std::string FILENAME = "naive_blur.csv"; 
    std::ofstream ofile;
    ofile.open(FILENAME);

    for (int i = 0; i <= 2; i++) {

        int W, H;
        
        // currently W = H
        W = pow(2,10+i);
        H = pow(2,10+i);
        
        static char in[W][H];
        static char blur[W][H];
        static char out[W][H];

        // test for large input size
        // char ** in = (char**)malloc(8192*8192*sizeof(char));
        // char ** blur =(char**)malloc(8192*8192*sizeof(char));
        // char ** out =(char**)malloc(8192*8192*sizeof(char));

        // initialize input
        for (int x = 0; x < W; x++){
            for (int y = 0; y < H; y++){
                in[x][y] = rand() % 1024 + 1;
            }
        }

        double time = 0;
        // for each input size, run 5 times and take the average
        int rounds = 5;

        for (int j = 0; j < rounds; j++){

            std::clock_t t1 = std::clock();

            // naive blur operation
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
            // calculate time
            time += ( t2 - t1 ) / (double) CLOCKS_PER_SEC; // unit: s
           
        }

        double avgtime = time/rounds; 
        std::cout << avgtime << std::endl;
    }

    ofile.close();
    printf("Success!\n");

    return 0;
}