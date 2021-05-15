"""
A minimal implementation of Monte Carlo tree search (MCTS) in Python 3
Luke Harold Miles, July 2019, Public Domain Dedication
See also https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
"""
from abc import ABC, abstractmethod
from collections import defaultdict
import math
import numpy as np # ADDED
from random import choice, random # ADDED
from ILP_algorithms import LP_relax, rand_round


# node to string helper function
def nts(n):
    a = n['x']
    s = ''
    for pair in zip(*np.where(a == 1)): s += str(pair) + ' '
    return s


# Pick-Best-Pair with randomized rounding and running best
class MCTS_RR_RB:
    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = set() # children of each node
        self.mapping = dict() # TR-pair as tuple mapped to corresponding node

        # MODIFIED Jan 16 2021, keep track of best intermediate assignment
        self.running_best = (0, None)

        self.exploration_weight = exploration_weight
    
    def choose(self, node):
        "Choose the best TR-pair."
        if node.is_terminal(): raise RuntimeError(f"choose called on terminal node {node}")

        def score(n):
            if self.N[n] == 0: return float("inf") # avoid unseen TR-pairs
            return self.Q[n] / self.N[n] # average reward across all visits
        
        best = min(self.children, key=score) # find lowest completion time

        # reset dictionaries
        self.Q = defaultdict(int)
        self.N = defaultdict(int)
        self.children = set()

        return best
    
    def do_rollout(self, node, x_LP):
        """Run a randomized rounding on the LP-relax solution and add reward
        to TR-pairs that make up the randomized rounding"""
        self._expand(node) # make TR-pairs for this level
        x_rr, reward = self._simulate(node, x_LP) # get reward of randomized rounding

        # check if this rounding is best so far
        if self.running_best[1] is None or self.running_best[0] > reward:
            self.running_best = (reward, x_rr)

        self._backpropagate(x_rr, reward) # add reward to TR-pairs in x_rr
    
    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if self.children: return # already expanded
        self.children, self.mapping = node.find_children()

    def _simulate(self, node, x_LP):
        "Performs randomized rounding (x_rr) on LP_sol, returns x_rr and reward"
        x_rr = rand_round(x_LP)
        return x_rr, node.reward_of(x_rr)

    def _backpropagate(self, x_rr, reward):
        # go through every row in x_rr
        for i, row in enumerate(x_rr):
            # get node
            TR_pair = (i, np.where(row == 1)[0][0])
            if TR_pair not in self.mapping: continue # this is an already assigned pair
            node = self.mapping[TR_pair]

            # update node's num visits and reward
            self.N[node] += 1 #self.pagerank(x_rr, reward, i)
            self.Q[node] += reward

    # decides what factor for count to backpropagate to the ith task given x and the reward
    # basically, how much of this completion time is the fault of ith task assignment?
    # is it the other assignments that is dragging down the overall time?
    def pagerank(self, x, T, i):
        # calculate average reward of all other tasks
        allN, allQ = (0,0)
        for j, row in enumerate(x):
            if j == i: continue

            TR_pair = (j, np.where(row == 1)[0][0])
            if TR_pair not in self.mapping: continue
            node = self.mapping[TR_pair]

            allN += self.N[node]
            allQ += self.Q[node]
        
        if allN == 0: return 1
        avg_reward = allQ/allN

        # now decide the factor for ith task
        change = (avg_reward - T) / T
        return 1 + change


# Pick-Best-Pair, with randomized rounding for simulation
class MCTS_RR:
    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = set() # children of each node
        self.mapping = dict() # TR-pair as tuple mapped to corresponding node

        self.exploration_weight = exploration_weight
    
    def choose(self, node):
        "Choose the best TR-pair."
        if node.is_terminal(): raise RuntimeError(f"choose called on terminal node {node}")

        def score(n):
            if self.N[n] == 0: return float("inf") # avoid unseen TR-pairs
            return self.Q[n] / self.N[n] # average reward across all visits
        
        best = min(self.children, key=score) # find lowest completion time

        # reset dictionaries
        self.Q = defaultdict(int)
        self.N = defaultdict(int)
        self.children = set()

        return best
    
    def do_rollout(self, node, x_LP):
        """Run a randomized rounding on the LP-relax solution and add reward
        to TR-pairs that make up the randomized rounding"""
        self._expand(node) # make TR-pairs for this level
        x_rr, reward = self._simulate(node, x_LP) # get reward of randomized rounding
        self._backpropagate(x_rr, reward) # add reward to TR-pairs in x_rr            
    
    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if self.children: return # already expanded
        self.children, self.mapping = node.find_children()

    def _simulate(self, node, x_LP):
        "Performs randomized rounding (x_rr) on LP_sol, returns x_rr and reward"
        x_rr = rand_round(x_LP)
        return x_rr, node.reward_of(x_rr)

    def _backpropagate(self, x_rr, reward):
        # go through every row in x_rr
        for i, row in enumerate(x_rr):
            # get node
            TR_pair = (i, np.where(row == 1)[0][0])
            if TR_pair not in self.mapping: continue # this is an already assigned pair
            node = self.mapping[TR_pair]

            # update node's num visits and reward
            self.N[node] += 1
            self.Q[node] += reward




