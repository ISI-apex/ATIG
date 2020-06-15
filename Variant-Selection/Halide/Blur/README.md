Within each file:

1. generate the dataset using the code in `experiments`. Instuctions for compling and running are included in the top of `.cpp` files.

2. run
```
python parse.py
```
to parse the data into `out.csv`.

3. put the generated `.csv` file in `prediction`.

4. run the performance prediction model with 
```
python pred_*.py
```

* `pred_NN.py` uses common neural networks.
* `pred_NN+C.py` uses augmented neural networks.

5. In `results`, `plot.ipynb` can be used to plot the speedup. Contents in `.csv` have to be manually inspected now. 