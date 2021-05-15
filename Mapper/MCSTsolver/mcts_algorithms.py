import numpy as np

from atig import ATIG
from mcts import MCTS, MCTS_PBP, MCTS_RR, MCTS_RR_RB, Node
from ILP_algorithms import LP_relax, ILP_calculate



# -- MAIN MCTS ALGORITHMS -- #
# Pick-Best-Pair with randomized rounding and running best
def find_ATIG_RR_RB(atig, num_rollouts=100):
    tree = MCTS_RR_RB()

    # each iteration assigns another TR-pair
    for i in range(atig['n']):
        # get LP-relax solution, which is will be rand-rounded for simulation
        # Note: prev_x is passed in as last argument
        T_LP, x_LP = LP_relax(*atig.get_entries(-1))

        # do rollouts
        for j in range(num_rollouts):
            tree.do_rollout(atig, x_LP)

        # after rollouts, assign a TR-pair
        atig = tree.choose(atig)
    

    # calculate greedy, in case it is better
    greedy_atig = ATIG(atig.get_entries(-2))
    greedy_T, greedy_x, greedy_res_times = find_ATIG_greedy(greedy_atig)

    # check algorithm output against running best and greedy
    best_completion_time = ILP_calculate(*atig.get_entries(-1)) # initialize with final result
    best_x = atig['x']

    if tree.running_best[0] < best_completion_time: # running best is better?
        best_completion_time, best_x = tree.running_best
    
    if greedy_T < best_completion_time: # greedy is better?
        best_completion_time, best_x = (greedy_T, greedy_x)

    return best_completion_time, best_x


# Pick-Best-Pair, with randomized rounding for simulation
def find_ATIG_RR(atig, num_rollouts=100):
    tree = MCTS_RR()

    # each iteration assigns another TR-pair
    for i in range(atig['n']):
        # get LP-relax solution, which is will be rand-rounded for simulation
        # Note: prev_x is passed in as last argument
        T_LP, x_LP = LP_relax(*atig.get_entries(-1))

        # do rollouts
        for j in range(num_rollouts):
            tree.do_rollout(atig, x_LP)

        # after rollouts, assign a TR-pair
        atig = tree.choose(atig)
    
    completion_time = ILP_calculate(*atig.get_entries(-1))
    return completion_time, atig['x']


# Pick-Best-Pair version of algorithm (choose best task-resource pair, no order)
def find_ATIG_PBP(atig, num_rollouts=50):
    tree = MCTS_PBP(verbose=0)

    # one outer loop for every level (task) in tree
    for i in range(atig['n']):
        # print('\n---- ON LEVEL', i, '----')
        # print('starting x:')
        # print(atig['x'])

        # Get LP_relax, which will partly determine what nodes to explore next
        T_LP, x_LP = LP_relax(*atig.get_entries(-1))
        # print('x_LP:')
        # print(x_LP)

        # one inner loop for each rollout
        for j in range(num_rollouts): tree.do_rollout(atig, x_LP)

        # after rollouts, update an xij = 1 (fix a task assignment)
        atig = tree.choose(atig)
    
    # once we have all our assignments, compute the completion time
    completion_time = ILP_calculate(*atig.get_entries(-1))
    return completion_time, atig['x']


# Main function (go task by task)
def find_ATIG(atig, num_rollouts=50, verbose=1):
    tree = MCTS(verbose=verbose)

    # one outer loop for every level (task) in tree
    for i in range(atig['n']):
        if verbose: print('---- ON LEVEL', i, '----')

        # First time, choose which resource to run on
        if verbose: print('-- rollout on initial atig --')
        initial = atig.get_initial(i)
        tree.do_rollout(atig, initial)

        # All other times, let program choose
        for j in range(1, num_rollouts):
            if verbose: print ('-- rollout', j, '--')
            tree.do_rollout(atig)

        # update an xij = 1 (fix a task assignment)
        atig = tree.choose(atig)
        
        # Output
        # clear_output(wait=True)
        # print('---- ASSIGNED TASK', i, '----')
        # print(atig['x'], end='\n--------\n\n')


    # finished
    # clear_output(wait=True)
    # print('atig terminal. final:')
    # print(np.array(atig['x']))
    
    completion_time = ILP_calculate(*atig.get_entries(-1))
    # print('T:', completion_time)

    return completion_time, atig['x']
    


# -- Greedy algorithm -- #
def find_ATIG_greedy(atig):
    # keep track of task assignments
    x = []

    # keep track of aggregate execution times of each resource
    resource_times = np.zeros(atig['m'])

    # assign each task to a resource greedily.
    for i in range(atig['n']):
        # holds what resource_times would be if we ran the current task on said resource
        resource_times_new = np.zeros(atig['m'])

        # try each resource
        for j in range(atig['m']):
            # added time = task execution time of current task(Tt) +
            # communication/transfer time required for dependencies (Tc)
            # 1. task execution time
            added_time = atig['Tt'][i,j]

            # 2. communication time for running on this resource
            incoming_edges = atig['Adj'][:,i] # get incoming edges for current task
            for k, prev_task in enumerate(incoming_edges):
                if not prev_task: continue # this task is not an incoming edge

                # otherwise, get resource that the incoming task is from
                from_resource = x[k].index(1)
                added_time += atig['Tc'][from_resource,j] # j = curr resource

            # 3. add to aggregate resource tracking
            resource_times_new[j] = resource_times[j] + added_time
        
        # now pick the incrementally best resource
        min_index, min_val = np.argmin(resource_times_new), np.amin(resource_times_new)
        resource_times[min_index] = min_val

        # make a row for it in the task map
        new_row = [0,]*atig['m']
        new_row[min_index] = 1
        x.append(new_row)

    x = np.array(x)
    return ILP_calculate(*atig.get_entries(-2), x), x, resource_times

