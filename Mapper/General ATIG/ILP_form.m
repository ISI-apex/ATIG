%% ILP solution

cvx_begin
    variables T(P+1) M(P);
    variable x(n,m) binary; % (6) binary decisions
    minimize(T(P+1));
    subject to
    
    % (1) completion time (Note that M(i) = M_{i-1})
    T(1) == 0; %#ok<*EQEFF>
    for p = 2 : P+1, %#ok<*NOCOL>
        T(p) == T(p-1) + M(p-1);
    end
    
    % (2) find the slowest process
    for p = 1 : P,
        for i = 1 : n
            for j = 1 : m,
                    Tt(i,j) * stagemat(p, i)* x(i,j) + stagemat(p, i) * Adj(:, i)' * x * Tc(:, j) <= M(p);
            end
        end
    end
    
    % (3) resource constraints
    for p = 1 : P,
            for j = 1 : m,
                    stagemat(p, :)*(x(:,j).*C(:, j)) <= B(j);
            end
    end
    
            
    % (5) assign tasks
    for i = 1 : n,
         sum( x(i,:)) == 1;
    end
    
%     % (6) sink resource
%     for k=1:n,
%         stagemat(P, i)*x(i, :, sinkresource) == stagemat(P, i);
%     end
cvx_end
