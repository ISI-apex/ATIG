Within `fft_cpu`:

1. generate the dataset using `main.cpp` in `experiments`. Instuctions for compling and running are included in the top of `.cpp` files.
2. put the generated `.csv` file in `prediction`.
3. run the performance prediction model with 
```
python pred_*.py
```

* `pred_NN.py` uses common neural networks.
* `pred_NN+C.py` uses augmented neural networks.

4. In `results`, `plot.ipynb` can be used to plot the speedup. Contents in `.csv` have to be manually inspected now. 

Within `fft_gpu`:

1.  
```
cd /Halide-master/apps/fft
```

2. 
```
for w in 4 5 6 7; do sh -c "./bin/host/bench_fft $w $w"; done
```

3. put the generated `.csv` file in `prediction`.
3. run the performance prediction model with 
```
python pred_*.py
```

* `pred_NN.py` uses common neural networks.
* `pred_NN+C.py` uses augmented neural networks.

4. In `results`, `plot.ipynb` can be used to plot the speedup. Contents in .csv have to be manually inspected now. 
