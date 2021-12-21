from BayesNet import BayesNet
#from typing import Union 
#from collections import deque
#from networkx.utils import UnionFind
import pruner
import copy


def check_dseperated(network : BayesNet, x: set,z: set,y: set) -> bool:
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
    
    network = copy.deepcopy(network)
    network = pruner.prune(network, z, x.union(y)) ## idk if this works identically.
                                          ## because it prunes less, basically.
    #network.draw_structure()
    
    ## now for the pruning
    network.del_all_edges_from(network.get_outer_edges(z))
    union_diagram = network.find_unions()
    
    for w_node in network.weakly_con_comp():        
        union_diagram.union(*w_node) 
    union_diagram.union(*x)
    union_diagram.union(*y)

    if (x and y and union_diagram[next(iter(x))] == union_diagram[next(iter(y))]):
        print("False, not d-seperated by : ", z)
        return False
    else:
        print('True, d-seperated by : ', z)
        return True 


#bnet = BayesNet() ## make empty network
#bnet.load_from_bifxml(file_path=filePath) ## fill that bitch up with data
#x, z, y = {"light-on"}, {"family-out"}, {"dog-out"}
#bnet.draw_structure() ## draw the graph
#check_dseperated(bnet, x,z,y)
#bnet.get_interaction_graph() ## get interaction graph (idk what this does tbh)
#bnet.draw_structure() ## draw the graph
