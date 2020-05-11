%% Toy Example
m = 2;                      % #resources
P = 2;                      % #tasks organized into P stages
sinkresource = m;
n = 3;                    % #tasks

C = ones(n, m);     % C_ij
Ce = zeros(n, m, m); % C^e_ijk
Cr = zeros(n, m, m); % C^r_ikj
Tt = zeros(n, m);  % T_ijk

Tt(1, :) = 2;
Tt(2, :) = 3;
Tt(3, :) = 5;

Tc = [0 6; 2 0];

B = ones(m, 1);     % B_j
E = [1 2; 3 3];  % The set of edges
e = 2;                      % edges
stagemat = zeros(P, n);
stagemat(1, [1 2]) = 1; stagemat(2, [3]) = 1;
Adj = full(sparse(E(1, :)', E(2, :)',  1, n, n));
