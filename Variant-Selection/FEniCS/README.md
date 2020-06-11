## Data Generation
Within the virtual machine,

use following commands to vary the parameters logistically:
1. 
```
for np in 1 2 4 8; do for th in 1 2 4; do sh -c "export OMP_NUM_THREADS=$th && mpirun -np $np python demo_cavity.py  2>&1 | tee meas/256x256/mumps/atlas-blas-st/mpi/np$np/th_2_$th.log"; done; done
```

2. for remaining pairwise combinations
```
for np in 32; do for th in 1; do sh -c "export OMP_NUM_THREADS=$th && mpirun --oversubscribe -np $np python demo_cavity.py  2>&1 | tee meas/256x256/mumps/atlas-blas-st/mpi/np$np/th_2_$th.log"; done; done
```

use following commands to vary the parameters linearly:
1. 
```
for np in {1..16..1}; do for th in {1..32..1}; do sh -c "export OMP_NUM_THREADS=$th && mpirun -np $np python demo_cavity.py $np $th 2>&1"; done; done
```

2. for remaining pairwise combinations
```
for np in 32; do for th in 1; do sh -c "export OMP_NUM_THREADS=$th && mpirun --oversubscribe -np $np python demo_cavity.py  2>&1 | tee meas/256x256/mumps/atlas-blas-st/mpi/np$np/th_2_$th.log"; done; done
```

3. put the generated `.csv` file in the corresponding `prediction_for_*` file. **Done**

**Since the virtual machine environment is not provided here, dataset generated on our server (*Intel(R) Xeon(R) CPU E5-2650 v2 @ 2.60GHz*) are included in `prediction_for_*` as `out.csv`.**


## Performance Prediction
0. In `out.csv`, the header is 

| Runtime     | Mesh size   | np         | th         | Augmented constant |
| ----------- | ----------- |----------- |----------- |-----------         |
| ...         | ...         |...         |...         |...                 |

1. run the performance prediction model with 
```
python pred_*.py
```

* `pred_NN.py` uses common neural networks.
* `pred_NN+C.py` uses augmented neural networks.

## Results Evaluation

1. In `results`, use `plot_for_*.ipynb` to plot the speedup. Contents in `.csv` have to be manually inspected and filled in now. 
