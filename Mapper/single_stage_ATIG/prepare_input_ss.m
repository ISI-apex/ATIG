%% Input for Blur
m = 50;
n = 100;

T_ij = zeros(n, m);         % best_runtime
B_ij = zeros(n, m);


best_CPU = [0.0169542, 0.0183616, 0.032741, 0.154846, 0.55953, 2.27961];
best_GPU = [0.002309, 0.107198, 0.136053, 0.262614, 0.77503, 2.90731];

baseline_CPU = [0.0116752, 0.0413536, 0.167417, 0.664858, 2.62894, 13.4657];
baseline_GPU = [0.00545369, 0.0195138, 0.0784861, 0.309586, 1.29343, 7];

prof_dat = [best_CPU' best_GPU'];
base_dat = [baseline_CPU' baseline_GPU'];

%pct = [0.030, 0.060, 0.070, 0.080, 0.090, 1]; % input distribution
pct = [0 0 0 0 0 1]; % input distribution
all_rct = [0 1; 0.3 1; 0.5 1; 0.7 1; 1 1]; % device distribution
prt_list = [2 1] ;
%% Input for Halide FFT
m = 20;
n = 100;

T_ij = zeros(n, m);         % best_runtime
B_ij = zeros(n, m);

prof_dat = [0.148	0.011; 1.24	0.449; 7.748	2.639; 59.188	23.397; 398.709	112.171];

base_dat = [0.438	0.358; 2.436	1.438; 12.751	7.187; 63.753	35.45; 398.709	189.376];


%pct = [0.030, 0.060, 0.070, 0.080, 0.090, 1]; % input distribution
pct = [0.2 0.4 0.6 0.8 1]; % input distribution
all_rct = [0 1; 0.3 1; 0.5 1; 0.7 1; 1 1]; % device distribution
%% Input Halide FFT all


m = 40;
n = 100;

T_ij = zeros(n, m);         % best_runtime
B_ij = zeros(n, m);

prof_dat = [1.24	0.449	0.069	0.042	0.017	0.035; 59.188	23.397	0.134	0.099	0.067	0.056];

base_dat = [2.436	1.438	0.069	0.042	0.017	0.035; 63.753	35.45	0.369	0.171	0.161	0.344];



%pct = [0.030, 0.060, 0.070, 0.080, 0.090, 1]; % input distribution
pct = [0 1]; % input distribution
all_rct = [1/6 2/6 3/6 4/6 5/6 1; ...
    0.5 0.6 0.7 0.8 0.9 1; ...
    0.1 0.6 0.7 0.8 0.9 1.0; ...
    0.1 0.2 0.7 0.8 0.9 1.0; ...
    0.1 0.2 0.3 0.8 0.9 1.0; ...
    0.1 0.2 0.3 0.4 0.9 1.0; ...
    0.1 0.2 0.3 0.4 0.5 1.0]; % device distribution

prt_list = [2 2 1 1 1 1];
%% Input for blur all

m = 30;
n = 100;

prof_dat = [0.0169542	0.037809	0.002309	0.00255367; ...
0.0183616	0.0375837	0.107198	0.0382193; ...
0.032741	0.0473833	0.136053	0.0776557; ...
0.154846	0.072304	0.262614	0.190017; ...
0.55953	0.189835	0.77503	0.755045; ...
2.27961	0.617344	2.90731	3.20193];

base_dat = [0.0116752	0.0118374	0.00545369	0.0522981; ...
0.0413536	0.0464954	0.0195138	0.211979; ...
0.167417	0.186842	0.0784861	0.825738; ...
0.664858	inf	0.309586	3.31661; ...
2.62894	inf	1.29343	inf; ...
13.4657	inf	inf	inf];

prof_dat = min(prof_dat, base_dat);

all_rct = [1/4 2/4 3/4 1; 3/6 4/6 5/6 6/6; 1/6 4/6 5/6 6/6; 1/6 2/6 5/6 6/6; 1/6 2/6 3/6 6/6];
pct = [0 0 0.0 0.0 0.5 1];
prt_list = repmat([2 2 1 1 ], [length(pct), 1]);
prt_list(base_dat > 10000) = Inf;

%% Run script with mixtures

%all_rct = [1/6 2/6 3/6 6/6];

res_mat = zeros(size(all_rct, 1), 4);

for rr = 1:size(all_rct, 1)
    rct = all_rct(rr, :);
    [res_mat(rr, 1), res_mat(rr, 2), res_mat(rr, 3), res_mat(rr, 4)] = alloc_ss(m, n, pct, rct, prof_dat, base_dat, prt_list); 
    xx = res_mat(rr, :)
end
disp('DONE!');
save ss.mat;
