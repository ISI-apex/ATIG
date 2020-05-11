import numpy as np
import cvxpy as cp # use `pip install --pre --upgrade cvxpy` to get cvxpy-1.1 from cvxpy.atoms.affine.reshape import reshape
from cvxpy.atoms.affine.binary_operators import multiply


# -- ILP (exact) Solver -- #
def ILP_form(m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj):
    # -- Variables --
    T = cp.Variable(P+1) # task time
    M = cp.Variable(P) # models resources
    x = cp.Variable((n,m), boolean=True) # binary decisions

    # -- Objective --
    obj = cp.Minimize(T[P])


    # -- Constraints --
    constraints = []


    # (1) completion time (Note that M(i) = M_{i-1})
    constraints.append(T[0] == 0)
    for p in range(1,P+1):
        constraints.append(T[p] == T[p-1] + M[p-1])

    # (2) find the slowest process
    for p in range(P):
        for i in range(n):
            for j in range(m):
                constraints.append(Tt[i,j] * stagemat[p,i] * x[i,j] + \
                    stagemat[p,i] * (Adj[:,i].reshape(1,n) @ x @ Tc[:,j]) <= M[p])

    # (3) resource constraints
    for p in range(P):
        for j in range(m):
            constraints.append(stagemat[p] @ multiply(reshape(x[:,j], (n,1)), C[:,j].reshape(n,1)) <= B[j])


    # (5) assign tasks
    for i in range(n):
        constraints.append(sum(x[i]) == 1)


    # -- Solve --
    prob = cp.Problem(obj, constraints)
    val = prob.solve()

    print('T.value:', T.value)
    print('M.value:', M.value)
    print('x.value:\n', x.value)
    print('T:', val)

    return x.value


# -- Linear Relaxation -- #
def LP_relax(m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj, verbose=1):
    # -- Variables --
    T = cp.Variable(P+1) # task time
    M = cp.Variable(P) # models resources
    xl = cp.Variable((n,m), boolean=False) # binary decisions

    # -- Objective --
    obj = cp.Minimize(T[P])


    # -- Constraints --
    constraints = []


    # (1) completion time (Note that M(i) = M_{i-1})
    constraints.append(T[0] == 0)
    for p in range(1,P+1):
        constraints.append(T[p] == T[p-1] + M[p-1])

    # (2) find the slowest process
    for p in range(P):
        for i in range(n):
            for j in range(m):
                constraints.append(Tt[i,j] * stagemat[p,i] * xl[i,j] + \
                    stagemat[p,i] * (Adj[:,i].reshape(1,n) @ xl @ Tc[:,j]) <= M[p])

    # (3) resource constraints
    for p in range(P):
        for j in range(m):
            constraints.append(stagemat[p] @ multiply(reshape(xl[:,j], (n,1)), C[:,j].reshape(n,1)) <= B[j])

    # (5) assign tasks
    for i in range(n):
        constraints.append(sum(xl[i]) == 1)

    # (6) bounded between 0 and 1
    for i in range(n):
        for j in range(m):
            constraints.append(xl[i,j] >= 0)

    for i in range(n):
        for j in range(m):
            constraints.append(xl[i,j] <= 1)


    # -- Solve --
    prob = cp.Problem(obj, constraints)
    val = prob.solve()

    if verbose == 1:
        print('prob.solve:', val)
        print('T.value:', np.around(T.value, 3))
        print('M.value:', np.around(M.value, 3))
        print('xl.value:\n', np.around(xl.value, 3))

    return val, xl.value


# -- Randomized Rounding -- #
def rand_round(x):
    n, m = x.shape
    u = np.zeros((n,1))
    xi = np.zeros((n,m))

    for i in range(n):
        prob = x[i].clip(min=0) / sum(x[i].clip(min=0))
        u[i] = np.random.choice(range(0,m), 1, p=prob)
        xi[i, int(u[i][0])] = 1

    return xi


# -- Calculate ILP -- #
def ILP_calculate(m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj, x, verbose=0):
    # (5) assign tasks
    for i in range(n):
        if (sum(x[i]) != 1): return float("inf")

    # (3) resource contraints
    for p in range(P):
        for j in range(m):
            res = np.dot(stagemat[p], x[:,j].reshape((n,1)) * C[:,j].reshape(n,1))
            if (res > B[j]): return float("inf")


    # (2) completion time
    M = np.zeros(P)

    for p in range(P):
        for i in range(n):
            for j in range(m):
                slowest = Tt[i,j] * stagemat[p,i] * x[i,j] + \
                    (stagemat[p,i]) * (Adj[:,i].reshape(1,n)).dot(x).dot(Tc[:,j])

                if (slowest > M[p]): M[p] = slowest

    # (1) find slowest process
    T = np.zeros(P+1)
    T[0] = 0

    for p in range(1, P+1): T[p] = T[p-1] + M[p-1]

    # total time
    if verbose == 1: print('T =', T[-1], 'for:\n', x, end='\n\n')

    return T[-1]



# -- Calculate ILP with constraint counting. -- #
def ILP_calc_violations(m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj, x, verbose=0):
    num_violations = 0

    # (5) assign tasks
    for i in range(n):
        if (sum(x[i]) != 1): num_violations += 1 #return float("inf")

    # (3) resource contraints
    for p in range(P):
        for j in range(m):
            res = np.dot( stagemat[p], x[:,j].reshape((n,1)) * C[:,j].reshape(n,1) )
            if (res > B[j]): num_violations += 1 #return float("inf")


    # (2) completion time
    M = np.zeros(P)

    for p in range(P):
        for i in range(n):
            for j in range(m):
                slowest = Tt[i,j] * stagemat[p,i] * x[i,j] + \
                    (stagemat[p,i]) * (Adj[:,i].reshape(1,n)).dot(x).dot(Tc[:,j])

                if (slowest > M[p]): M[p] = slowest

    # (1) find slowest process
    T = np.zeros(P+1)
    T[0] = 0

    for p in range(1, P+1): T[p] = T[p-1] + M[p-1]

    # total time
    if verbose == 1: print('T =', T[-1], 'for:\n', x, end='\n\n')

    return  T[-1] * (1 + (2*num_violations))
