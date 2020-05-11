function [xi] = rand_round(x)

temp = size(x);
m = temp(2);
n = temp(1);

u = int32(zeros(n, 1));

xi = zeros(temp);

for i=1:n
    x(i, :) = x(i, :).*(x(i, :)>0);
    u(i) = datasample([1:m], 1, 'Weight', x(i, :));
    xi(i, u(i)) = 1;
end