%% Random Example

m = 6;                      % #resources
P = 5;                      % #tasks organized into P stages
sinkresource = m;
n = 20;                    % #tasks
C = rand(n, m);     % C_ij
Tt = rand(n, m);  % T_ij
Tc = rand(m, m);
B = 2*rand(m, 1);     % B_j
                   % edges
E = []; e=0; newidx=1;
%%%% Task Graph Generation %%%%
newfirst = 1;
dens = 0.7;
stagemat = zeros(P, n);
ptask = {};
for j=1:P
    xx = randi([1, ceil(1.5*(n-newfirst)/P)]);
    newlast = newfirst + xx;
    if j==P
        newlast = n;
    end
    newstage = [newfirst:newlast];
    newfirst = newlast+1;
    ptask{j} = newstage;
    stagemat(j, newstage) = 1;
    if j==1
        continue;
    end
    prevstage = ptask{j-1};
    
    for k1 = 1:length(prevstage)
        for k2 = 1:length(newstage)
            if rand(1)<dens
                E = [E [prevstage(k1); newstage(k2)]];
            end
        end
    end
end
e = size(E, 2);
Adj = full(sparse(E(1, :)', E(2, :)',  1, n, n));
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%