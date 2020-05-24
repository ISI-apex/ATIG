# Overview
This repo contains code for the CASPER project. Specifically, included are python scripts that will generate an ATIG using Monte Carlo Tree Search and LP relaxation. Given a graph, with tasks assigned to stages, the MCTS algorithm will generate an assignment from each task to each resource that will result in close to minimal completion time of the graph.

# Contents
- `ATIG_generation.py`: contains functions used to generate a random or toy graph.
- `ILP_algorithms.py`: contains ILP form and LP relax algorithms, as well as some helper functions to determine constraint violations.
- `monte_carlo_tree_search.py`: MCTS script, modified from [this GitHub Gist](https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1).
- `mcts_atig.ipynb`: MAIN FILE. Jupyter notebook that defines the ATIG object and the primary function which uses the MCTS algorithm to generate the task graph. Test graphs

# Instructions
The linear programming algorithms require `cxvpy-1.1`. Install by running the command `pip install --pre --upgrade cvxpy`.

## `ILP_algorithms.py` constants and variables
Main constants
- `m`: resources
- `P`: stages
- `sinkresource`: set to `m`
- `n`: tasks

Time/resource constants
- `C`: running cost of task i on resource j (such as memory)
- `Ce`, `Cr` not used. Can be zero matrices of dimension n x m x m
- `Tt`: time it takes to run task i on resource j and send to resource k
- `Tc`: communication cost between resources

Graph description constants
- `B`: maximum capacity per resource
- `E`: set of edges
- `e`: number of edges
- `stagemat`: what stage each task is in
- `Adj`: adjacency matrix

`cvx` Variables
- `T`: task time
- `M`: slowest process per stage
- `x`: resulting task graph. a `1` in position `x_ij` indicates that task `i` is running on resource `j`

## Editing algorithm constraints
To edit constraints of, say, the ILP or LP relax algorithms, open `ILP_algorithms.py` and find the corresponding function. Each constraint is labeled, so they can be easily modified. In this file, one can also declare new solvers.

## Running the MCTS
Open the `mcts_atig.ipynb` notebook and go to the bottom, where there is a section called "Insert your own testing here." There a cell directly below laying out the steps necessary, but to further clarify:
1. Get ATIG constants. You can do this by declaring a new function in ATIG_generation.py that will generate and return all the constants needed to describe the ATIG graph.
2. Create ATIG object. Feed the constants you generated into the ATIG object constructor.
3. Perform `find_ATIG(new_atig)`, which returns x and T, the generated task graph and its processing/completion time, respectively.

In addition, examine the cells within the "`LP_relax` + MCTS" section as an example.


# Possible Improvements
- Is there a way to retroactively change a task assignment if the solver gets stuck at, say, 1-2 violations?
- Along those lines, how do we resolve the issue when we get an infinite solution? What if we try again several times and still get an infinite solution (which happened more than once)?
- Are there any baselines we could use to measure how good the current MCTS + LP relax algorithm is?
