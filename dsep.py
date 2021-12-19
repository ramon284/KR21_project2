from BNReasoner import BNReasoner
from BayesNet import BayesNet
from typing import Union 
from collections import deque
from networkx.utils import UnionFind
import pruner

filePath = 'testing/dog_problem.BIFXML' ## filepath


def dSeperator(network : BayesNet, x: set,z: set,y: set):
    # union = x.union(y).union(z)
    # l_nodes = deque() ## we begin by pruning
    # nodes = network.get_all_variables()
    # for node in nodes:
    #     if len(network.get_children(node)) == 0:
    #         l_nodes.append(node)
            
    # while len(l_nodes) != 0:
    #     l = l_nodes.popleft()
    #     if l not in union:
    #         for parent in network.get_parents(l):
    #             if len(network.get_children(parent)) == 1:
    #                 l_nodes.append(parent)
    #         network.del_var(l)
    
    pruner.prune(network, z, x.union(y)) ## idk if this works identically.
                                          ## because it prunes less, basically.
    bnet.draw_structure()
    
    ## now for the pruning
    network.del_all_edges_from(network.get_outer_edges(z))
    union_diagram = network.find_unions()
    
    for w_node in network.weakly_con_comp():        
        union_diagram.union(*w_node) 
    union_diagram.union(*x)
    union_diagram.union(*y)

    if (x and y and union_diagram[next(iter(x))] == union_diagram[next(iter(y))]):
        print("False")
        return False
    else:
        print('True')
        return True 


bnet = BayesNet() ## make empty network
bnet.load_from_bifxml(file_path=filePath) ## fill that bitch up with data
x, z, y = {"light-on"}, {"dog-out"}, {"bowel-problem"}
bnet.draw_structure() ## draw the graph
dSeperator(bnet, x,z,y)
bnet.get_interaction_graph() ## get interaction graph (idk what this does tbh)
bnet.draw_structure() ## draw the graph