# Pick-Best-Pair version for MCTS
class MCTS_PBP:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, verbose, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight
        self.verbose = verbose # ADDED verbose for intermediate outputs

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            # print('hmm')
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0: return float("-inf")  # avoid unseen moves. CHANGED FROM -inf TO inf? NO
            return self.Q[n] / self.N[n]  # average reward

        # CHANGED FROM MAX TO MIN? NO
        best = max(self.children[node], key=score)
        return best

    def do_rollout(self, node, x_LP):
        """Make the tree one layer better. (Train for one iteration.)"""
        path = self._select(node, x_LP)
        leaf = path[-1]
        self._expand(leaf)
        reward = self._simulate(leaf, x_LP)
        self._backpropagate(path, reward)

    def _select(self, node, x_LP):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys() # get the children w/o children
            if unexplored:
                n = self._LP_select_unexplored(unexplored, x_LP) # unexplored.pop()
                path.append(n)
                return path
            
            node = self._LP_select(node, x_LP)  # descend a layer deeper based on LP solution

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children: return  # already has children
        self.children[node] = node.find_children()

    def _simulate(self, node, x_LP):
        """Returns the reward for a random simulation (to completion) of `node`"""
        "Complete rest of node with LP-relax and best rand-round, calculate completion time for reward"
        return node.complete_with_LP_reward(x_LP)

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"

        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward


    def _LP_select_unexplored(self, nodes, x_LP):
        "Select a node from set nodes based on the LP solution"
        # half of the time, get random node
        if random() < 0.5: return nodes.pop()

        # other half of the time, get a node based on how "good"
        # LP solution suggests it is
        def best_from_LP(node):
            TR_pairs = zip(*np.where(node['x'] == 1)) # get TR-pairs
            total = 0 # will contain the total of the fractions of TR-pairs from LP

            for i,j in TR_pairs: total += x_LP[i][j]
            return total

        return max(nodes, key=best_from_LP)
            



    def _LP_select(self, node, x_LP):
        "Select a child of node based on the LP solution"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        # get children of node. we will select one of these
        children_of_node = self.children[node]
        
        # 50% of the time, select a child using uct
        if random() < 0.5: return self._uct_select(node)
        
        # rest of the time, select child with highest fractions in LP
        def best_from_LP(node):
            TR_pairs = zip(*np.where(node['x'] == 1)) # get TR-pairs
            total = 0 # will contain the total of the fractions of TR-pairs from LP

            for i,j in TR_pairs: total += x_LP[i][j]
            return total

        return max(children_of_node, key=best_from_LP)


    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        # CHANGE FROM MAX TO MIN? NO
        return max(self.children[node], key=uct)



class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, verbose, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight
        self.verbose = verbose # ADDED verbose for intermediate outputs

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves. CHANGED FROM -inf TO inf? NO
            return self.Q[n] / self.N[n]  # average reward

        # CHANGED FROM MAX TO MIN? NO
        return max(self.children[node], key=score)

    def do_rollout(self, node, is_initial=False):
        """Make the tree one layer better.
           (Train for one iteration.)"""
        if is_initial: path = [node]
        else: path = self._select(node)
        leaf = path[-1]

        if self.verbose:
            print('starting atig')
            print(leaf.atig_dict['x'])

        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()

    # UPDATE _simulate() AND _backpropagate TO ELIMINATE INVERSE REWARDS, NOT PLAYING A GAME HERE
    # UPDATE to run LP-relax periodically
    def _simulate(self, node):
        """Returns the reward for a random simulation
           (to completion) of `node`"""
        LP_freq = node['n']//5

        while True:
            if node.is_terminal():
                return node.reward(self.verbose)

            # would run LP-relax about 5 times total from start to finish
            if random() < 1/LP_freq:
                node = node.find_LP_child()
            else:
                node = node.find_random_child()

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        # CHANGE FROM MAX TO MIN? NO
        return max(self.children[node], key=uct)


class Node(ABC):
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

    # @abstractmethod
    # def __hash__(self):
    #     "Nodes must be hashable"
    #     return 123456789
    #
    # @abstractmethod
    # def __eq__(node1, node2):
    #     "Nodes must be comparable"
    #     return True
