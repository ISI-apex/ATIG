# command for Halide FFT
# now w = h
for w in 1 2 3 4 5 6; do sh -c "./bin/host/bench_fft $w $w"; done

for w in 3; do sh -c "./bin/host/bench_fft $w $w"; done