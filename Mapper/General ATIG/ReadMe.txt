We first generate the graph data (we call it ATIG) which generates the constants necessary for the ILP to run. This is done using one of the two:
toy_ATIG.m: Hand coded constants
random_ATIG.m: Randomly generate constants

Then we will run a solver. This is performed using one of the two:
ILP_form.m: Exact ILP solver
ILP_relax: Solves the LP without integer constraint, rand_round.m generates integer solutions from fractional LP solutions.