function [T, rc] = evaluate_xi(x, m, n, P, stagemat, C, B, Tt, Tc, Adj)
% Outputs
% T: objective after rounding, rc: resource constraint violations, td:
% dependency constraint violations

    M = zeros(P, 1);
    for p = 1 : P
        for i = 1 : n
            for j = 1 : m
                    t = Tt(i,j) * stagemat(p, i)* x(i,j) + stagemat(p, i) * Adj(:, i)' * x * Tc(:, j);
                    if (t > M(p))
                        M(p) = t;
                    end
            end
        end
    end
    T = sum(M);
    
    % (3) resource constraints
    rc = 0;
    for p = 1 : P
            for j = 1 : m
                    if (stagemat(p, :)*(x(:,j).*C(:, j))- B(j))> 0.000001
                        rc  = rc + 1;
                    end
             end
    end
         