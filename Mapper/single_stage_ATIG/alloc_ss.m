function [minLPt, minBt, minGt, minPt] = alloc_ss(m, n, pct, rct, prof_dat, base_dat, prt_list)

if nargin<7
    prt_list = ones(size(prof_dat, 1), size(prof_dat, 2));
end

if ndims(prt_list) == 1
    prt_list = prt_list(:)';
    prt_list = repmat(prt_list, [size(prof_dat, 2)]);
end

% Prepare LP

T_ij = zeros(n, m);         % best_runtime
B_ij = zeros(n, m);

switchtask = floor(pct*n);
switchres = floor(rct*m);
k1 = 1;
for ii=1:n
    while ii>switchtask(k1)
        k1 = k1+1;
    end
    k2 = 1;
    for jj=1:m
        while jj>switchres(k2)
            k2 = k2+1;
        end
        T_ij(ii, jj) = prof_dat(k1, k2);
        B_ij(ii, jj) = base_dat(k1, k2);
        prt_vec(ii, jj) = prt_list(k1, k2);
    end
end

%ILP solution

cvx_begin quiet
    variable M;
    variable x(n,m);
    minimize(M);
    subject to
    
    % completion time
    for j = 1: m,
        M >= sum( T_ij(:,j) .* x(:,j) );
    end
            
    % assign tasks
%     for i = 1 : n,
%         sum( x(i,:) ) == 1;
%     end
    sum(x, 2) == 1;
    
    x >= 0;
    x <= 1;
cvx_end

% LP rounding
nsim = 100;
LPt = zeros(nsim, 1);
for sim = 1:nsim
    u = int32(zeros(m, 1));
    xi = zeros(n, m);

    for i=1:n
        x(i, :) = x(i, :).*(x(i, :)>0);
        u(i) = datasample([1:m], 1, 'Weight', x(i, :));
        xi(i, u(i)) = 1;
    end
    SUM = sum(T_ij .* xi, 1);
    LPt(sim) = max(SUM);
end
CPT = zeros(m, 1);
xg_ij = zeros(n,m);
for i=1:n
    opts = CPT'+T_ij(i, :);
    [~, idx] = min(opts);
    xg_ij(i, idx) = 1;
    CPT(idx) = CPT(idx)+T_ij(i, idx);
end
SUM = sum(T_ij .* xg_ij, 1);
LPt(sim) = max(SUM);
minLPt = min(LPt);

%minLPt = 1;

% Baseline uniform random
nsim = 100;
Bt = zeros(nsim, 1);
for sim = 1:nsim
    r = randi(m,n,1);
    xb_ij = zeros(n,m);
    for i=1:n
        xb_ij(i, r(i)) = 1;
    end
    SUM = sum(B_ij .* xb_ij, 1);
    Bt(sim) = max(SUM);
end

minBt =  mean(Bt);

% Baseline Priority based
xp_ij = zeros(n,m);
xx = prt_list(:);
prt_adder = max(xx(xx< Inf));
for i=1:n
    [~, idx] = min(prt_vec(i, :));
    xp_ij(i, idx) = 1;
    prt_vec(:, idx) = prt_vec(:, idx) + prt_adder;
end
SUM = sum(B_ij .* xp_ij, 1);
minPt = max(SUM);

% Baseline greedy
CPT = zeros(m, 1);
xg_ij = zeros(n,m);
for i=1:n
    opts = CPT'+B_ij(i, :);
    [~, idx] = min(opts);
    xg_ij(i, idx) = 1;
    CPT(idx) = CPT(idx)+B_ij(i, idx);
end
SUM = sum(B_ij .* xg_ij, 1);
minGt = max(SUM);

end