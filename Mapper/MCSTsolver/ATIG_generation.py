import numpy as np
import random
import math

# -- Second toy example -- #
def toy_ATIG2():
    m = 3
    P = 1
    sinkresource = m
    n = 5

    # memory/space cost
    C = np.zeros((n,m))
    C[0] = 1
    C[1] = 1
    C[2] = 2
    C[3] = 2
    C[4] = 3

    Ce = np.zeros((n, m, m)) # C^e_ijk
    Cr = np.zeros((n, m, m)) # C^r_ikj

    # dim. n x m
    Tt = np.array([ [100,3,10],
                    [1,10,105],
                    [100,100,10],
                    [100,10,100],
                    [10,2,101]])
    Tc = np.zeros((m,m)) # communication cost between resources

    # capacity per resource
    B = np.array([[3],[3],[3]])

    # All in first stage, no edges
    E = np.array([])
    e = 0
    stagemat = np.ones((P, n))
    Adj = np.zeros((5,5))


    return m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj





# -- Toy example, graph generation -- #
def toy_ATIG():
    m = 2
    P = 2
    sinkresource = m
    n = 3

    C = np.ones((n, m)) # C_ij
    Ce = np.zeros((n, m, m)) # C^e_ijk
    Cr = np.zeros((n, m, m)) # C^r_ikj
    Tt = np.zeros((n, m)) # T_ijk

    Tt[0] = 2
    Tt[1] = 3
    Tt[2] = 5

    Tc = np.array([[0,6],[2,0]])

    B = np.ones((m, 1)) # B_j
    E = np.array([[0,1], [2,2]]) # set of edges
    e = 2 # edges

    stagemat = np.zeros((P, n))
    stagemat[0, 0:2] = 1
    stagemat[1, 2] = 1

    Adj = np.zeros((3,3))
    Adj[tuple(E)] = 1

    return m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj


# -- Random graph generation. m, P, n are customizable -- #
def random_ATIG(m=6, P=5, n=20):
    m = m
    P = P
    sinkresource = m # UNUSED
    n = n

    C = np.random.rand(n, m)
    Ce = np.zeros((n, m, m)) # UNUSED
    Cr = np.zeros((n, m, m)) # UNUSED

    Tt = np.random.rand(n, m)
    Tc = np.random.rand(m, m)

    B = 2*np.random.rand(m, 1)
    E = []
    e = 0

    # Task graph generation. Filling in E and stagemat
    newfirst = 0
    dens = 0.7
    stagemat = np.zeros((P, n))
    ptask = []

    for j in range(P):
        xx = random.randint(1, math.ceil(1.5*(n-newfirst)/P))
        newlast = newfirst + xx;

        if j == P-1:
            newlast = n-1

        newstage = np.arange(newfirst, newlast+1)
        newfirst = newlast+1;
        ptask.append(newstage)

        stagemat[j, newstage] = 1

        if j == 0:
            continue

        prevstage = ptask[j-1]
        for k1 in range(len(prevstage)):
            for k2 in range(len(newstage)):
                if random.uniform(0,1) < dens:
                    E.append([prevstage[k1], newstage[k2]])


    e = len(E)
    E = np.array(E).T
    Adj = np.zeros((n,n))
    Adj[tuple(E)] = 1

    return m, P, sinkresource, n, C, Ce, Cr, Tt, Tc, B, E, e, stagemat, Adj
