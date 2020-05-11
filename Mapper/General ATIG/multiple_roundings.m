maxs = 10;
Total_time = zeros(maxs, 1);
rc = zeros(maxs, 1);
[n, m] = size(xl);
allxi = zeros(maxs, n, m);
for s = 1:10
    xi = rand_round(xl);
    [tt, rr] =  evaluate_xi(xi, m, n, P, stagemat, C, B, Tt, Tc, Adj);
    Total_time(s) = tt;
    rc(s) = rr; 
    allxi(s, :, :) = xi;
end

[bestT, idx] = min(Total_time)
finxi = squeeze(allxi(idx, :, :));