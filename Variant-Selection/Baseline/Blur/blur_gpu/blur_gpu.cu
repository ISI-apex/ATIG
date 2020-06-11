// nvcc blur_gpu.cu -o blur_gpu
// CUDA_VISIBLE_DEVICES=1 ./blur_gpu


#include <iostream>
#include <cstdlib>
#include <math.h>
#include <stdio.h>
#include <assert.h>
#include <fstream>
#include <time.h>



__global__ void image_convolution_kernel(float *input, float *out, float *kernelConv,
                                         int img_width, const int img_height,
                                         const int kernel_width, const int kernel_height )
{

    int x = threadIdx.x + blockIdx.x * blockDim.x;
    int y = threadIdx.y + blockIdx.y * blockDim.y;
    
    if ((x < img_width) && (y < img_height)){  
        float sum = 0;
        for ( int j = 0; j < kernel_height; j++ )
        {
            for ( int i = 0; i < kernel_width; i++ )
            {
                int dX = x + i - kernel_width / 2;
                int dY = y + j - kernel_height / 2;

                if ( dX < 0 )
                    dX = 0;

                if ( dX >= img_width )
                    dX = img_width - 1;

                if ( dY < 0 )
                    dY = 0;

                if ( dY >= img_height )
                    dY = img_height - 1;


                const int idMat = j * kernel_width + i;
                const int idPixel = dY * img_width + dX;
                sum += (float)input[idPixel] * kernelConv[idMat];
            }
        }

        const int idOut = y * img_width + x;
        out[idOut] = abs(sum);
    }

}

__global__ void convolutionGPU(
float *d_Result,
float *d_Data,
int dataW,
int dataH )
{


// global mem address for this thread
const int gLoc = threadIdx.x +
blockIdx.x * blockDim.x +
threadIdx.y * dataW +
blockIdx.y * blockDim.y * dataW;

float sum = 0;
float value = 0;

int KERNEL_RADIUS = 3;


for (int i = -KERNEL_RADIUS; i <= KERNEL_RADIUS; i++) // row wise
for (int j = -KERNEL_RADIUS; j <= KERNEL_RADIUS; j++) // col wise
{
// check row first
if (blockIdx.x == 0 && (threadIdx.x + i) < 0) // left apron
value = 0;
else if ( blockIdx.x == (gridDim.x - 1) &&
(threadIdx.x + i) > blockDim.x-1 ) // right apron
value = 0;
else
{
// check col next
if (blockIdx.y == 0 && (threadIdx.y + j) < 0) // top apron
value = 0;
else if ( blockIdx.y == (gridDim.y - 1) &&
(threadIdx.y + j) > blockDim.y-1 ) // bottom apron
value = 0;
else // safe case
value = d_Data[gLoc + i + j * dataW];
}
sum += value * 0.5 * 0.5;
}
d_Result[gLoc] = sum;
}


void image_convolution(float * input,float* output, int img_height, int img_width, const int r, float & gpu_elapsed_time_ms)
{


    // initialize kernel here
    int kernel_height = r;
    int kernel_width = r;

    float *kernel;
    kernel = new float[r*r];

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);


    cudaEventRecord(start, 0);

    for (int i = 0; i < r*r; i++){
        kernel[i] = rand() % 10 + 1;
    }


    float * mask = new float[kernel_height*kernel_width];
    for (int i = 0; i < kernel_height*kernel_width; i++)
    {
        mask[i] = kernel[i];
    }



    float * d_input, * d_output, * d_kernel;
    cudaMalloc(&d_input, img_width*img_height*sizeof(float));
    cudaMalloc(&d_output, img_width*img_height*sizeof(float));
    cudaMalloc(&d_kernel, kernel_height*kernel_width*sizeof(float));

    cudaMemcpy(d_input, input, img_width*img_height*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kernel, mask, kernel_height*kernel_width*sizeof(float), cudaMemcpyHostToDevice);
    dim3 blocksize(16,16);
    dim3 gridsize;
    gridsize.x=(img_width+blocksize.x-1)/blocksize.x;
    gridsize.y=(img_height+blocksize.y-1)/blocksize.y;


    //image_convolution_kernel<<<gridsize,blocksize>>>(d_input,d_output,d_kernel,img_width,img_height,kernel_width,kernel_height);
    convolutionGPU<<<gridsize,blocksize>>>(d_output,d_input,img_width,img_height);
    
    cudaMemcpy(output, d_output, img_width*img_height*sizeof(float), cudaMemcpyDeviceToHost);


    cudaEventRecord(stop, 0);
    cudaEventSynchronize(stop);

    cudaEventElapsedTime(&gpu_elapsed_time_ms, start, stop);
}

int main(){
    


    // number of instances of data generated
    int NUM = 5;
    float total_time = 0;

    std::ofstream ofile;

    // change here to customize output filename
    ofile.open("naive_blur_gpu.csv");

    for (int iterator = 0; iterator < NUM; iterator++) {



        float *in, *out;
        int m = 16384;
        int n = 16384;
        int is = n * m;

        int r = 3;

        in = new float[is];
        out = new float[is];



        for (int i = 0; i < m * n; i++)
            in[i] = rand() % 1024 + 1;


        
        float time;

        // convolutionGPU(out,in,n,m);

        image_convolution(in, out, n, m, r, time);
        
        total_time += time;

        //int c = (m-r+1)*(n-r+1)*r*r;

        //ofile << time / 1000;
        //ofile << "," << m << "," << n << "," << r << "," << d << "," << c << ",\n";


    }

    std::cout << total_time / (NUM*1000) << std::endl;

    ofile.close();
    return 0;
}