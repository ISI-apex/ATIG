1.  
```
cd /Halide-master/apps/fft
```

2. 
```
for w in 4 5 6 7; do sh -c "./bin/host/bench_fft $w $w"; done
```

3. run
```
python parse.py
```
to parse the data into `out.csv`.

4. put the generated `.csv` file in `prediction`.

5. run the performance prediction model with 
```
python pred_*.py
```

* `pred_NN.py` uses common neural networks.
* `pred_NN+C.py` uses augmented neural networks.

6. In `results`, `plot.ipynb` can be used to plot the speedup. Contents in .csv have to be manually inspected now. 
